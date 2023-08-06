from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from djangoldp.views import NoCSRFAuthentication
from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.exceptions import ValidationError
from djstripe.models.core import Price
import stripe

STRIPE_LIVE_SECRET_KEY = settings.STRIPE_LIVE_SECRET_KEY
STRIPE_LIVE_MODE = settings.STRIPE_LIVE_MODE
STRIPE_TEST_SECRET_KEY = settings.STRIPE_TEST_SECRET_KEY

stripe.api_key = STRIPE_LIVE_SECRET_KEY if STRIPE_LIVE_MODE else STRIPE_TEST_SECRET_KEY


class SuccessPageView(APIView):
    authentication_classes = (NoCSRFAuthentication,)

    def get(self, request):
        return render(request, 'success.html')


class CancelledPageView(APIView):
    authentication_classes = (NoCSRFAuthentication,)

    def get(self, request):
        return render(request, 'cancel.html')


class CheckoutSessionView(APIView):
    authentication_classes = (NoCSRFAuthentication,)

    def get(self, request):
        # lookup_key must be passed in the requesting form
        lookup_key = request.GET.get('lookup_key', None)

        if lookup_key is None:
            raise ValidationError('lookup_key is required')

        price = get_object_or_404(Price, lookup_key=lookup_key)

        return render(request, 'checkout.html', context={'product': price.product, 'price': price, 'unit_amount': price.unit_amount * 0.01})

    def post(self, request):
        # lookup_key must be passed in the requesting form
        lookup_key = request.data.get('lookup_key', None)

        if lookup_key is None:
            raise ValidationError('lookup_key is required')

        price = get_object_or_404(Price, lookup_key=lookup_key)
        host_url = settings.SITE_URL

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=host_url + '/checkout-session/success/',
            cancel_url=host_url + '/checkout-session/cancel/',
        )
        return redirect(checkout_session.url)