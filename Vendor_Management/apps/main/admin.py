from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserChangeForm, UserCreationForm
from .models import (
    User,
    Profile,
    Permissions,
    Vendor,
    Product,
    Document,
    Comment
)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    readonly_fields = ["date_joined", ]
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "user_type",
        "is_active",
        "is_staff",
        "is_superuser"
    ]
    list_filter = ["is_staff", "is_superuser"]
    fieldsets = [
        ("Login Credentials", {"fields": ["username", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name", "email"]}),
        ("Permissions", {"fields": ["user_type", "is_staff", "is_superuser", "user_permissions"]}),
        ("Important dates", {"fields": ["last_login", "date_joined"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "user_type",
                    "password1",
                    "password2"
                ],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'bio', 'created_at', 'updated_at')
    search_fields = ('user__username',)


@admin.register(Permissions)
class PermissionsAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        'vendor_name',
        'company_website_url',
        'company_established_on',
        'no_of_employees',
        'country',
        'city',
        'address',
        'phone_number',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'vendor_name',
        'company_website_url',
        'company_established_on',
        'no_of_employees',
        'description'
    )
    list_filter = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'vendor',
        'name',
        'last_demo_date',
        'last_review_date',
        'next_review_date',
        'document_attached',
        'cloud_status',
        'internal_professional_services',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'vendor__vendor_name',
        'name',
        'last_demo_date',
        'last_review_date',
        'next_review_date',
        'additional_information',
        'description'
    )
    list_filter = (
        'cloud_status',
        'internal_professional_services',
        'created_at',
        'updated_at'
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('product', 'document', 'created_at', 'updated_at')
    search_fields = ('product__name', 'document', 'description')
    list_filter = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('commented_by', 'vendor', 'product', 'content', 'rating', 'timestamp')
    search_fields = ('commented_by__username', 'vendor__vendor_name', 'product__name', 'content')
    list_filter = ('rating', 'timestamp')
