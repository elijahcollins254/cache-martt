from django.test import TestCase

from services.admin import ServiceAdmin, activate_services, deactivate_services
from services.models import Service, ServiceCategory


class ServiceAdminActionsTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name='General', slug='general')
        self.service_1 = Service.objects.create(
            name='Repair',
            category=self.category,
            price='1500.00',
            is_active=False,
        )
        self.service_2 = Service.objects.create(
            name='Cleaning',
            category=self.category,
            price='1200.00',
            is_active=True,
        )

    def test_activate_services_action_updates_queryset(self):
        queryset = Service.objects.filter(pk__in=[self.service_1.pk, self.service_2.pk])

        activate_services(None, None, queryset)

        self.service_1.refresh_from_db()
        self.service_2.refresh_from_db()
        self.assertTrue(self.service_1.is_active)
        self.assertTrue(self.service_2.is_active)

    def test_deactivate_services_action_updates_queryset(self):
        queryset = Service.objects.filter(pk__in=[self.service_1.pk, self.service_2.pk])

        deactivate_services(None, None, queryset)

        self.service_1.refresh_from_db()
        self.service_2.refresh_from_db()
        self.assertFalse(self.service_1.is_active)
        self.assertFalse(self.service_2.is_active)

    def test_service_admin_registers_bulk_status_actions(self):
        self.assertIn(activate_services, ServiceAdmin.actions)
        self.assertIn(deactivate_services, ServiceAdmin.actions)
