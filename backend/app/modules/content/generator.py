"""
Content Generator using local Ollama
"""
import logging
import requests
import json
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.models import Product

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate product content using local Ollama"""
    
    def __init__(self, model: str = "llama3", ollama_url: str = "http://host.docker.internal:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self._check_ollama()
    
    def _check_ollama(self):
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available = [m['name'] for m in models]
                logger.info(f"Ollama available. Models: {available}")
                if self.model not in [m.split(':')[0] for m in available]:
                    logger.warning(f"Model {self.model} not found, using default")
            else:
                logger.warning("Ollama not available, using fallback templates")
        except Exception as e:
            logger.warning(f"Cannot connect to Ollama: {e}")
    
    def generate_seo_title(self, product_name: str, category: str = None) -> str:
        """Generate SEO-optimized title"""
        prompt = f"""Generate a SEO-optimized product title for dropshipping.
Product: {product_name}
Category: {category or 'general'}

Requirements:
- Include relevant keywords
- Under 70 characters
- Start with main keyword
- Make it click-worthy

Title:"""
        
        result = self._call_ollama(prompt)
        if result:
            return result.strip()[:70]
        return f"{product_name} - Premium Quality Best Seller"
    
    def generate_description(self, product_name: str, category: str = None, 
                             features: list = None) -> str:
        """Generate product description"""
        features_text = "\n".join([f"- {f}" for f in (features or [])]) if features else ""
        
        prompt = f"""Write a compelling product description for dropshipping.

Product: {product_name}
Category: {category or 'general'}
{features_text}

Requirements:
- Emotional and persuasive tone
- Highlight benefits, not just features
- Include social proof elements
- Call to action at the end
- 150-250 words

Description:"""
        
        result = self._call_ollama(prompt)
        if result:
            return result.strip()
        return self._get_fallback_description(product_name, category)
    
    def generate_tags(self, product_name: str, category: str = None) -> list:
        """Generate SEO tags/keywords"""
        prompt = f"""Generate 10 relevant SEO keywords/tags for this product.
Product: {product_name}
Category: {category or 'general'}

Return only comma-separated keywords without numbering:"""
        
        result = self._call_ollama(prompt)
        if result:
            tags = [t.strip().lower() for t in result.split(',')[:10]]
            return tags
        return [product_name.lower(), category.lower() if category else 'product']
    
    def generate_ad_copy(self, product_name: str, price: float = None) -> str:
        """Generate Facebook/TikTok ad copy"""
        price_text = f" for just ${price}" if price else ""
        
        prompt = f"""Write a short, viral Facebook/TikTok ad copy.
Product: {product_name}{price_text}

Requirements:
- Hook in first sentence
- Create urgency
- Include emojis
- Max 125 characters

Ad:"""
        
        result = self._call_ollama(prompt)
        if result:
            return result.strip()[:125]
        return f"🔥 HOT SALE! {product_name} available now{price_text}! 🚀 Limited stock! Order today! 💥"
    
    def generate_full_product_content(self, product: Product) -> Dict:
        """Generate all content for a product"""
        logger.info(f"Generating content for product: {product.name}")
        
        content = {
            'generated_title': self.generate_seo_title(product.name, product.category),
            'generated_description': self.generate_description(
                product.name, 
                product.category,
                features=['High quality', 'Fast shipping', '24/7 support']
            ),
            'tags': self.generate_tags(product.name, product.category),
            'generated_description': self.generate_description(product.name, product.category),
            'seo_title': self.generate_seo_title(product.name, product.category),
        }
        
        return content
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 500}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            return None
    
    def update_product_content(self, product: Product, db: Session) -> Product:
        """Generate and update product with AI content"""
        content = self.generate_full_product_content(product)
        
        if content.get('generated_title'):
            product.generated_title = content['generated_title']
        if content.get('generated_description'):
            product.generated_description = content['generated_description']
        if content.get('tags'):
            product.tags = content['tags']
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Updated product {product.id} with AI content")
        return product
    
    def _get_fallback_description(self, product_name: str, category: str) -> str:
        """Fallback description template"""
        templates = {
            'electronics': f"Discover the ultimate {product_name}! Premium quality, advanced features, and modern design. Perfect for everyday use. Order now and experience the difference!",
            'beauty': f"Transform your beauty routine with {product_name}. Made with premium ingredients for visible results. Loved by thousands. Shop today!",
            'home': f"Upgrade your space with {product_name}. Stylish, functional, and built to last. The perfect addition to any home. Get yours now!",
            'fashion': f"Elevate your style with {product_name}. Trendy, comfortable, and versatile. A must-have for every wardrobe. Shop the collection!",
            'sports': f"Take your fitness to the next level with {product_name}. Durable, professional-grade, and results-driven. Start your journey today!",
            'pet': f"Spoil your furry friend with {product_name}. Safe, fun, and loved by pets everywhere. Your pet deserves the best!",
            'baby': f"Give your little one the best with {product_name}. Safe, gentle, and parent-approved. Shop with confidence!",
            'general': f"Amazing {product_name} that exceeds expectations. High quality, great value, and fast shipping. Order now and see why customers love it!"
        }
        return templates.get(category or 'general', templates['general'])
