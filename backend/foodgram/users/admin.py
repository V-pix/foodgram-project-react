from django.contrib import admin

from users.models import CustomUser, Subscribtion


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "email", "first_name", "last_name", "password"
    )
    list_display_links = ("id", "username")
    list_filter = ("username", "email")
    search_fields = (
        "username",
        "email",
    )
    empty_value_display = "-пусто-"


class SubscribtionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    list_filter = ("user", "author")
    search_fields = ("user", "author")
    empty_value_display = "-пусто-"


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscribtion, SubscribtionAdmin)
