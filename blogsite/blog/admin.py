from django.contrib import admin

from .models import Comment, Post, Recipe, RecipeRating, CommentRes


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "author", "publish", "display_photo", "status"]
    list_filter = ["status", "created", "publish", "author"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "publish"]
    show_facets = admin.ShowFacets.ALWAYS

    def display_photo(self, obj):
        if obj.photo:
            return '<img src="{}" width="50" height="50" />'.format(obj.photo.url)
        return "No Image"

    display_photo.allow_tags = True
    display_photo.short_description = "Photo"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "post", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email", "body"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "author", "publish", "display_photo", "status"]
    list_filter = ["status", "created", "publish", "author"]
    search_fields = ["title", "ingredients", "steps"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "publish"]

    def display_photo(self, obj):
        if obj.photo:
            return '<img src="{}" width="50" height="50" />'.format(obj.photo.url)
        return "No Image"

    display_photo.allow_tags = True
    display_photo.short_description = "Photo"


@admin.register(CommentRes)
class CommentResAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "recipe", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email", "body"]


@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ["recipe", "user", "rating", "created"]
