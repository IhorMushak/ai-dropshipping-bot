"""
Landing Page Generator - з повною checkout формою
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
        self.api_url = "https://ai-dropshipping-backend.onrender.com"
    
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
        
        # API ендпоінт для checkout
        api_base = self.api_url
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product.name} | Premium Quality</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .product-card {{ background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); transition: all 0.2s; }}
        .btn-primary:hover {{ transform: translateY(-2px); filter: brightness(1.05); }}
    </style>
</head>
<body class="p-6">
    <div class="max-w-6xl mx-auto">
        <div class="product-card">
            <div class="grid md:grid-cols-2">
                <div class="p-8 bg-gray-50">
                    <img src="{image_url}" alt="{product.name}" class="w-full rounded-lg" onerror="this.src='https://placehold.co/500x500/1a1a2e/3b82f6?text=No+Image'">
                    <div class="mt-6 text-center">
                        <div class="inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">✨ AI SELECTED • SCORE {final_score:.0f}</div>
                        <div class="mt-4 text-sm text-gray-500">🚚 Free Worldwide Shipping • 30-Day Returns</div>
                    </div>
                </div>
                <div class="p-8">
                    <h1 class="text-2xl font-bold text-gray-800">{product.name}</h1>
                    <div class="mt-4">
                        <span class="text-3xl font-bold text-green-600">${selling_price:.2f}</span>
                        <span class="text-lg text-gray-400 line-through ml-2">${original_price:.2f}</span>
                        <span class="ml-2 px-2 py-1 bg-red-100 text-red-600 rounded text-sm">-{discount}%</span>
                    </div>
                    <p class="mt-6 text-gray-600">{description}</p>
                    
                    <div class="mt-8 border-t pt-6">
                        <h3 class="font-semibold mb-4">Complete Your Order</h3>
                        <form id="checkoutForm" class="space-y-4">
                            <input type="hidden" id="productId" value="{product.id}">
                            <div><input type="text" id="name" placeholder="Full Name *" required class="w-full px-4 py-2 border border-gray-300 rounded-lg"></div>
                            <div><input type="email" id="email" placeholder="Email *" required class="w-full px-4 py-2 border border-gray-300 rounded-lg"></div>
                            <div><input type="text" id="address" placeholder="Address Line 1 *" required class="w-full px-4 py-2 border border-gray-300 rounded-lg"></div>
                            <div class="grid grid-cols-2 gap-4">
                                <input type="text" id="city" placeholder="City *" required class="px-4 py-2 border border-gray-300 rounded-lg">
                                <input type="text" id="zip" placeholder="ZIP *" required class="px-4 py-2 border border-gray-300 rounded-lg">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <input type="text" id="state" placeholder="State" class="px-4 py-2 border border-gray-300 rounded-lg">
                                <select id="country" class="px-4 py-2 border border-gray-300 rounded-lg">
                                    <option value="US">United States</option>
                                    <option value="GB">United Kingdom</option>
                                    <option value="DE">Germany</option>
                                    <option value="FR">France</option>
                                    <option value="CA">Canada</option>
                                    <option value="AU">Australia</option>
                                </select>
                            </div>
                            <button type="submit" class="btn-primary w-full text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2">
                                Continue to PayPal <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.882a.766.766 0 0 1 .757-.634h9.266c2.316 0 3.968.636 4.944 1.91.978 1.274 1.121 3.046.433 5.321-.694 2.302-1.342 4.084-1.945 5.347-.6 1.258-1.325 2.288-2.173 3.09-.848.802-1.793 1.376-2.835 1.722-.97.322-1.97.484-2.997.484h-3.47l-.788 4.774a.761.761 0 0 1-.755.674z"/></svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div id="loadingOverlay" class="hidden fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p class="mt-4 text-gray-700">Processing your order...</p>
        </div>
    </div>
    <script>
        const API_URL = '{api_base}/api/v1';
        
        document.getElementById('checkoutForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const data = {{
                product_id: document.getElementById('productId').value,
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                address_line1: document.getElementById('address').value,
                city: document.getElementById('city').value,
                zip: document.getElementById('zip').value,
                state: document.getElementById('state').value,
                country: document.getElementById('country').value
            }};
            
            if (!data.name || !data.email || !data.address_line1 || !data.city || !data.zip) {{
                alert('Please fill all required fields');
                return;
            }}
            
            document.getElementById('loadingOverlay').classList.remove('hidden');
            
            try {{
                const res = await fetch(`${{API_URL}}/checkout/create`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});
                const result = await res.json();
                if (result.success && result.paypal_url) {{
                    window.location.href = result.paypal_url;
                }} else {{
                    alert('Failed to create order. Please try again.');
                    document.getElementById('loadingOverlay').classList.add('hidden');
                }}
            }} catch(e) {{
                console.error(e);
                alert('Network error. Please try again.');
                document.getElementById('loadingOverlay').classList.add('hidden');
            }}
        }});
    </script>
</body>
</html>'''
