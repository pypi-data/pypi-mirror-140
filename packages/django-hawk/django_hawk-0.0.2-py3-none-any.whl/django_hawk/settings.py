from django.conf import settings

DEFAULTS = {
    "NO_CREDENTIALS_MESSAGE": "Authentication credentials were not provided.",
    "INCORRECT_CREDENTIALS_MESSAGE": "Incorrect authentication credentials.",
    "MAX_PER_PAGE": 500,
}


class DjangoHawkSettings:
    HAWK_INCOMING_ACCESS_KEY: str
    HAWK_INCOMING_SECRET_KEY: str
    NO_CREDENTIALS_MESSAGE: str
    INCORRECT_CREDENTIALS_MESSAGE: str
    MAX_PER_PAGE: int

    def __getattr__(self, attr):
        django_settings = getattr(settings, "DJANGO_HAWK", {})

        # Check if present in user settings
        if attr in django_settings:
            return django_settings[attr]

        # Check if present in defaults
        default_value = DEFAULTS.get(attr, None)
        if default_value is None and attr not in DEFAULTS:
            raise AttributeError(f"No value set for DJANGO_HAWK['{attr}']")
        return default_value


django_hawk_settings = DjangoHawkSettings()
