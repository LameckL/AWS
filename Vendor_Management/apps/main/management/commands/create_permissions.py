from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from apps.main.management.permissions import custom_permissions
from apps.main.management.permissions.custom_permissions import vendor_management_permissions, product_management_permissions
from apps.main.models import Permissions


class Command(BaseCommand):
    help = "Creates default permission groups for users"

    def handle(self, *args, **options):
        self.create_permissions('vendor', vendor_management_permissions)
        self.create_permissions('product', product_management_permissions)

    def create_permissions(self, category, permissions):
        try:
            content_type = self.get_content_type(category)
            for codename, name, category, description in permissions:
                permission, created = Permissions.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    name=name,
                    category=category,
                    description=description
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Permission '{permission.name}' created"))
                else:
                    # Permission already exists, update the name if it's different
                    if permission.name != name:
                        permission.name = name
                        permission.save()
                        self.stdout.write(self.style.SUCCESS(f"Permission '{permission.name}' updated"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Permission '{permission.name}' already exists"))

            self.stdout.write(self.style.SUCCESS(f"Permissions for category '{category}' created successfully"))
        except Exception as error:
            self.stdout.write(self.style.ERROR(str(error)))
            raise error

    @staticmethod
    def get_content_type(category):
        if category == 'vendor':
            return ContentType.objects.get(app_label='main', model='vendor')
        elif category == 'product':
            return ContentType.objects.get(app_label='main', model='product')
        else:
            return None  # Handle other cases as needed
