from django.contrib import admin

from users.models import CustomUser


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "email", "first_name", "last_name", "password"
    )
    list_display_links = ("id", "username")
    search_fields = (
        "username",
        "email",
    )


admin.site.register(CustomUser, UserAdmin)
