import logging
from typing import TypedDict

from django.core.cache import cache
from django.utils.crypto import constant_time_compare
from django_hawk.settings import django_hawk_settings
from mohawk import Receiver
from mohawk.exc import HawkFail

logger = logging.getLogger(__name__)


class LookupCredentials(TypedDict):
    id: str
    key: str
    algorithm: str


def lookup_credentials(access_key_id) -> LookupCredentials:
    """
    Raises a HawkFail if the passed ID is not equal to
    """

    if not constant_time_compare(
        access_key_id,
        django_hawk_settings.HAWK_INCOMING_ACCESS_KEY,
    ):
        raise HawkFail(
            "No Hawk ID of {access_key_id}".format(
                access_key_id=access_key_id,
            )
        )

    lookup_creds: LookupCredentials = {
        "id": django_hawk_settings.HAWK_INCOMING_ACCESS_KEY,
        "key": django_hawk_settings.HAWK_INCOMING_SECRET_KEY,
        "algorithm": "sha256",
    }
    return lookup_creds


def seen_nonce(access_key_id, nonce, _) -> bool:
    """
    Returns if the passed access_key_id/nonce combination has been
    used within 60 seconds.
    """

    cache_key = "activity_stream:{access_key_id}:{nonce}".format(
        access_key_id=access_key_id,
        nonce=nonce,
    )

    # cache.add only adds key if it isn't present
    seen_cache_key = not cache.add(
        cache_key,
        True,
        timeout=60,
    )

    if seen_cache_key:
        logger.warning("Already seen nonce {nonce}".format(nonce=nonce))

    return seen_cache_key


def authorise(request) -> Receiver:
    """
    Raises a HawkFail if the passed request cannot be authenticated
    """

    return Receiver(
        lookup_credentials,
        request.META["HTTP_AUTHORIZATION"],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
        seen_nonce=seen_nonce,
    )
