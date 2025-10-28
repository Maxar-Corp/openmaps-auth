import string

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.crypto import get_random_string
from social_core.utils import is_url


def get_index_url():
    if is_url(settings.INDEX_URL):
        return settings.INDEX_URL
    else:
        return reverse(settings.INDEX_URL)


def random_password(length=48, alphabet=string.ascii_letters + string.digits):
    return get_random_string(length, alphabet)


def set_auth_cookies(request, response):
    if settings.OPENMAPS_AUTH_OSM_SESSION:
        response.set_cookie(
            settings.OSM_SESSION_KEY,
            request.session[settings.OSM_SESSION_KEY],
            domain=settings.SESSION_COOKIE_DOMAIN,
        )
    messages.add_message(
        request,
        messages.SUCCESS,
        f"You've successfully logged in to {settings.OPENMAPS_AUTH_TITLE}!",
    )
    return response
