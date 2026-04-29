# AI Dropshipping Bot

An intelligent dropshipping automation platform that helps you find trending products, generate content, and manage orders automatically using AI.

## Features

- Trend Scanning: Automatically identifies trending products across social media and marketplaces
- Product Scoring: AI-powered scoring system to evaluate product potential
- Content Generation: Creates product descriptions and ad copy using AI
- Supplier Integration: Seamless integration with AliExpress and other suppliers
- Marketplace Sync: Connect with Shopify and other e-commerce platforms
- Ad Management: Automated ad campaign creation and optimization
- Analytics: Comprehensive metrics and ROI tracking

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose

### Installation

1. Clone the repository
2. Copy .env.example to .env and configure your settings
3. Run docker-compose up -d
4. Initialize the database: docker-compose exec backend python scripts/init_db.py

### Access the Application

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## License

MIT
