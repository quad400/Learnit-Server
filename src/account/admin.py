from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import UserAccount,Profile
from .forms import UserChangeForm,UserCreationForm

# Register your models here.
class InlineProfile(admin.StackedInline):
    model = Profile
    extra=0
    can_delete = False




class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm


    list_display = ['email', 'fullname', 'is_admin','is_active']
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Personal info', {'fields': ('fullname',)}),
        ('Permissions', {'fields': ('is_admin','is_worker','is_instructor',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email","fullname","password1", "password2"),
            },
        ),
    )
    search_fields = ("email","fullname",)
    ordering = ("email",)
    filter_horizontal = ()

    inlines = (InlineProfile,)



admin.site.register(UserAccount, UserAdmin)
admin.site.unregister(Group)