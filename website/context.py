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
        # Facebook page link (fallback button) + the Page Plugin timeline embed,
        # both derived from one setting so a future YouTube swap is one change.
        "facebook_page_url": settings.FACEBOOK_PAGE_URL,
        "facebook_embed_url": (
            "https://www.facebook.com/plugins/page.php?href="
            f"{quote_plus(settings.FACEBOOK_PAGE_URL)}"
            "&tabs=timeline&width=400&height=520&small_header=true"
            "&adapt_container_width=true&hide_cover=false&show_facepile=false"
        ),
        "service_times": [
            ("Sunday School", "9:45 AM"),
            ("Morning Service", "11:00 AM"),
            ("Evening Service", "6:00 PM"),
            ("Wednesday Bible Study", "7:00 PM"),
        ],
    }
