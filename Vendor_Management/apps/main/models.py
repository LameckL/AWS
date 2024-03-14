from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .enums import CloudStatus, UserTypes, PermissionCategories

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Permission
from django.db import models

from apps.main.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    """
    username = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(
        max_length=50,
        choices=UserTypes.choices(),
        default=UserTypes.NORMAL_USER
    )

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='users/images', default='users/images/avatar.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profiles"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.email


class Permissions(Permission):
    category = models.CharField(
        max_length=50,
        choices=PermissionCategories.choices,
        default=PermissionCategories.PRODUCT_MANAGEMENT
    )
    description = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Permissions'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return self.name


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class Vendor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor")
    description = models.TextField(blank=True, null=True)
    vendor_name = models.CharField(max_length=255)
    company_website_url = models.URLField(blank=True, null=True)
    company_established_on = models.PositiveIntegerField(
        validators=[MinValueValidator(1600),
                    MaxValueValidator(timezone.now().year)])
    no_of_employees = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "vendors"
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ["-created_at"]

    def __str__(self):
        return self.vendor_name


class Product(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    software_type = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    client_type = models.CharField(max_length=255)
    last_demo_date = models.DateTimeField(blank=True, null=True)
    last_review_date = models.DateTimeField(blank=True, null=True)
    next_review_date = models.DateTimeField(blank=True, null=True)
    document_attached = models.BooleanField(default=False)
    cloud_status = models.CharField(
        max_length=20, choices=CloudStatus.choices(), default=CloudStatus.NATIVE)
    additional_information = models.TextField(blank=True, null=True)
    internal_professional_services = models.BooleanField(default=False)
    business_area = models.CharField(max_length=255)

    class Meta:
        db_table = "products"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Document(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to="products/documents/%Y-%m-%d", blank=True, max_length=250)

    class Meta:
        db_table = "documents"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.document}"


class Comment(models.Model):
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-timestamp"]

    def __str__(self):
        if self.vendor:
            return f"Comment on {self.vendor.vendor_name} - {self.timestamp}"
        elif self.product:
            return f"Comment on {self.product.name} - {self.timestamp}"
        else:
            return "Orphan Comment"
