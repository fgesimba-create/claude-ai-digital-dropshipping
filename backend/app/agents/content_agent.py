"""
AI agent that generates compelling product descriptions, SEO metadata,
and marketing copy for every product automatically.
"""
import json
import structlog
from anthropic import AsyncAnthropic
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

CONTENT_SYSTEM_PROMPT = """You are an expert e-commerce copywriter specializing in technology products.
You create compelling, conversion-optimized product content that:

- Leads with customer benefits, not just features
- Uses power words that trigger buying impulses
- Is SEO-optimized with natural keyword integration
- Builds trust and reduces purchase anxiety
- Creates urgency without being pushy
- Speaks directly to the target audience's pain points

Your writing style is clear, enthusiastic, and authoritative — like a knowledgeable friend
who genuinely loves tech and wants to help people find the right product."""


class ContentAgent:
    """Generates AI-powered product content for the store."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.store_name = settings.store_name

    async def generate_product_content(self, product_data: dict) -> dict:
        """
        Generate complete product content: description, short description,
        SEO title, SEO description, and selling points.
        """
        log.info("content_agent.generating", product=product_data.get("name"))

        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": CONTENT_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate complete product content for this item in our tech store "{settings.store_name}":

Product: {json.dumps(product_data, indent=2)}

Return a JSON object:
{{
  "name": "Refined product name (keep it concise and compelling)",
  "short_description": "1-2 sentence hook that makes people want to read more (under 160 chars)",
  "description": "Full HTML description with <h2>, <ul>, <p> tags. 200-350 words. Lead with benefits. Include: what it is, key features as bullet points, who it's for, what's in the box.",
  "meta_title": "SEO page title (under 60 chars, include main keyword)",
  "meta_description": "SEO meta description (under 155 chars, include call to action)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "key_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
  "use_cases": ["Perfect for gaming sessions", "Great for travel", "Ideal for the office"]
}}

Return ONLY the JSON object.""",
                }
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)

    async def generate_batch_content(self, products: list[dict]) -> list[dict]:
        """Generate content for multiple products efficiently."""
        results = []
        for product in products:
            try:
                content = await self.generate_product_content(product)
                content["product_id"] = product.get("id")
                results.append(content)
            except Exception as e:
                log.error("content_agent.error", product=product.get("name"), error=str(e))
        return results

    async def refresh_stale_content(self, products: list[dict]) -> list[dict]:
        """
        Identify and refresh product content that's outdated or underperforming.
        Uses lighter Haiku model for quick content refresh.
        """
        response = await self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Review these products and identify which need content refreshes
(low view counts, bounce rates, or content older than 90 days):
{json.dumps(products, indent=2)}

For each product needing refresh, return updated short_description and meta_description only.
JSON array: [{{"product_id": "id", "short_description": "...", "meta_description": "..."}}]
Return ONLY the JSON array.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)

    async def generate_homepage_content(self, top_products: list[dict], season: str = "") -> dict:
        """Generate hero section copy and featured product blurbs."""
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate homepage hero content for our tech store "{settings.store_name}".
Season/Context: {season or "General"}
Top products to feature: {json.dumps(top_products[:5], indent=2)}

Return JSON:
{{
  "hero_headline": "Main hero headline (punchy, 5-8 words)",
  "hero_subheadline": "Supporting line that expands on headline (under 100 chars)",
  "hero_cta": "Call to action button text",
  "featured_section_title": "Section title for featured products",
  "value_propositions": [
    {{"icon": "truck", "title": "Fast Shipping", "description": "Delivered in 5-8 days"}},
    {{"icon": "shield", "title": "Secure Checkout", "description": "256-bit SSL encryption"}},
    {{"icon": "refresh", "title": "Easy Returns", "description": "30-day hassle-free returns"}},
    {{"icon": "star", "title": "Top Rated", "description": "Thousands of 5-star reviews"}}
  ]
}}
Return ONLY the JSON object.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
