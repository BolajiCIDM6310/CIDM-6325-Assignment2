from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from taggit.models import Tag

from .forms import (
    CommentForm,
    EmailPostForm,
    RecipeRatingForm,
    EmailRecipeForm,
    CommentRecForm,
)
from .models import Post, Recipe, RecipeRating, BookmarkPost, BookmarkRecipe


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    # bookmarking status
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = BookmarkPost.objects.filter(
            user=request.user, post=post
        ).exists()

    # return render(request, 'post_detail.html', {'post': post, 'is_bookmarked': is_bookmarked})

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
            "is_bookmarked": is_bookmarked,
        },
    )

    # class PostListView(ListView):
    """
    Alternative post list view
    """

    # queryset = Post.published.all()
    # context_object_name = "posts"
    # paginate_by = 3
    # template_name = "blog/post/list.html"


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) " f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True

    else:
        form = EmailPostForm()
    return render(
        request,
        "blog/post/share.html",
        {"post": post, "form": form, "sent": sent},
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


# Helper function to get post by date and slug
def get_post_by_date_and_slug(year, month, day, slug):
    return get_object_or_404(
        Post, publish__year=year, publish__month=month, publish__day=day, slug=slug
    )


@login_required
def add_bookmark(request, year, month, day, post):
    post = get_post_by_date_and_slug(year, month, day, post)
    BookmarkPost.objects.get_or_create(user=request.user, post=post)
    return redirect(post.get_absolute_url())


@login_required
def remove_bookmark(request, year, month, day, post):
    post = get_post_by_date_and_slug(year, month, day, post)
    BookmarkPost.objects.filter(user=request.user, post=post).delete()
    return redirect(post.get_absolute_url())


@login_required
def view_bookmarks(request):
    bookmarks = BookmarkPost.objects.filter(user=request.user).select_related("post")
    return render(request, "blog/post/bookmarks.html", {"bookmarks": bookmarks})


def recipe_list(request, tag_slug=None):
    recipe_list = Recipe.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        recipe_list = recipe_list.filter(tags__in=[tag])

    # Pagination with 3 recipes per page
    paginator = Paginator(recipe_list, 3)  # Changed from post_list to recipe_list
    page_number = request.GET.get("page", 1)
    try:
        recipes = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        recipes = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        recipes = paginator.page(paginator.num_pages)

    # return render(request, 'recipes/recipe_list.html', {'recipes': recipes, 'tag': tag})
    # print(tag)
    return render(request, "recipes/list.html", {"recipes": recipes, "tag": tag})


def recipe_detail(request, year, month, day, slug):
    recipe = get_object_or_404(
        Recipe,
        status=Recipe.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    ratings = recipe.ratings.all()
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()

    rating_form = RecipeRatingForm()

    # List of active comments for this post
    comments = recipe.responses.filter(active=True)
    # Form for users to comment
    form = CommentRecForm()

    # List of similar posts
    recipe_tags_ids = recipe.tags.values_list("id", flat=True)
    similar_recipes = Recipe.published.filter(tags__in=recipe_tags_ids).exclude(
        id=recipe.id
    )
    similar_recipes = similar_recipes.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    # bookmarking status
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = BookmarkRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).exists()
    # return render(request, 'post_detail.html', {'post': post, 'is_bookmarked': is_bookmarked})

    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "recipe": recipe,
            "comments": comments,
            "form": form,
            "ratings": ratings,
            "user_rating": user_rating,
            "rating_form": rating_form,
            "is_bookmarked": is_bookmarked,
            "similar_recipes": similar_recipes,
        },
    )


def recipe_share(request, recipe_id):

    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        # Form was submitted
        form = EmailRecipeForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(recipe.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) " f"recommends you read {recipe.title}"
            )
            message = (
                f"Read {recipe.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['responses']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True

    else:
        form = EmailRecipeForm()
    return render(
        request,
        "recipes/share.html",
        {"recipe": recipe, "form": form, "sent": sent},
    )


@require_http_methods(["GET", "POST"])
def recipe_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentRecForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.recipe = recipe
        # Save the comment to the database
        comment.save()
    return render(
        request,
        "recipes/comment.html",
        {"recipe": recipe, "form": form, "comment": comment},
    )


# Helper function to get recipe by date and slug
def get_recipe_by_date_and_slug(year, month, day, slug):
    return get_object_or_404(
        Recipe, publish__year=year, publish__month=month, publish__day=day, slug=slug
    )


@login_required
def add_bookmark_rec(request, year, month, day, recipe):
    recipe = get_recipe_by_date_and_slug(year, month, day, recipe)
    BookmarkRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect(recipe.get_absolute_url())


@login_required
def remove_bookmark_rec(request, year, month, day, recipe):
    recipe = get_recipe_by_date_and_slug(year, month, day, recipe)
    BookmarkRecipe.objects.filter(user=request.user, recipe=recipe).delete()
    return redirect(recipe.get_absolute_url())


@login_required
def view_bookmarks_rec(request):
    bookmarks = BookmarkRecipe.objects.filter(user=request.user).select_related(
        "recipe"
    )
    return render(request, "recipes/bookmarks.html", {"bookmarks": bookmarks})


# user registreation
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})
