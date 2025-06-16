from typing import List, Dict
from datetime import datetime

# Since we're implementing a separate module, we need to define or import necessary classes
class MenuItem:
    def __init__(self, item_id: str, name: str, description: str, price: float):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.price = price

class CartItem:
    def __init__(self, menu_item: MenuItem, quantity: int):
        self.menu_item = menu_item
        self.quantity = quantity

class OrderDetails:
    def __init__(self, order_id: str, cart_items: List[CartItem], customer_name: str, 
                 customer_email: str, subtotal: float, tax: float, discount: float, total: float):
        self.order_id = order_id
        self.cart_items = cart_items
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.subtotal = subtotal
        self.tax = tax
        self.discount = discount
        self.total = total
        self.timestamp = datetime.now()

class BillingProcessor:
    """Calculate order totals including taxes and apply discounts."""
    
    def __init__(self, tax_rate: float = 0.08):
        # Initialize with default tax rate (8%), can be customized
        self.tax_rate = tax_rate
        # A simple discount code dictionary for demonstration
        self.discount_codes: Dict[str, float] = {
            "WELCOME10": 0.10,  # 10% off
            "SAVE20": 0.20,    # 20% off
            "FREESHIP": 5.00   # $5 off
        }
        self.current_subtotal = 0.0
    
    def calculate_subtotal(self, cart_items: List[CartItem]) -> float:
        """Calculates and returns the subtotal of the order."""
        subtotal = 0.0
        for item in cart_items:
            subtotal += item.menu_item.price * item.quantity
        
        self.current_subtotal = subtotal
        return subtotal
    
    def apply_discount(self, code: str) -> float:
        """Applies a discount to the current order and returns the discount amount."""
        if not self.current_subtotal:
            raise ValueError("Subtotal must be calculated before applying discounts")
        
        code = code.upper()  # Case-insensitive discount codes
        if code not in self.discount_codes:
            return 0.0  # No discount if code is invalid
        
        discount_value = self.discount_codes[code]
        
        # Handle percentage discounts vs fixed amount discounts
        if discount_value < 1:  # Assuming discounts less than 1 are percentage-based
            return self.current_subtotal * discount_value
        else:  # Fixed amount discount
            return min(discount_value, self.current_subtotal)  # Don't discount more than the subtotal

class ReceiptGenerator:
    """Generate digital or printable receipts for customers based on their orders."""
    
    def generate_receipt(self, order_details: OrderDetails) -> str:
        """Generates a textual receipt and returns it."""
        receipt = []
        receipt.append("=" * 40)
        receipt.append(f"{'ORDER RECEIPT':^40}")
        receipt.append("=" * 40)
        receipt.append(f"Order ID: {order_details.order_id}")
        receipt.append(f"Date: {order_details.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        receipt.append(f"Customer: {order_details.customer_name}")
        receipt.append("-" * 40)
        
        # List items
        receipt.append(f"{'Item':<20}{'Qty':^10}{'Price':>10}")
        receipt.append("-" * 40)
        for item in order_details.cart_items:
            receipt.append(
                f"{item.menu_item.name[:18]:<20}{item.quantity:^10}${item.menu_item.price * item.quantity:>9.2f}"
            )
        
        receipt.append("-" * 40)
        receipt.append(f"{'Subtotal':>30}: ${order_details.subtotal:.2f}")
        receipt.append(f"{'Tax':>30}: ${order_details.tax:.2f}")
        
        if order_details.discount > 0:
            receipt.append(f"{'Discount':>30}: -${order_details.discount:.2f}")
        
        receipt.append(f"{'Total':>30}: ${order_details.total:.2f}")
        receipt.append("=" * 40)
        receipt.append(f"{'Thank you for your order!':^40}")
        receipt.append("=" * 40)
        
        return "\n".join(receipt)
    
    def send_receipt_via_email(self, email: str, receipt: str) -> None:
        """Sends the generated receipt to a customer's email."""
        # In a real implementation, this would use an email sending service
        # For demonstration purposes, we'll just print a confirmation
        print(f"Receipt sent to {email}")
        
        # The actual implementation would look something like:
        # email_service = EmailService()
        # email_service.send(
        #     to=email,
        #     subject="Your Order Receipt",
        #     body=receipt,
        #     from="noreply@restaurant.com"
        # )
