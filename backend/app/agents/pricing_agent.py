"""
AI agent for dynamic price optimization.
Analyzes market conditions, competitor pricing, and sales velocity
to maximize profit while staying competitive.
"""
import json
import structlog
from anthropic import AsyncAnthropic
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

PRICING_SYSTEM_PROMPT = """You are an expert e-commerce pricing strategist specializing in
dropshipping businesses. You understand:

- Psychological pricing (charm pricing: $29.99 vs $30)
- Price elasticity and demand curves
- Competitive positioning strategies
- Seasonal pricing adjustments
- Bundle and upsell opportunities
- Margin optimization without sacrificing conversion rates

Your pricing recommendations are always profitable yet competitive.
You never recommend prices that would result in a loss after supplier costs and fees.
Stripe takes 2.9% + $0.30 per transaction. Always account for this."""


class PricingAgent:
    """Dynamically optimizes product prices using AI market analysis."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.min_multiplier = settings.min_profit_multiplier
        self.target_multiplier = settings.target_profit_multiplier
        self.max_price = settings.max_product_price

    async def optimize_prices(self, products: list[dict]) -> list[dict]:
        """
        Analyze a batch of products and return optimized pricing for each.

        products: list of {id, name, cost_price, sale_price, sale_count,
                           view_count, category, competitor_prices}
        """
        log.info("pricing_agent.optimizing", product_count=len(products))

        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": PRICING_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Optimize pricing for these products in our tech dropshipping store.

Products: {json.dumps(products, indent=2)}

Rules:
- Minimum sale price = supplier cost × {self.min_multiplier} (after Stripe fees)
- Target margin = {self.target_multiplier}x supplier cost
- Maximum price = ${self.max_price}
- Use charm pricing ($X.99 or $X.95)
- If view_count is high but sale_count is low → price may be too high, reduce
- If sale_count is consistently high → test a 5-10% increase
- Set compare_at_price (crossed-out price) ~20-30% above sale_price for perceived value

Return a JSON array, one entry per product:
[{{
  "product_id": "uuid",
  "new_sale_price": 34.99,
  "new_compare_at_price": 44.99,
  "price_change_percent": -8.5,
  "reasoning": "High views, low conversion suggests price sensitivity",
  "expected_impact": "15-20% conversion increase"
}}]

Return ONLY the JSON array.""",
                }
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        updates = json.loads(raw)

        # Safety guard: never let AI set a price below cost × minimum multiplier
        for update in updates:
            product = next((p for p in products if p.get("id") == update.get("product_id")), None)
            if product:
                min_price = product["cost_price"] * self.min_multiplier
                if update["new_sale_price"] < min_price:
                    update["new_sale_price"] = round(min_price, 2)
                    update["reasoning"] += f" [CORRECTED: price floor enforced at ${min_price:.2f}]"

        return updates

    async def suggest_seasonal_adjustments(self, season: str, products: list[dict]) -> list[dict]:
        """Adjust prices for seasonal events (Black Friday, holidays, back-to-school)."""
        response = await self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""For the season/event: {season}
Suggest price adjustments for these products to maximize seasonal sales:
{json.dumps(products, indent=2)}

Return JSON array with: product_id, adjustment_percent, new_price, reasoning.
Return ONLY the JSON array.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)

    async def identify_bundle_opportunities(self, products: list[dict]) -> list[dict]:
        """Identify which products to bundle together for increased AOV."""
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""Identify bundle opportunities from this product catalog:
{json.dumps(products, indent=2)}

Suggest 3-5 high-value bundles. Return JSON array:
[{{
  "bundle_name": "Work From Home Essentials Bundle",
  "product_ids": ["id1", "id2", "id3"],
  "individual_total": 89.97,
  "bundle_price": 74.99,
  "discount_percent": 16.7,
  "bundle_cost": 28.50,
  "bundle_profit": 46.49,
  "target_audience": "Remote workers"
}}]
Return ONLY the JSON array.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
