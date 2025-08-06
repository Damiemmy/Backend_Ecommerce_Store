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
