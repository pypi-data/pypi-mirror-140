from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
from djangoldp_stripe.views import CheckoutSessionView, SuccessPageView, CancelledPageView


urlpatterns = [
    url("checkout-session/cancel/", CancelledPageView.as_view()),
    url("checkout-session/success/", SuccessPageView.as_view()),
    url("checkout-session/", CheckoutSessionView.as_view()),
    path(getattr(settings, 'LDP_STRIPE_URL_PATH', "stripe/"), include("djstripe.urls", namespace="djstripe")),
]
