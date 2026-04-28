from ipaddress import ip_address
from urllib.parse import urlparse

from django.conf import settings
from rest_framework.permissions import BasePermission


LOCAL_DEMO_HOSTS = {"localhost", "127.0.0.1", "[::1]"}


class IsAdminOrDemoMode(BasePermission):
    """
    Admin endpoints are staff-only in production.
    During local MVP development, ALLOW_DEMO_ADMIN=1 keeps the UI usable.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        return self._allow_local_demo_admin(request)

    def _allow_local_demo_admin(self, request):
        if not (settings.DEBUG and settings.ALLOW_DEMO_ADMIN):
            return False

        remote_addr = request.META.get("REMOTE_ADDR", "")
        try:
            client_ip = ip_address(remote_addr)
        except ValueError:
            return False

        if not (client_ip.is_loopback or client_ip.is_private):
            return False

        host = request.get_host().split(":")[0].lower()
        if host not in LOCAL_DEMO_HOSTS:
            return False

        origin = request.headers.get("Origin")
        if origin:
            origin_host = (urlparse(origin).hostname or "").lower()
            if origin_host not in LOCAL_DEMO_HOSTS:
                return False

        return True
