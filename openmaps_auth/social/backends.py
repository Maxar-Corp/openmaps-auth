import logging
import secrets
import time
from urllib.parse import urljoin, urlparse, urlunparse
from xml.dom import minidom

import jwt
from django.conf import settings
from social_core.backends.oauth import BaseOAuth2
from social_core.backends.okta_openidconnect import (
    OktaOpenIdConnect as BaseOktaOpenIdConnect,
)
from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.backends.openstreetmap import (
    OpenStreetMapOAuth as BaseOpenStreetMapOAuth,
)
from social_core.utils import slugify

logger = logging.getLogger(__name__)  # noqa


class LoginGovOpenIdConnect(OpenIdConnectAuth):
    name = "login-gov"

    ACR_VALUES = "http://idmanagement.gov/ns/assurance/ial/1"
    DEFAULT_SCOPE = ["openid", "email"]
    JWT_DECODE_OPTIONS = {"leeway": 30}
    OIDC_ENDPOINT = "https://secure.login.gov"
    TOKEN_TTL_SEC = 5 * 60  # 5 minutes into the future.

    def auth_allowed(self, response, details):
        """
        Only allow authentication from accounts with verified email addresses.
        """
        if details.get("email_verified"):
            return super().auth_allowed(response, details)
        else:
            return False

    def auth_complete_params(self, state=None):
        return {
            "client_assertion": self.generate_client_secret(),
            "client_assertion_type": (
                "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
            ),
            "code": self.data.get("code", ""),
            "grant_type": "authorization_code",
        }

    def auth_params(self, state=None):
        params = {"acr_values": self.ACR_VALUES}
        params.update(super().auth_params(state))
        return params

    def generate_client_secret(self):
        now = int(time.time())
        client_id = self.setting("KEY")
        private_key = self.setting("SECRET")
        payload = {
            "iss": client_id,
            "sub": client_id,
            "aud": self.access_token_url(),
            "jti": secrets.token_urlsafe(32),
            "exp": now + self.TOKEN_TTL_SEC,
        }
        logger.error("Hereeeeeeeeee generate_client_secret ------>")  # noqa
        logger.error(
            jwt.encode(payload, key=private_key, algorithm=self.JWT_ALGORITHMS[0])
        )  # noqa
        return jwt.encode(payload, key=private_key, algorithm=self.JWT_ALGORITHMS[0])

    def get_key_and_secret(self):
        client_id = self.setting("KEY")
        client_secret = self.generate_client_secret()
        return client_id, client_secret

    def get_user_details(self, response):
        user_details = super().get_user_details(response)
        user_details["email_verified"] = response["email_verified"]
        return user_details


class OktaOpenIdConnect(BaseOktaOpenIdConnect):
    # This fix for Okta OIDC configuration URLs copied from:
    # https://github.com/python-social-auth/social-core/pull/663
    def oidc_config_url(self):
        # https://developer.okta.com/docs/reference/api/oidc/#well-known-openid-configuration
        url = urlparse(self.api_url())

        # If the URL path does not contain an authorizedServerId, we need
        # to truncate the path in order to generate a proper openid-configuration
        # URL.
        if url.path == "/oauth2/":
            url = url._replace(path="")

        return urljoin(
            urlunparse(url),
            "./.well-known/openid-configuration?client_id={}".format(
                self.setting("KEY")
            ),
        )

    def oidc_config(self):
        return self.get_json(self.oidc_config_url())


class OpenStreetMapMixin:
    def get_osm_email(self, username):
        return f"{slugify(username)}@{settings.OSM_USER_EMAIL_DOMAIN}"

    def get_user_details(self, response):
        """Return user details from OpenStreetMap account"""
        return {
            "email": self.get_osm_email(response["username"]),
            "fullname": "",
            "first_name": "",
            "last_name": "",
            "username": response["username"],
        }

    def user_data_response(self, response):
        try:
            dom = minidom.parseString(response.content)
        except ValueError:
            return None
        user = dom.getElementsByTagName("user")[0]
        try:
            avatar = dom.getElementsByTagName("img")[0].getAttribute("href")
        except IndexError:
            avatar = None
        return {
            "account_created": user.getAttribute("account_created"),
            "avatar": avatar,
            "id": user.getAttribute("id"),
            "username": user.getAttribute("display_name"),
        }


class OpenStreetMapOAuth(OpenStreetMapMixin, BaseOpenStreetMapOAuth):
    """OpenStreetMap OAuth1 authentication backend"""

    ACCESS_TOKEN_URL = settings.OSM_OAUTH1_ACCESS_TOKEN_URL
    AUTHORIZATION_URL = settings.OSM_OAUTH1_AUTHORIZATION_URL
    REQUEST_TOKEN_URL = settings.OSM_OAUTH1_REQUEST_TOKEN_URL

    def user_data(self, access_token, *args, **kwargs):
        """Return user data provided by OSM"""
        return self.user_data_response(
            self.oauth_request(access_token, settings.OSM_USER_DETAILS_URL)
        )


class OpenStreetMapOAuth2(OpenStreetMapMixin, BaseOAuth2):
    """OpenStreetMap OAuth2 authentication backend"""

    name = "openstreetmap-oauth2"
    ACCESS_TOKEN_METHOD = "POST"
    ACCESS_TOKEN_URL = settings.OSM_OAUTH2_ACCESS_TOKEN_URL
    AUTHORIZATION_URL = settings.OSM_OAUTH2_AUTHORIZATION_URL
    DEFAULT_SCOPE = settings.OSM_OAUTH2_DEFAULT_SCOPE
    EXTRA_DATA = [
        ("id", "id"),
        ("avatar", "avatar"),
        ("account_created", "account_created"),
    ]
    SCOPE_SEPARATOR = "+"

    def user_data(self, access_token, *args, **kwargs):
        """Return user data provided by OSM"""
        return self.user_data_response(
            self.request(
                settings.OSM_USER_DETAILS_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )
        )
