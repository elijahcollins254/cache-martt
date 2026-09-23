import logging

from django.conf import settings

from .models import Offer, OfferNotificationSubscription

logger = logging.getLogger(__name__)


def send_offer_sms(phone_number, message):
    """Send an offer-related SMS and return the provider result."""
    from services.sms_service import AfricasTalkingSMSService

    if not phone_number:
        return {
            'status': 'error',
            'message': 'No phone number is available for this notification.',
        }

    try:
        return AfricasTalkingSMSService().send_sms(phone_number, message)
    except Exception as exc:
        logger.exception('Offer SMS failed for %s', phone_number)
        return {
            'status': 'error',
            'message': str(exc),
            'error': str(exc),
        }


def send_subscription_confirmation(subscription, opted_in):
    """Confirm an offer-notification subscription change by SMS."""
    action = 'subscribed to' if opted_in else 'unsubscribed from'
    message = (
        f"CACHE INDUSTRIES: You have successfully {action} new offer SMS notifications. "
        "You can change this anytime from your profile."
    )
    return send_offer_sms(subscription.phone_number, message)


def send_offer_claim_confirmation(user, offer: Offer):
    """Confirm an offer claim by SMS."""
    discount = (
        f'{offer.discount_percent}% off'
        if offer.discount_percent > 0
        else f'KSh {offer.discount_amount} off'
    )
    message = (
        f'CACHE INDUSTRIES: You claimed "{offer.title}" ({discount}). '
        f'Use code {offer.code} when placing your order.'
    )
    return send_offer_sms(user.phone, message)


def notify_subscribers_of_new_offer(offer: Offer):
    """Notify every active subscriber when an offer is created in admin."""
    if not getattr(settings, 'AFRICAS_TALKING_API_KEY', ''):
        logger.warning('Skipping offer SMS notifications because Africa\'s Talking is not configured.')
        return {'sent': 0, 'failed': 0, 'skipped': True}

    message = (
        f"CACHE INDUSTRIES new offer: {offer.title}. "
        f"{offer.discount_percent}% off" if offer.discount_percent > 0
        else f"CACHE INDUSTRIES new offer: {offer.title}. KSh {offer.discount_amount} off"
    )
    message = f"{message}. Code: {offer.code}. Visit cache.co.ke/offers"

    sent = 0
    failed = 0
    subscriptions = OfferNotificationSubscription.objects.filter(
        is_active=True,
    ).exclude(phone_number__isnull=True).exclude(phone_number='')

    for subscription in subscriptions.iterator():
        result = send_offer_sms(subscription.phone_number, message)
        if result.get('status') == 'success':
            sent += 1
        else:
            failed += 1
            logger.warning(
                'Failed to notify offer subscriber %s: %s',
                subscription.phone_number,
                result.get('message'),
            )

    return {'sent': sent, 'failed': failed, 'skipped': False}
