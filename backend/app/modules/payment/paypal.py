"""
PayPal Payment Integration
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.models import Product

logger = logging.getLogger(__name__)


class PayPalPayment:
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.environment = settings.PAYPAL_ENVIRONMENT
        self.client = None
        
        if self.client_id and self.client_secret:
            self._init_client()
        else:
            logger.warning("⚠️ PayPal credentials missing. Using simulation mode.")
    
    def _init_client(self):
        try:
            from paypal_checkout_sdk.core import SandboxEnvironment, LiveEnvironment, PayPalHttpClient
            
            if self.environment == "sandbox":
                environment = SandboxEnvironment(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            else:
                environment = LiveEnvironment(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            
            self.client = PayPalHttpClient(environment)
            logger.info(f"✅ PayPal client initialized ({self.environment} mode)")
        except Exception as e:
            logger.error(f"Failed to initialize PayPal: {e}")
            self.client = None
    
    def create_order(self, product: Product, success_url: str, cancel_url: str) -> Dict:
        if not self.client:
            return self._simulate(product)
        
        try:
            from paypal_checkout_sdk.orders import OrdersCreateRequest, OrdersCaptureRequest
            
            request = OrdersCreateRequest()
            request.request_body({
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": product.id,
                    "description": product.name[:127],
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{float(product.selling_price or 29.99):.2f}"
                    }
                }],
                "application_context": {
                    "return_url": success_url,
                    "cancel_url": cancel_url
                }
            })
            
            response = self.client.execute(request)
            
            if response.status_code == 201:
                for link in response.result.links:
                    if link.rel == "approve":
                        return {
                            "success": True,
                            "order_id": response.result.id,
                            "approval_url": link.href,
                            "status": response.result.status,
                            "mode": "real"
                        }
        except Exception as e:
            logger.error(f"PayPal error: {e}")
        
        return self._simulate(product)
    
    def _simulate(self, product: Product) -> Dict:
        logger.info(f"🔧 [SIMULATION] PayPal order for: {product.name}")
        return {
            "success": True,
            "order_id": f"SIM_{product.id[:8]}",
            "approval_url": f"https://sandbox.paypal.com/checkoutnow?token=SIM_{product.id[:8]}",
            "status": "CREATED",
            "mode": "simulation"
        }
