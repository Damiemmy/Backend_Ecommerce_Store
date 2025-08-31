"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_fieldsets=(
        (None,{
            "classes":('wide',),
            "fields":("username","password1","password2","email","first_name","last_name","state","city","address","phone","is_staff","is_active")

        }),
    )
admin.site.register(CustomUser,CustomUserAdmin)
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Add your custom fields to the default fieldsets (used when editing users)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("state", "city", "address", "phone")}),
    )

    # Add your custom fields to add_fieldsets (used when creating users in admin)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("state", "city", "address", "phone")}),
    )

    # Display your custom fields in the list view
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "city",
        "state",
        "phone",
    )


# Register the custom user model with custom admin
admin.site.register(CustomUser, CustomUserAdmin)
