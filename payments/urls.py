from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MpesaSTKPushView, MpesaCallbackView, BNPLViewSet, TradeInView, PaymentStatusView, ZeroPaymentCompletionView

router = DefaultRouter(trailing_slash=True)
router.register(r'bnpl', BNPLViewSet, basename='bnpl')

urlpatterns = [
    path('mpesa/stk-push/', MpesaSTKPushView.as_view(), name='mpesa_stk_push'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),
    path('payment-status/', PaymentStatusView.as_view(), name='payment_status'),
    path('orders/<str:code>/complete-zero/', ZeroPaymentCompletionView.as_view(), name='complete_zero_payment'),
    path('tradein/', TradeInView.as_view(), name='tradein'),
    path('', include(router.urls)),
]
