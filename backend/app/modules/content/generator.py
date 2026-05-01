"""
Content Generator - використовує Ollama в Docker
"""
import logging
import requests
import json
from typing import Dict
from sqlalchemy.orm import Session
from app.database.models import Product

logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self):
        self.ollama_url = "http://ollama:11434"
        self.model = "llama3"
    
    def generate_full_content(self, product: Product, db: Session) -> Dict:
        """Генерує контент через Ollama"""
        
        prompt = f"""Generate a short product title (max 60 chars) and description (max 200 chars) for: {product.name}
Category: {product.category or 'general'}

Return ONLY valid JSON in this format:
{{"title": "...", "description": "..."}}"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 300}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                
                # Парсимо JSON
                try:
                    data = json.loads(result)
                    title = data.get('title', '')
                    description = data.get('description', '')
                except:
                    # Якщо не JSON, пробуємо парсити рядок
                    lines = result.split('\n')
                    title = ""
                    description = ""
                    for line in lines:
                        if 'title' in line.lower():
                            title = line.split(':', 1)[-1].strip()
                        elif 'description' in line.lower():
                            description = line.split(':', 1)[-1].strip()
                
                if title:
                    product.generated_title = title[:60]
                if description:
                    product.generated_description = description[:500]
                
                db.commit()
                logger.info(f"✅ Generation: {product.name}")
            else:
                self._fallback(product, db)
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            self._fallback(product, db)
        
        return {
            "generated_title": product.generated_title,
            "generated_description": product.generated_description,
            "model": self.model
        }
    
    def _fallback(self, product: Product, db: Session):
        product.generated_title = f"{product.name} - Premium Quality"
        product.generated_description = f"High quality {product.name}. Fast shipping worldwide."
        db.commit()
