"""
CJDropshipping API integration — the primary supplier for our store.
CJDropshipping offers: US/EU warehouses, fast 5-8 day shipping,
wide tech product catalog, automated fulfillment API.

API docs: https://developers.cjdropshipping.com/
"""
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

CJ_BASE_URL = "https://developers.cjdropshipping.com/api2.0"


class CJDropshippingService:
    """
    Full integration with CJDropshipping supplier API.
    Handles product discovery, order placement, and tracking.
    """

    def __init__(self):
        self.api_key = settings.cj_api_key
        self.access_token = settings.cj_access_token
        self._token: str | None = None

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "CJ-Access-Token": self._token or self.access_token,
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def authenticate(self) -> str:
        """Authenticate with CJDropshipping and get access token."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{CJ_BASE_URL}/authentication/getAccessToken",
                json={"apiKey": self.api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("result"):
                self._token = data["data"]["accessToken"]
                log.info("cj.authenticated")
                return self._token
            raise ValueError(f"CJ auth failed: {data.get('message')}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_products(
        self,
        keyword: str,
        category_id: str = "",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        Search CJDropshipping product catalog.
        Returns products with pricing, images, and shipping info.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CJ_BASE_URL}/product/list",
                headers=self._headers(),
                params={
                    "productNameEn": keyword,
                    "categoryId": category_id,
                    "pageNum": page,
                    "pageSize": page_size,
                    "isPublish": "true",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if not data.get("result"):
            log.warning("cj.search_failed", keyword=keyword, message=data.get("message"))
            return {"list": [], "total": 0}

        return data.get("data", {})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_product_detail(self, product_id: str) -> dict | None:
        """Get detailed product information including variants and pricing."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CJ_BASE_URL}/product/query",
                headers=self._headers(),
                params={"pid": product_id},
            )
            resp.raise_for_status()
            data = resp.json()

        if not data.get("result"):
            return None
        return data.get("data")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_shipping_options(
        self,
        product_id: str,
        quantity: int,
        country_code: str = "US",
        weight_grams: int = 200,
    ) -> list[dict]:
        """Get available shipping options and estimated costs."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{CJ_BASE_URL}/logistic/freightCalculate",
                headers=self._headers(),
                json={
                    "startCountryCode": "CN",
                    "endCountryCode": country_code,
                    "quantity": quantity,
                    "weight": weight_grams / 1000,  # convert to kg
                    "products": [{"productId": product_id, "quantity": quantity}],
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if not data.get("result"):
            return []
        return data.get("data", [])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_order(self, order_data: dict) -> dict:
        """
        Submit a dropshipping order to CJDropshipping for fulfillment.
        order_data must include shipping address, products, and our order reference.
        """
        payload = {
            "orderNumber": order_data["order_number"],
            "shippingZip": order_data["shipping_address"]["zip"],
            "shippingCountryCode": order_data["shipping_address"]["country_code"],
            "shippingCountry": order_data["shipping_address"]["country"],
            "shippingProvince": order_data["shipping_address"]["state"],
            "shippingCity": order_data["shipping_address"]["city"],
            "shippingAddress": order_data["shipping_address"]["line1"],
            "shippingAddress2": order_data["shipping_address"].get("line2", ""),
            "shippingCustomerName": order_data["customer_name"],
            "shippingPhone": order_data.get("customer_phone", ""),
            "remark": f"TechFlow Order #{order_data['order_number']}",
            "products": [
                {
                    "vid": item["supplier_sku"],
                    "quantity": item["quantity"],
                }
                for item in order_data["items"]
            ],
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{CJ_BASE_URL}/shopping/order/createOrder",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        if not data.get("result"):
            raise ValueError(f"CJ order creation failed: {data.get('message')}")

        log.info("cj.order_created", cj_order_id=data["data"].get("orderId"))
        return data.get("data", {})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_order_tracking(self, cj_order_id: str) -> dict | None:
        """Get tracking information for a placed order."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CJ_BASE_URL}/shopping/order/getOrderDetail",
                headers=self._headers(),
                params={"orderId": cj_order_id},
            )
            resp.raise_for_status()
            data = resp.json()

        if not data.get("result"):
            return None

        order_detail = data.get("data", {})
        return {
            "cj_order_id": cj_order_id,
            "status": order_detail.get("orderStatus"),
            "tracking_number": order_detail.get("trackNumber"),
            "tracking_url": order_detail.get("trackUrl"),
            "carrier": order_detail.get("logisticsName"),
            "shipped_at": order_detail.get("shipTime"),
        }

    async def sync_inventory(self, supplier_product_ids: list[str]) -> list[dict]:
        """Batch check inventory levels for a list of products."""
        results = []
        for pid in supplier_product_ids:
            try:
                detail = await self.get_product_detail(pid)
                if detail:
                    results.append({
                        "supplier_product_id": pid,
                        "stock": detail.get("inventoryNum", 0),
                        "cost_usd": detail.get("sellPrice", 0),
                    })
            except Exception as e:
                log.error("cj.inventory_sync_error", product_id=pid, error=str(e))
        return results

    async def get_trending_categories(self) -> list[dict]:
        """Get hot/trending product categories from CJDropshipping."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CJ_BASE_URL}/product/getCategory",
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        return data.get("data", [])
