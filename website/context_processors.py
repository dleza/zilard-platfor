from .models import SiteSetting


def site_settings(request):
    """Confirmed contact details/social links, available to every public template."""
    return {"site_settings": SiteSetting.load()}
