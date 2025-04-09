# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User

# # Отменяем стандартную регистрацию модели User
# admin.site.unregister(User)


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#     search_fields = ('username', 'email')
#     list_filter = ('is_staff', 'is_superuser')