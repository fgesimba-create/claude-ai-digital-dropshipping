# TechFlow — AI-Powered Dropshipping Platform

A fully autonomous technology dropshipping store powered by Claude AI (claude-opus-4-7 & claude-sonnet-4-6).
**You never touch the products.** The AI finds them, prices them, writes copy, fulfills orders, and monitors security — automatically.

---

## How It Works (Fully Automated)

```
Every 24h: Claude AI scans for trending tech products → searches CJDropshipping → evaluates profitability
           → generates product descriptions + SEO → lists them automatically

Every 6h:  AI analyzes sales velocity + competitor prices → adjusts your prices for max profit

Every 2h:  Syncs inventory with supplier → deactivates out-of-stock items automatically

Every 1h:  Syncs order tracking from CJDropshipping → emails customers their tracking numbers

Every 12h: AI security scan → detects fraud patterns + threats → auto-remediates what it can

Daily 6am: AI generates analytics report → executes recommended actions (feature winners, kill losers)

Real-time: Customer orders → Stripe payment → Auto-forwarded to CJDropshipping → Customer notified
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| AI Brain | Claude claude-opus-4-7 (strategy) + claude-sonnet-4-6 (content/pricing) + claude-haiku-4-5-20251001 (quick tasks) |
| Backend | FastAPI + Python 3.12 + APScheduler |
| Database | PostgreSQL + Redis |
| Frontend | Next.js 15 + TypeScript + Tailwind CSS |
| Payments | Stripe (PaymentIntents + Webhooks) |
| Supplier | CJDropshipping API (US/EU warehouses, 5-10 day shipping) |
| Emails | SendGrid |
| Alerts | Slack Webhooks |
| Deploy | Docker Compose |

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <repo>
cd claude-ai-digital-dropshipping
cp .env.example .env
# Edit .env with your API keys
```

### 2. Required API Keys

Get these before starting:

| Service | Where to get | Cost |
|---------|-------------|------|
| **Anthropic** | platform.anthropic.com | Pay per use |
| **CJDropshipping** | developers.cjdropshipping.com | Free |
| **Stripe** | dashboard.stripe.com | 2.9% + $0.30/transaction |
| **SendGrid** | sendgrid.com | Free up to 100 emails/day |
| **Slack Webhook** | api.slack.com/apps | Free |

### 3. Configure Your `.env`

```bash
ANTHROPIC_API_KEY=sk-ant-...
CJ_API_KEY=your_key
CJ_ACCESS_TOKEN=your_token
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
ADMIN_EMAIL=you@yourdomain.com
ADMIN_PASSWORD=strong_password_here
STORE_DOMAIN=https://yourdomain.com
SECRET_KEY=64_random_chars_here
```

### 4. Launch Everything

```bash
docker-compose up -d
```

On first launch, the platform will:
1. Create the database schema
2. Seed 8 product categories
3. Immediately trigger AI product discovery (adds ~10 products in ~5 minutes)
4. Start all automation schedules

### 5. Set Up Stripe Webhooks

In your Stripe dashboard → Webhooks, add:
- **Endpoint URL**: `https://yourdomain.com/api/webhooks/stripe`
- **Events to listen to**: `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.refunded`
- Copy the **webhook signing secret** to `STRIPE_WEBHOOK_SECRET` in your `.env`

---

## Accessing Your Store

| URL | Description |
|-----|-------------|
| `http://localhost:3000` | Customer storefront |
| `http://localhost:3000/admin` | Admin login |
| `http://localhost:3000/admin/dashboard` | Command center |
| `http://localhost:8000/api/docs` | API documentation (dev only) |
| `http://localhost:8000/health` | System health check |

### Admin Dashboard Features
- Real-time revenue, profit, and order metrics
- AI-generated daily report with insights
- Security scan status
- Manual automation triggers (run any AI task on demand)
- Order management with tracking
- Product performance data

---

## AI Agents

### 1. Product Discovery Agent (`claude-opus-4-7`)
Runs every 24 hours. Identifies trending tech products with strong profit potential, searches CJDropshipping for real suppliers, evaluates each product, and automatically adds winners to your store.

**Products it targets:**
- Wireless earbuds & headphones
- Smart home devices (plugs, cameras, lights)
- Mobile accessories (chargers, stands, cases)
- Gaming peripherals
- Wearables & fitness trackers
- LED/RGB products
- Portable projectors

### 2. Pricing Agent (`claude-sonnet-4-6`)
Runs every 6 hours. Analyzes each product's view-to-sale conversion rate and adjusts prices using psychological pricing principles. Never prices below your minimum margin floor.

### 3. Content Agent (`claude-sonnet-4-6`)
Generates: product names, descriptions (HTML), short descriptions, SEO meta titles + descriptions, tags, and feature lists. Every product gets professional copy automatically.

### 4. Security Agent (`claude-opus-4-7`)
Runs every 12 hours. Analyzes order patterns for fraud, checks API access patterns, reviews configuration for vulnerabilities, and alerts you to anything critical via Slack.

### 5. Analytics Agent (`claude-opus-4-7`)
Generates daily reports at 6am UTC. Classifies each product as winner/neutral/loser and automatically: features winners, reduces prices on stalling products, deactivates persistent losers.

---

## Supplier: CJDropshipping

Why CJDropshipping:
- Free to use API, no monthly fees
- US, EU, and UK warehouses available (faster shipping)
- 5-10 business day average delivery to US
- Automated order fulfillment via API
- No minimum order quantities
- Wide tech product catalog

When you receive an order:
1. Customer pays via Stripe
2. Webhook fires → order marked as paid
3. Order automatically forwarded to CJDropshipping API
4. CJDropshipping packs and ships directly to customer
5. Tracking number auto-synced every hour
6. Customer receives shipping email automatically

---

## Customization

### Change Profit Margins
In `.env`:
```
MIN_PROFIT_MULTIPLIER=2.2    # Never sell for less than 2.2x cost
TARGET_PROFIT_MULTIPLIER=2.8 # AI aims for 2.8x cost
MAX_PRODUCT_PRICE=299.00     # No product listed above this
```

### Change Automation Schedule
```
PRODUCT_DISCOVERY_INTERVAL_HOURS=24
PRICE_UPDATE_INTERVAL_HOURS=6
INVENTORY_SYNC_INTERVAL_HOURS=2
SECURITY_SCAN_INTERVAL_HOURS=12
```

### Store Branding
Update the store name throughout:
```
STORE_NAME=YourStoreName
STORE_DOMAIN=https://yourdomain.com
```

---

## Deployment (Production)

### Option A: Any VPS (DigitalOcean, Linode, Vultr)

```bash
# On your server (Ubuntu 22.04+)
apt update && apt install -y docker.io docker-compose
git clone <your-repo>
cd claude-ai-digital-dropshipping
cp .env.example .env && nano .env
docker-compose -f docker-compose.yml up -d
```

Add Nginx reverse proxy + Let's Encrypt SSL:
```nginx
server {
    server_name yourdomain.com;
    location / { proxy_pass http://localhost:3000; }
    location /api { proxy_pass http://localhost:8000; }
}
```

### Option B: Railway / Render / Fly.io
Each service (backend, frontend, db, redis) deploys as a separate container.
Set environment variables in the platform's dashboard.

---

## Security

- All admin endpoints are JWT-protected (8-hour token expiry)
- Stripe webhook signatures are verified
- Customer passwords are never stored (Stripe handles payment)
- No card data ever touches your servers (fully PCI-compliant)
- AI security agent scans for fraud and threats every 12 hours
- Rate limiting and CORS protection built in

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Customer Browser                      │
│              Next.js 15 Storefront (Port 3000)          │
└─────────────────────────┬───────────────────────────────┘
                          │ /api/* (rewrites)
┌─────────────────────────▼───────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │              APScheduler (Automation)            │    │
│  │  • Product Discovery (24h)                      │    │
│  │  • Price Optimization (6h)                      │    │
│  │  • Inventory Sync (2h)                          │    │
│  │  • Order Tracking (1h)                          │    │
│  │  • Security Scan (12h)                          │    │
│  │  • Daily Report (6am UTC)                       │    │
│  └──────────────────┬──────────────────────────────┘    │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐    │
│  │              Claude AI Agents                    │    │
│  │  claude-opus-4-7 (strategy, security, analytics) │    │
│  │  claude-sonnet-4-6 (content, pricing, discovery) │    │
│  │  claude-haiku-4-5-20251001 (quick tasks)              │    │
│  └──────────────────┬──────────────────────────────┘    │
└─────────────────────┼───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
  PostgreSQL        Redis     CJDropshipping API
  (orders,         (cache)   (supplier fulfillment)
   products,
   analytics)
```

---

## License

MIT License — use commercially, no attribution required.
