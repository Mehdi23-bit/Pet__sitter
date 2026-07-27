from rest_framework.throttling import BaseThrottle
from  django.core.cache import cache
from .tools import get_client_ip

class IPRateThrottle(BaseThrottle):
    """
    Generic IP-based throttle. Set `throttle_scope`, `rate_limit`,
    and `window` on each view that uses this class.
    """
    def allow_request(self, request, view):
        # pull config from the view, not the throttle class
        scope = getattr(view, 'throttle_scope', 'default')
        rate_limit = getattr(view, 'throttle_rate_limit', 5)
        window = getattr(view, 'throttle_window', 3600)

        ip = get_client_ip(request)
        if not ip:
            return True

        key = f"throttle:{scope}:{ip}"
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=window)
            count = 1

        return count <= rate_limit

    def wait(self):
        return 60  # could be smarter, covered below
