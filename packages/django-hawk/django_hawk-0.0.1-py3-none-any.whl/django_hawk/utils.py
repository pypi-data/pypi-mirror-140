import logging

from django.http import HttpRequest
from django_hawk.authentication import authorise
from django_hawk.settings import django_hawk_settings
from mohawk.exc import HawkFail

logger = logging.getLogger(__name__)


class DjangoHawkAuthenticationFailed(Exception):
    pass


def authenticate_request(request: HttpRequest):
    if "HTTP_AUTHORIZATION" not in request.META:
        raise DjangoHawkAuthenticationFailed(
            django_hawk_settings.NO_CREDENTIALS_MESSAGE
        )

    try:
        hawk_receiver = authorise(request)
    except HawkFail as e:
        logger.warning(
            "Failed authentication {e}".format(
                e=e,
            )
        )
        raise DjangoHawkAuthenticationFailed(
            django_hawk_settings.INCORRECT_CREDENTIALS_MESSAGE
        )
    return hawk_receiver
