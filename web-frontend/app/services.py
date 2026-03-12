"""HTTP client to communicate with backend microservices."""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
TIMEOUT = 5


class ServiceClient:
    """Generic REST client for microservices."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", TIMEOUT)
        try:
            resp = getattr(requests, method)(url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("Service call failed: %s %s - %s", method.upper(), url, e)
            return None

    def get(self, path, **kw):
        return self._request("get", path, **kw)

    def post(self, path, **kw):
        return self._request("post", path, **kw)

    def put(self, path, **kw):
        return self._request("put", path, **kw)

    def patch(self, path, **kw):
        return self._request("patch", path, **kw)

    def delete(self, path, **kw):
        url = f"{self.base_url}{path}"
        try:
            resp = requests.delete(url, timeout=TIMEOUT, **kw)
            resp.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error("Service delete failed: %s - %s", url, e)
            return False


# Service instances
book_client = ServiceClient(settings.BOOK_SERVICE_URL)
catalog_client = ServiceClient(settings.CATALOG_SERVICE_URL)
customer_client = ServiceClient(settings.CUSTOMER_SERVICE_URL)
cart_client = ServiceClient(settings.CART_SERVICE_URL)
order_client = ServiceClient(settings.ORDER_SERVICE_URL)
ship_client = ServiceClient(settings.SHIP_SERVICE_URL)
pay_client = ServiceClient(settings.PAY_SERVICE_URL)
comment_client = ServiceClient(settings.COMMENT_SERVICE_URL)
recommender_client = ServiceClient(settings.RECOMMENDER_SERVICE_URL)
staff_client = ServiceClient(settings.STAFF_SERVICE_URL)
manager_client = ServiceClient(settings.MANAGER_SERVICE_URL)
