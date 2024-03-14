from django import forms

from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import (
    User,
    Profile,
    Vendor,
    Product,
    Document,
    Comment,
    Permissions
)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_superuser"
        ]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'image']


class UserForm(forms.Form):
    username = forms.CharField(max_length=255)
    email = forms.EmailField()
    user_type = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'vendor_name',
            'company_website_url',
            'company_established_on',
            'no_of_employees',
            'country',
            'city',
            'address',
            'phone_number',
            'description'
        ]


class ProductForm(forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all())

    class Meta:
        model = Product
        fields = [
            'vendor',
            'name',
            'software_type',
            'client_type',
            'business_area',
            'module',
            'last_demo_date',
            'last_review_date',
            'next_review_date',
            'document_attached',
            'cloud_status',
            'additional_information',
            'internal_professional_services'
        ]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document']


DocumentFormSet = inlineformset_factory(Product, Document, form=DocumentForm, extra=1)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['commented_by', 'vendor', 'product', 'content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None and (rating < 1 or rating > 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permissions
        fields = ['name', 'content_type', 'codename', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
