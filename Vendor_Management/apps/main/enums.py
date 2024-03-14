import enum

from django.db.models import TextChoices


class CloudStatus(str, enum.Enum):
    ENABLED = "Enabled"
    NATIVE = "Native"
    BASED = "Based"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class UserTypes(str, enum.Enum):
    ADMIN = "Admin"
    VENDOR = "Vendor"
    NORMAL_USER = "Normal User"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PermissionCategories(TextChoices):
    VENDOR_MANAGEMENT = 'Vendor Management', 'Vendor Management'
    PRODUCT_MANAGEMENT = 'Product Management', 'Product Management'
    MANAGE_USER_PERMISSIONS = 'Manage User Permissions', 'Manage User Permissions'
