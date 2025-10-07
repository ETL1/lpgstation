from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Instructor, Student


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'fname', 'is_member', 'uid','access_level',)
    list_filter = ('email', 'is_staff', 'is_active', 'fname', 'is_member')
    fieldsets = (
        (None, {'fields': ('uid', 'token','email', 'password', 'fname', 'sname', 'username', 'lastOnline', 'phone_num', 'acc_token', 'logi', 'lati', 'u_pic', 'access_level', 'site_id')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_member', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('uid', 'token','email', 'fname', 'sname', 'username', 'lastOnline', 'phone_num', 'acc_token', 'logi', 'lati', 'u_pic', 'password1', 'password2', 'access_level', 'is_staff', 'is_active', 'is_member')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Instructor)
admin.site.register(Student)
