from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase

from users.models import User

from offers.models import Offer, UserOffer


class OfferClaimNotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='offer-customer',
            password='test-password',
            phone='0712345678',
        )
        self.offer = Offer.objects.create(
            title='Weekend Wash',
            description='Save on weekend laundry.',
            discount_percent=20,
            code='WEEKEND20',
            valid_from=timezone.now(),
        )
        self.url = f'/offers/{self.offer.pk}/claim'
        self.client.force_authenticate(user=self.user)

    @patch('offers.views.send_offer_claim_confirmation')
    def test_claim_sends_confirmation_sms(self, send_confirmation):
        send_confirmation.return_value = {'status': 'success'}

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(UserOffer.objects.filter(user=self.user, offer=self.offer).exists())
        send_confirmation.assert_called_once_with(self.user, self.offer)
        self.assertNotIn('sms_notification', response.data)

    @patch('offers.views.send_offer_claim_confirmation')
    def test_claim_is_kept_when_confirmation_sms_fails(self, send_confirmation):
        send_confirmation.return_value = {'status': 'error', 'message': 'provider unavailable'}

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(UserOffer.objects.filter(user=self.user, offer=self.offer).exists())
        self.assertEqual(response.data['sms_notification'], 'Offer claimed, but the confirmation SMS could not be sent.')
