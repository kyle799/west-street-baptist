"""Template context processor: expose site-wide brand/content constants."""
from urllib.parse import quote_plus

from django.conf import settings


def site(request):
    maps_query = f"{settings.SITE_NAME}, {settings.SITE_STREET}, {settings.SITE_CITY_STATE_ZIP}"
    return {
        "site_name": settings.SITE_NAME,
        "site_tagline": settings.SITE_TAGLINE,
        "site_city": settings.SITE_CITY,
        "site_street": settings.SITE_STREET,
        "site_city_state_zip": settings.SITE_CITY_STATE_ZIP,
        # Keyless Google Maps embed + directions links built from the address.
        "maps_embed_url": f"https://www.google.com/maps?q={quote_plus(maps_query)}&output=embed",
        "maps_link_url": f"https://www.google.com/maps/search/?api=1&query={quote_plus(maps_query)}",
        "service_times": [
            ("Sunday School", "10:00 AM"),
            ("Sunday Worship", "11:00 AM & 6:00 PM"),
            ("Wednesday Bible Study & Prayer", "7:00 PM"),
        ],
    }
