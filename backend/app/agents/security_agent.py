"""
AI security agent that continuously monitors the platform for vulnerabilities,
suspicious activity, and compliance issues — then auto-remediates what it can.
"""
import json
import structlog
from datetime import datetime, timezone
from anthropic import AsyncAnthropic
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

SECURITY_SYSTEM_PROMPT = """You are a cybersecurity expert specializing in e-commerce platform security.
You assess security risks for online stores with a focus on:

- Payment security (PCI-DSS compliance)
- Customer data protection (GDPR, CCPA)
- API endpoint security
- SQL injection and XSS prevention
- Rate limiting and DDoS protection
- Suspicious transaction patterns (fraud detection)
- Dependency vulnerabilities
- SSL/TLS configuration
- Admin access controls

You provide actionable security recommendations ranked by severity (critical, high, medium, low).
For each finding you indicate whether it can be auto-remediated or requires manual intervention."""


class SecurityAgent:
    """AI-powered security monitoring and auto-remediation agent."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run_security_scan(self, scan_data: dict) -> dict:
        """
        Run a comprehensive security scan. scan_data contains:
        - recent_orders: list of recent orders (for fraud detection)
        - api_logs: recent API request patterns
        - failed_auth_attempts: count and IPs
        - dependency_versions: current package versions
        - config_snapshot: non-sensitive config items
        """
        log.info("security_agent.scan_starting")

        response = await self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=3000,
            system=[
                {
                    "type": "text",
                    "text": SECURITY_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Perform a security assessment of our e-commerce platform based on this data:

{json.dumps(scan_data, indent=2)}

Return a JSON security report:
{{
  "scan_timestamp": "{datetime.now(timezone.utc).isoformat()}",
  "overall_risk_level": "low|medium|high|critical",
  "risk_score": 3.2,
  "findings": [
    {{
      "severity": "high",
      "category": "authentication",
      "title": "Multiple failed login attempts from IP 192.168.1.1",
      "description": "Detected 47 failed login attempts in 5 minutes — possible brute force",
      "affected_component": "admin login endpoint",
      "can_auto_remediate": true,
      "remediation_action": "block_ip",
      "remediation_params": {{"ip": "192.168.1.1", "duration_hours": 24}}
    }}
  ],
  "auto_remediations_performed": [],
  "manual_actions_required": [],
  "compliance_notes": {{
    "pci_dss": "Compliant — no card data stored",
    "gdpr": "Review cookie consent implementation"
  }},
  "recommendations": [
    "Enable 2FA for admin accounts",
    "Review API rate limits"
  ]
}}

Return ONLY the JSON object.""",
                }
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(raw)
        log.info("security_agent.scan_complete", risk_level=result.get("overall_risk_level"))
        return result

    async def analyze_fraud_signals(self, orders: list[dict]) -> list[dict]:
        """
        Analyze recent orders for fraud signals.
        Returns flagged orders with risk scores and recommended actions.
        """
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": SECURITY_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze these orders for fraud signals:
{json.dumps(orders, indent=2)}

Fraud signals to check:
- High-value orders from new customers
- Multiple orders to same address with different cards
- Shipping to reshipping addresses (freight forwarders)
- Unusual quantities
- Mismatched billing/shipping countries
- Disposable email addresses

Return JSON array of flagged orders:
[{{
  "order_id": "uuid",
  "fraud_risk_score": 0.85,
  "risk_level": "high",
  "signals": ["New account, high value", "Freight forwarder address"],
  "recommended_action": "hold_for_review|auto_cancel|flag_for_manual_review"
}}]
Return ONLY the JSON array. Return empty array [] if no fraud detected.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)

    async def get_security_recommendations(self, platform_stats: dict) -> list[str]:
        """Get actionable security improvement recommendations."""
        response = await self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on these platform stats, provide top 5 security recommendations:
{json.dumps(platform_stats, indent=2)}

Return a JSON array of recommendation strings.
Return ONLY the JSON array.""",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
