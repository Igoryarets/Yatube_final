from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):

    empty_value_display = "-пусто-"
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "text", "pub_date", "author", "group")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "author")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
