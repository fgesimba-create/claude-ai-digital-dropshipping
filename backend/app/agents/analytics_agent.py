"""
AI analytics agent that analyzes store performance, identifies trends,
and generates actionable recommendations to grow revenue.
"""
import json
import structlog
from anthropic import AsyncAnthropic
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

ANALYTICS_SYSTEM_PROMPT = """You are a data-driven e-commerce growth consultant specializing in
dropshipping businesses. You analyze store performance metrics and provide:

- Revenue trend analysis and forecasting
- Product performance insights (winners vs. losers)
- Customer behavior analysis
- Conversion rate optimization suggestions
- Inventory and supplier performance assessment
- Profit margin optimization strategies
- Growth opportunity identification

Your analysis is always grounded in data, quantified where possible, and focused on
actionable steps that a fully automated system can execute without human intervention."""


class AnalyticsAgent:
    """AI agent that analyzes store performance and drives automated improvements."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_daily_report(self, metrics: dict) -> dict:
        """
        Generate a comprehensive daily analytics report with AI insights.
        metrics contains revenue, orders, traffic, top products, etc.
        """
        log.info("analytics_agent.generating_report", date=metrics.get("date"))

        response = await self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": ANALYTICS_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze today's store performance and generate a strategic report.

Today's Metrics:
{json.dumps(metrics, indent=2)}

Return a comprehensive JSON report:
{{
  "executive_summary": "2-3 sentence overview of today's performance",
  "performance_score": 7.8,
  "revenue_analysis": {{
    "assessment": "Revenue is up 12% vs 7-day average",
    "drivers": ["New wireless earbuds product launched", "Weekend traffic boost"],
    "concerns": ["Return rate slightly elevated on product X"]
  }},
  "top_performing_products": [
    {{"product_id": "id", "name": "Product", "revenue": 234.50, "units": 7, "margin": 68.2}}
  ],
  "underperforming_products": [
    {{"product_id": "id", "name": "Product", "issue": "High views, zero sales", "action": "reduce_price"}}
  ],
  "automated_actions_recommended": [
    {{
      "action": "reduce_price",
      "product_id": "uuid",
      "current_price": 49.99,
      "recommended_price": 42.99,
      "reason": "15% price reduction expected to improve conversion"
    }},
    {{
      "action": "deactivate_product",
      "product_id": "uuid",
      "reason": "0 sales in 30 days, high return rate"
    }},
    {{
      "action": "increase_stock_buffer",
      "product_id": "uuid",
      "reason": "Selling faster than expected, risk of stockout"
    }},
    {{
      "action": "feature_product",
      "product_id": "uuid",
      "reason": "High conversion rate, should get more visibility"
    }}
  ],
  "weekly_forecast": {{
    "expected_revenue": 3500.00,
    "confidence": 0.78,
    "key_assumptions": ["Weekend traffic increase", "No major competitor price changes"]
  }},
  "supplier_performance": {{
    "avg_fulfillment_days": 1.8,
    "issues": [],
    "recommendations": []
  }},
  "growth_opportunities": [
    "Add complementary accessories for best-selling earbuds",
    "Test Facebook ad for wireless charger category"
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

    async def analyze_product_performance(self, products_with_metrics: list[dict]) -> list[dict]:
        """
        Classify each product as winner/neutral/loser and recommend actions.
        """
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=[
                {
                    "type": "text",
                    "text": ANALYTICS_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze product performance and classify each:
{json.dumps(products_with_metrics, indent=2)}

Return JSON array:
[{{
  "product_id": "uuid",
  "classification": "winner|neutral|loser",
  "performance_score": 8.2,
  "key_metrics": {{"conversion_rate": 3.2, "profit_per_unit": 18.50}},
  "recommended_action": "feature|price_test|refresh_content|deactivate|maintain",
  "action_details": "Specific action to take"
}}]
Return ONLY the JSON array.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)

    async def forecast_demand(self, historical_data: dict) -> dict:
        """Forecast next 30 days revenue and top product demand."""
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Forecast demand for next 30 days based on historical data:
{json.dumps(historical_data, indent=2)}

Return JSON:
{{
  "forecast_period": "30 days",
  "expected_revenue": 12500.00,
  "expected_orders": 285,
  "confidence_level": 0.72,
  "top_products_forecast": [
    {{"product_id": "uuid", "expected_units": 45, "expected_revenue": 2025.00}}
  ],
  "seasonal_factors": ["Back to school season", "Tech gift season approaching"],
  "risk_factors": ["Potential shipping delays", "Competitor price war in earbuds"],
  "recommended_inventory_actions": []
}}
Return ONLY the JSON object.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
