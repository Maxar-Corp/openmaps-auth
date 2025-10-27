import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractUser,
    UserManager as BaseUserManager,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import utils


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email address must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    User model that uses email addresses instead of usernames.
    """

    # Unique email address is the username.
    email = models.EmailField(_("email address"), unique=True)

    # Password to use for OSM instance when `OPENMAPS_AUTH_OSM_SESSION` is enabled.
    osm_password = models.CharField(
        _("OpenStreetMap password"),
        max_length=128,
        default=utils.random_password,
        editable=False,
    )

    # Password to use for PKCS#12 certificate files.
    pkcs12_password = models.CharField(
        _("PKCS#12 password"),
        max_length=128,
        default=utils.random_password,
        editable=False,
    )

    # JOSM-related field for OAuth1 access token key/secret.
    josm_oauth1_key = models.CharField(
        _("JOSM OAuth1 client key"),
        max_length=40,
        blank=True,
        default="",
        editable=False,
    )
    josm_oauth1_secret = models.CharField(
        _("JOSM OAuth1 client secret"),
        max_length=40,
        blank=True,
        default="",
        editable=False,
    )
    josm_oauth1_token_key = models.CharField(
        _("JOSM OAuth1 token key"),
        max_length=40,
        blank=True,
        default="",
        editable=False,
    )
    josm_oauth1_token_secret = models.CharField(
        _("JOSM OAuth1 token secret"),
        max_length=40,
        blank=True,
        default="",
        editable=False,
    )

    # Don't want `username` field.
    username_validator = None
    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def email_local_part(self):
        """
        Returns the local-part of the user's email address.
        """
        return self.email.split("@")[0]


class Certificate(models.Model):
    """
    Represents a TLS certificate for use by a user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    serial = models.CharField(
        _("certificate serial number"), db_index=True, editable=False, max_length=50
    )
    start = models.DateTimeField(
        _("certificate validity start"), db_index=True, editable=False
    )
    end = models.DateTimeField(
        _("certificate validity end"), db_index=True, editable=False
    )

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")

    @property
    def cert_file(self):
        return str(self.certs_path / f"{self.pk}.crt")

    @property
    def key_file(self):
        return str(self.secrets_path / f"{self.pk}.key")

    @property
    def p12_file(self):
        return str(self.secrets_path / f"{self.pk}.p12")

    @property
    def p12_name(self):
        return f"{self.user.email_local_part}.p12"

    @property
    def certs_path(self):
        return settings.STEP_CERTS / f"{self.user.pk}"

    @property
    def secrets_path(self):
        return settings.STEP_SECRETS / f"{self.user.pk}"

    @property
    def valid(self):
        if not self.start or not self.end:
            return False
        return self.start < timezone.now() < self.end
