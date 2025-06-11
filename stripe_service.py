import os
import stripe
from flask import current_app

# Initialize Stripe with the secret key from environment variables
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_default_key')

def get_domain():
    """Get the current domain based on environment"""
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return os.environ.get('REPLIT_DEPLOY_DOMAIN')
    elif os.environ.get('REPLIT_DOMAINS'):
        return os.environ.get('REPLIT_DOMAINS').split(',')[0]
    return 'localhost:5000'

def create_checkout_session(price_id, mode='payment'):
    """Create a Stripe checkout session
    
    Args:
        price_id: Stripe Price ID for the product
        mode: 'payment' for one-time payments, 'subscription' for recurring
        
    Returns:
        The checkout session URL
    """
    try:
        domain = get_domain()
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode=mode,
            success_url=f'https://{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{domain}/pricing',
            automatic_tax={'enabled': False},  # Disable automatic tax for simplicity
        )
        return checkout_session.url
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error creating checkout session: {str(e)}")
        else:
            print(f"Error creating checkout session: {str(e)}")
        return None

def create_subscription_product(name, description, price, interval='month'):
    """Create a new subscription product in Stripe
    
    Args:
        name: Product name
        description: Product description
        price: Price in USD (e.g., 9.99)
        interval: Billing interval ('month' or 'year')
    
    Returns:
        dict with product and price IDs
    """
    try:
        # Create the product
        product = stripe.Product.create(
            name=name,
            description=description,
            active=True,
        )
        
        # Create the price
        price_obj = stripe.Price.create(
            product=product.id,
            unit_amount=int(price * 100),  # Convert to cents
            currency='usd',
            recurring={
                'interval': interval,
            },
        )
        
        return {
            'product_id': product.id,
            'price_id': price_obj.id
        }
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error creating subscription product: {str(e)}")
        else:
            print(f"Error creating subscription product: {str(e)}")
        return None

def create_one_time_product(name, description, price):
    """Create a new one-time payment product in Stripe
    
    Args:
        name: Product name
        description: Product description
        price: Price in USD (e.g., 49.99)
    
    Returns:
        dict with product and price IDs
    """
    try:
        # Create the product
        product = stripe.Product.create(
            name=name,
            description=description,
            active=True,
        )
        
        # Create the price
        price_obj = stripe.Price.create(
            product=product.id,
            unit_amount=int(price * 100),  # Convert to cents
            currency='usd',
        )
        
        return {
            'product_id': product.id,
            'price_id': price_obj.id
        }
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error creating one-time product: {str(e)}")
        else:
            print(f"Error creating one-time product: {str(e)}")
        return None

def get_session(session_id):
    """Retrieve a checkout session
    
    Args:
        session_id: Stripe checkout session ID
        
    Returns:
        Checkout session or None if error
    """
    try:
        return stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error retrieving session: {str(e)}")
        else:
            print(f"Error retrieving session: {str(e)}")
        return None
