"""
Landing Page Generator - з PayPal Smart Buttons
"""
import logging
import os
from typing import Dict
from sqlalchemy.orm import Session
from app.database.models import Product

logger = logging.getLogger(__name__)


class LandingPageGenerator:
    def __init__(self):
        self.storage_path = "/tmp/landings"
        self.base_url = "http://localhost:8000/static/landings"
    
    def generate(self, product: Product, db: Session) -> Dict:
        selling_price = float(product.selling_price) if product.selling_price else 29.99
        final_score = float(product.final_score) if product.final_score else (float(product.trend_score) if product.trend_score else 0)
        
        page_id = product.id.replace("-", "")[:16]
        
        html_content = self._generate_html(product, page_id, selling_price, final_score)
        
        os.makedirs(self.storage_path, exist_ok=True)
        
        file_path = f"{self.storage_path}/{page_id}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        product.shopify_handle = page_id
        db.commit()
        
        page_url = f"{self.base_url}/{page_id}.html"
        
        logger.info(f"✅ Landing page generated: {page_url}")
        
        return {
            "success": True,
            "product_id": product.id,
            "product_name": product.name,
            "page_url": page_url,
            "page_id": page_id
        }
    
    def _generate_html(self, product: Product, page_id: str, selling_price: float, final_score: float) -> str:
        image_url = product.images[0] if product.images else ""
        description = product.generated_description or product.description or "Premium quality product. Fast shipping worldwide."
        
        original_price = round(selling_price * 1.5, 2)
        discount = round((1 - selling_price / original_price) * 100) if selling_price and original_price else 0
        
        from app.core.config import settings
        paypal_client_id = settings.PAYPAL_CLIENT_ID or "test"
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product.name} | Premium Quality</title>
    <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .product-card {{ background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); display: flex; flex-wrap: wrap; }}
        .product-image {{ flex: 1; min-width: 300px; background: #f3f4f6; display: flex; align-items: center; justify-content: center; padding: 40px; }}
        .product-image img {{ width: 100%; max-width: 400px; border-radius: 16px; }}
        .product-info {{ flex: 1; padding: 48px; background: white; }}
        .badge {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 16px; border-radius: 50px; font-size: 12px; font-weight: 600; margin-bottom: 20px; }}
        h1 {{ font-size: 32px; font-weight: 700; color: #1f2937; margin-bottom: 16px; }}
        .current-price {{ font-size: 42px; font-weight: 800; color: #059669; }}
        .old-price {{ font-size: 20px; color: #9ca3af; text-decoration: line-through; margin-left: 12px; }}
        .discount {{ display: inline-block; background: #fee2e2; color: #dc2626; padding: 4px 12px; border-radius: 50px; font-size: 14px; font-weight: 600; margin-left: 12px; }}
        .description {{ color: #4b5563; line-height: 1.6; margin-bottom: 32px; }}
        .features {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 32px; }}
        .feature {{ display: flex; align-items: center; gap: 12px; font-size: 14px; }}
        .paypal-container {{ margin-top: 20px; }}
        .guarantee {{ text-align: center; margin-top: 24px; font-size: 13px; color: #9ca3af; }}
        @media (max-width: 768px) {{ .product-info {{ padding: 32px; }} h1 {{ font-size: 24px; }} .current-price {{ font-size: 32px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="product-card">
            <div class="product-image">
                <img src="{image_url}" alt="{product.name}" onerror="this.src='https://placehold.co/500x500/1a1a2e/3b82f6?text=No+Image'">
            </div>
            <div class="product-info">
                <div class="badge">✨ AI SELECTED • SCORE {final_score:.0f}</div>
                <h1>{product.name}</h1>
                <div>
                    <span class="current-price">${selling_price:.2f}</span>
                    <span class="old-price">${original_price:.2f}</span>
                    <span class="discount">-{discount}% OFF</span>
                </div>
                <div class="description">{description}</div>
                <div class="features">
                    <div class="feature">🚚 Free Worldwide Shipping</div>
                    <div class="feature">✅ 30-Day Money Back</div>
                    <div class="feature">🔒 Secure Checkout</div>
                    <div class="feature">💬 24/7 Support</div>
                </div>
                <div class="paypal-container">
                    <div id="paypal-button-container"></div>
                </div>
                <div class="guarantee">🔥 Limited stock • Order now!</div>
            </div>
        </div>
    </div>
    
    <script>
        paypal.Buttons({{
            createOrder: function(data, actions) {{
                return actions.order.create({{
                    purchase_units: [{{
                        description: "{product.name[:50]}",
                        amount: {{
                            value: "{selling_price:.2f}"
                        }}
                    }}]
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    alert('Transaction completed by ' + details.payer.name.given_name);
                    window.location.href = '/success.html';
                }});
            }},
            onError: function(err) {{
                console.error('PayPal Error:', err);
                alert('Payment error. Please try again.');
            }}
        }}).render('#paypal-button-container');
    </script>
</body>
</html>'''
