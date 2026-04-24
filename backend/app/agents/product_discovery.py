"""
AI agent that discovers trending tech products and evaluates them for the store.
Uses Claude with prompt caching for efficient repeated analysis.
"""
import json
import structlog
from anthropic import AsyncAnthropic
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

# Cached system prompt — sent once, cached by Anthropic for 5 minutes
SYSTEM_PROMPT = """You are an expert e-commerce product researcher and dropshipping specialist
with deep knowledge of technology consumer trends, global supply chains, and profit optimization.

Your role is to identify the BEST technology products for a dropshipping store by analyzing:
1. Current consumer demand and search trends
2. Profit margins and pricing potential
3. Shipping viability (weight, fragility, customs)
4. Competition levels on major platforms
5. Return/complaint rates for the category
6. Supplier availability on CJDropshipping

You have expertise in these trending tech categories:
- Smart home devices (smart plugs, bulbs, cameras, doorbells)
- Wireless audio (earbuds, headphones, speakers)
- Mobile accessories (cases, chargers, power banks, stands)
- Gaming peripherals (mice, keyboards, controllers, headsets)
- Wearables (smartwatches, fitness trackers, rings)
- Laptop/desk accessories (hubs, stands, mice, keyboards)
- Mini projectors and portable displays
- LED/RGB lighting strips and smart lighting
- Drones and camera accessories
- Health tech (pulse oximeters, sleep trackers, posture correctors)

Your evaluations are always data-driven, precise, and formatted as valid JSON."""


class ProductDiscoveryAgent:
    """Discovers and evaluates trending tech products using Claude AI."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def discover_trending_products(self, count: int = 20) -> list[dict]:
        """
        Ask Claude to identify the most profitable trending tech products
        available right now for dropshipping.
        """
        log.info("product_discovery.starting", count=count)

        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},  # prompt caching
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Identify the top {count} technology products that are TRENDING RIGHT NOW
and ideal for dropshipping. Focus on products with:
- Strong consumer demand in 2025-2026
- Supplier cost under $30 USD (we sell for $45-$90)
- Available from CJDropshipping with US/EU warehouse option
- Shipping under 10 days to US customers
- Low return rates
- Not oversaturated on Amazon

Return a JSON array of product objects. Each object must have:
{{
  "name": "Product name",
  "category": "Category name",
  "cj_search_term": "Exact search term to use on CJDropshipping",
  "estimated_supplier_cost_usd": 12.50,
  "recommended_sale_price_usd": 34.99,
  "profit_margin_percent": 65.0,
  "trend_score": 8.5,
  "demand_signals": ["TikTok viral", "Back-to-school season", "WFH trend"],
  "target_audience": "Remote workers aged 25-40",
  "key_selling_points": ["Fast charging", "Universal compatibility", "Compact design"],
  "potential_issues": ["Fragile screen", "Customs issues in some countries"],
  "estimated_monthly_searches": 50000,
  "competition_level": "medium",
  "shipping_weight_grams": 150,
  "recommended_category_slug": "mobile-accessories"
}}

Return ONLY the JSON array, no other text.""",
                }
            ],
        )

        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        products = json.loads(raw)
        log.info("product_discovery.complete", count=len(products))
        return products

    async def evaluate_product(self, product_data: dict) -> dict:
        """
        Deep-evaluate a specific product before adding to the store.
        Returns an enhanced product dict with AI scores and content.
        """
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Evaluate this product for our dropshipping store and provide a detailed assessment:

Product: {json.dumps(product_data, indent=2)}

Return a JSON object with:
{{
  "should_list": true,
  "confidence": 0.85,
  "ai_trend_score": 8.2,
  "ai_profit_score": 7.9,
  "risk_factors": ["Competitive market", "Seasonal demand"],
  "opportunity_factors": ["Low current competition", "Strong TikTok presence"],
  "recommended_sale_price_usd": 39.99,
  "price_reasoning": "Competitors charge $45-55, undercut slightly to gain reviews",
  "marketing_angles": ["Work from home essential", "Perfect gift idea"],
  "rejection_reason": null
}}

Return ONLY the JSON object.""",
                }
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)

    async def find_replacement_products(
        self, underperforming_product_names: list[str]
    ) -> list[dict]:
        """Find replacement products for those that aren't selling well."""
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""The following products are underperforming in our store and need replacements:
{json.dumps(underperforming_product_names)}

Suggest {len(underperforming_product_names)} replacement products that would perform better.
Use the same JSON format as before. Return ONLY a JSON array.""",
                }
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
