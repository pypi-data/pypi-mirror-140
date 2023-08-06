from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.urls import reverse

from djangoldp.utils import is_authenticated_user
from djangoldp_stripe.permissions import user_has_subscriptions_in_products_list


required_product_subs = set(getattr(settings, 'PERMS_REQUIRED_STRIPE_SUBSCRIPTIONS_GLOBALLY', []))
exclude_paths = getattr(settings, 'EXCLUDE_FROM_GLOBAL_STRIPE_SUBSCRIPTION_REQ', [])


class StripeSubscriptionRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _request_path_excluded(self, request):
        return request.path.startswith(reverse('admin:index')) or request.path.startswith('/checkout-session/') \
            or request.path.startswith('/has-valid-subscription/') or request.path in exclude_paths

    def __call__(self, request):
        if is_authenticated_user(request.user) and \
            not self._request_path_excluded(request) and len(required_product_subs) > 0:

            if not user_has_subscriptions_in_products_list(request.user, required_product_subs):
                raise PermissionDenied('user must be subscribed to required products to access this site')
        
        return self.get_response(request)
