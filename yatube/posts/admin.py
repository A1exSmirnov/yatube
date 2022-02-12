from django.contrib import admin
from .models import Post, Group, Comment, Follow, User


class CommentInline(admin.TabularInline):
    model = Comment


class FollowerInline(admin.TabularInline):
    model = Follow
    fk_name = 'author'
    verbose_name_plural = 'Кто подписан на пользователя'


class FollowingInline(admin.TabularInline):
    model = Follow
    fk_name = 'user'
    verbose_name_plural = 'На кого подписан пользователь'


class UserAdmin(admin.ModelAdmin):
    inlines = [
        FollowerInline,
        FollowingInline,
    ]


class PostAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )

    list_editable = (
        'group',
    )
    search_fields = (
        'text',
    )
    list_filter = (
        'pub_date',
    )
    empty_value_display = '-пусто-'
    inlines = [
        CommentInline,
    ]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)
