from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = "Create the initial inventory roles and assign their permissions."

    def handle(self, *args, **options):
        viewer, _ = Group.objects.get_or_create(name="Viewer")
        inventory_manager, _ = Group.objects.get_or_create(name="Inventory Manager")

        inventory_permissions = Permission.objects.filter(
            content_type__app_label="inventory"
        )
        view_permissions = inventory_permissions.filter(codename__startswith="view_")
        manager_permissions = inventory_permissions.filter(
            Q(codename__startswith="view_")
            | Q(codename__startswith="add_")
            | Q(codename__startswith="change_")
        )

        viewer.permissions.remove(*inventory_permissions)
        viewer.permissions.add(*view_permissions)
        inventory_manager.permissions.remove(*inventory_permissions)
        inventory_manager.permissions.add(*manager_permissions)

        self.stdout.write(self.style.SUCCESS("Inventory roles configured."))
