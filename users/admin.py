from django.contrib import admin 
from .models import User
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class UserCreationForm(ModelForm):
    """
    Custom Form for User model in the Admin Page
    """
    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    """
    Custom Class for User model in the Admin Page
    """
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("user_display_name",)
    ordering = ("username",)
    date_hierarchy = 'date_joined'

    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'first_name', 'last_name',
                           'role', 'phone', 'is_active',
                           'user_display_name')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'username', 'first_name', 'last_name',
                       'is_superuser', 'is_staff', 'is_active', 'role', 'phone', 'is_active',
                       'user_display_name')}
         ),
    )


admin.site.register(User,CustomUserAdmin)
