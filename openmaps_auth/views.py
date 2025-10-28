import logging

import social_core.exceptions
import social_django.views
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render

from .utils import get_index_url, set_auth_cookies


logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html", {})


def logout(request):
    response = LogoutView.as_view(template_name="index.html")(request)
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response


def status(request):
    return JsonResponse({"status": "ok"})


def valid(request):
    if not request.user.is_authenticated:
        return JsonResponse({}, status=401)
    else:
        return JsonResponse({})


if settings.OPENMAPS_AUTH_BACKEND:

    def callback(request, *args, **kwargs):
        logger.error("Hereeeeeeeeee request ------>")  # noqa
        logger.error(request)  # noqa
        try:
            response = social_django.views.complete(
                request,
                settings.OPENMAPS_AUTH_BACKEND,
                *args,
                **kwargs,
            )
        except social_core.exceptions.AuthCanceled as error:
            logger.error("Hereeeeeeeeee callback ------>")  # noqa
            logger.error(error)  # noqa
            raise BadRequest
        except social_core.exceptions.AuthForbidden as denied:
            logger.info(denied)
            raise PermissionDenied

        return set_auth_cookies(request, response)

    def login(request):
        return social_django.views.auth(request, settings.OPENMAPS_AUTH_BACKEND)

else:

    def callback(request):
        response = HttpResponseRedirect(get_index_url())
        return set_auth_cookies(request, response)

    login = LoginView.as_view(template_name="login.html")
