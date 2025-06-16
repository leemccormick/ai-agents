import gradio as gr
import json
import uuid
from datetime import datetime

# Import modules from the backend
from order_management.order_management import MenuItem, CartItem, MenuManager, CartManager
from billing_and_receipts.billing_and_receipts import OrderDetails, BillingProcessor, ReceiptGenerator
from inventory_tracking.inventory_tracking import InventoryManager

# Initialize the managers and processors
menu_manager = MenuManager()
cart_manager = CartManager()
billing_processor = BillingProcessor()
receipt_generator = ReceiptGenerator()
inventory_manager = InventoryManager()

# Add some sample menu items
sample_items = [
    MenuItem("1", "Cheeseburger", "Classic beef patty with cheese", 9.99),
    MenuItem("2", "Caesar Salad", "Fresh romaine lettuce with Caesar dressing", 7.99),
    MenuItem("3", "Margherita Pizza", "Classic pizza with tomato and mozzarella", 12.99),
    MenuItem("4", "Chocolate Cake", "Rich chocolate cake with frosting", 6.99),
    MenuItem("5", "Iced Tea", "Refreshing black tea with lemon", 2.99),
]

# Add items to menu and inventory
for item in sample_items:
    menu_manager.menu_items.append(item)
    inventory_manager.add_menu_item(item, initial_stock=10)

# ----- ORDER MANAGEMENT FUNCTIONS -----

def view_menu():
    """Returns the menu as a formatted string"""
    menu_items = menu_manager.view_menu()
    menu_text = "MENU:\n"
    for item in menu_items:
        menu_text += f"ID: {item.item_id} - {item.name} - ${item.price:.2f}\n"
        menu_text += f"  {item.description}\n"
    return menu_text

def search_item(item_name):
    """Searches for an item by name"""
    item = menu_manager.search_item(item_name)
    if item:
        return f"Found: {item.name} - ${item.price:.2f} - {item.description}"
    else:
        return "Item not found"

def add_item_to_cart(item_id, quantity):
    """Adds an item to the cart"""
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be greater than zero"
        
        # Find the item in the menu
        item = None
        for menu_item in menu_manager.menu_items:
            if menu_item.item_id == item_id:
                item = menu_item
                break
        
        if not item:
            return f"Item with ID {item_id} not found"
        
        # Check inventory
        if not inventory_manager.check_stock(item):
            return f"Sorry, {item.name} is out of stock"
        
        if quantity > inventory_manager.get_stock_level(item):
            return f"Sorry, only {inventory_manager.get_stock_level(item)} of {item.name} available"
        
        # Add to cart
        cart_manager.add_to_cart(item, quantity)
        inventory_manager.decrease_stock(item, quantity)
        return f"Added {quantity} x {item.name} to cart"
    
    except ValueError as e:
        return str(e)

def view_cart():
    """Returns the cart contents as a formatted string"""
    cart_items = cart_manager.get_cart_items()
    if not cart_items:
        return "Cart is empty"
    
    cart_text = "CART:\n"
    for item in cart_items:
        cart_text += f"{item.quantity} x {item.menu_item.name} - ${item.menu_item.price:.2f} each = ${item.menu_item.price * item.quantity:.2f}\n"
    
    cart_text += f"\nTotal: ${cart_manager.get_cart_total():.2f}"
    return cart_text

def clear_cart():
    """Clears the cart and returns inventory"""
    cart_items = cart_manager.get_cart_items()
    for item in cart_items:
        inventory_manager.increase_stock(item.menu_item, item.quantity)
    
    cart_manager.clear_cart()
    return "Cart cleared. Items returned to inventory."

# ----- BILLING AND RECEIPTS FUNCTIONS -----

def calculate_bill(discount_code=""):
    """Calculates the bill with subtotal, tax, discount, and total"""
    cart_items = cart_manager.get_cart_items()
    if not cart_items:
        return "Cart is empty. Add items before calculating bill."
    
    subtotal = billing_processor.calculate_subtotal(cart_items)
    discount = billing_processor.apply_discount(discount_code) if discount_code else 0.0
    tax = subtotal * billing_processor.tax_rate
    total = subtotal + tax - discount
    
    bill_text = "BILL CALCULATION:\n"
    bill_text += f"Subtotal: ${subtotal:.2f}\n"
    bill_text += f"Tax ({billing_processor.tax_rate*100:.0f}%): ${tax:.2f}\n"
    
    if discount > 0:
        bill_text += f"Discount: -${discount:.2f}\n"
    
    bill_text += f"Total: ${total:.2f}"
    return bill_text

def generate_receipt(customer_name, customer_email, discount_code=""):
    """Generates a receipt for the current order"""
    cart_items = cart_manager.get_cart_items()
    if not cart_items:
        return "Cart is empty. Add items before generating a receipt."
    
    if not customer_name or not customer_email:
        return "Please provide customer name and email"
    
    # Calculate values
    subtotal = billing_processor.calculate_subtotal(cart_items)
    discount = billing_processor.apply_discount(discount_code) if discount_code else 0.0
    tax = subtotal * billing_processor.tax_rate
    total = subtotal + tax - discount
    
    # Create order details
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order_details = OrderDetails(
        order_id=order_id,
        cart_items=cart_items,
        customer_name=customer_name,
        customer_email=customer_email,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total
    )
    
    # Generate receipt
    receipt = receipt_generator.generate_receipt(order_details)
    
    # Clear cart (in a real application, you might want to ask confirmation first)
    cart_manager.clear_cart()
    
    return receipt

def send_receipt_by_email(receipt, email):
    """Simulates sending a receipt by email"""
    if not receipt or not email:
        return "Receipt or email missing"
    
    receipt_generator.send_receipt_via_email(email, receipt)
    return f"Receipt sent to {email}"

# ----- INVENTORY MANAGEMENT FUNCTIONS -----

def view_inventory():
    """Shows the current inventory levels"""
    inventory_text = "INVENTORY STATUS:\n"
    
    for item_id, item in inventory_manager.menu_items.items():
        stock = inventory_manager.get_stock_level(item)
        status = "In Stock" if stock > 0 else "OUT OF STOCK"
        inventory_text += f"{item.name}: {stock} units - {status}\n"
    
    return inventory_text

def update_item_stock(item_id, new_quantity):
    """Updates the stock level of an item"""
    try:
        new_quantity = int(new_quantity)
        if new_quantity < 0:
            return "Quantity cannot be negative"
        
        # Find the item
        item = None
        for menu_item in menu_manager.menu_items:
            if menu_item.item_id == item_id:
                item = menu_item
                break
        
        if not item:
            return f"Item with ID {item_id} not found"
        
        # Update stock
        inventory_manager.update_stock_level(item, new_quantity)
        return f"Updated stock for {item.name} to {new_quantity} units"
    
    except ValueError as e:
        return str(e)

def list_out_of_stock():
    """Lists all out-of-stock items"""
    out_of_stock = inventory_manager.get_out_of_stock_items()
    
    if not out_of_stock:
        return "All items are in stock"
    
    out_text = "OUT OF STOCK ITEMS:\n"
    for item in out_of_stock:
        out_text += f"- {item.name}\n"
    
    return out_text

def list_low_stock(threshold=5):
    """Lists items with stock below the threshold"""
    try:
        threshold = int(threshold)
        low_stock = inventory_manager.get_low_stock_items(threshold)
        
        if not low_stock:
            return f"No items with stock below {threshold} units"
        
        low_text = f"LOW STOCK ITEMS (below {threshold} units):\n"
        for item in low_stock:
            stock = inventory_manager.get_stock_level(item)
            low_text += f"- {item.name}: {stock} units\n"
        
        return low_text
    
    except ValueError:
        return "Please enter a valid number for threshold"

# ----- GRADIO INTERFACE -----

with gr.Blocks(title="Restaurant POS System Demo") as app:
    gr.Markdown("# Restaurant POS System Demo")
    
    with gr.Tab("Order Management"):
        gr.Markdown("## Menu Management")
        
        with gr.Row():
            with gr.Column():
                view_menu_btn = gr.Button("View Menu")
                menu_output = gr.Textbox(label="Menu Items", lines=10)
                view_menu_btn.click(fn=view_menu, outputs=menu_output)
            
            with gr.Column():
                search_input = gr.Textbox(label="Search for Item")
                search_btn = gr.Button("Search")
                search_output = gr.Textbox(label="Search Results")
                search_btn.click(fn=search_item, inputs=search_input, outputs=search_output)
        
        gr.Markdown("## Cart Management")
        
        with gr.Row():
            with gr.Column():
                item_id_input = gr.Textbox(label="Item ID")
                quantity_input = gr.Number(label="Quantity", value=1, minimum=1, step=1)
                add_to_cart_btn = gr.Button("Add to Cart")
                add_result = gr.Textbox(label="Result")
                add_to_cart_btn.click(
                    fn=add_item_to_cart, 
                    inputs=[item_id_input, quantity_input],
                    outputs=add_result
                )
            
            with gr.Column():
                view_cart_btn = gr.Button("View Cart")
                clear_cart_btn = gr.Button("Clear Cart")
                cart_output = gr.Textbox(label="Cart Contents", lines=10)
                view_cart_btn.click(fn=view_cart, outputs=cart_output)
                clear_cart_btn.click(fn=clear_cart, outputs=cart_output)
    
    with gr.Tab("Billing & Receipts"):
        gr.Markdown("## Bill Calculation")
        
        with gr.Row():
            with gr.Column():
                discount_code_input = gr.Textbox(label="Discount Code (Optional)")
                calculate_bill_btn = gr.Button("Calculate Bill")
                bill_output = gr.Textbox(label="Bill Details", lines=6)
                calculate_bill_btn.click(fn=calculate_bill, inputs=discount_code_input, outputs=bill_output)
        
        gr.Markdown("## Receipt Generation")
        
        with gr.Row():
            with gr.Column():
                customer_name = gr.Textbox(label="Customer Name")
                customer_email = gr.Textbox(label="Customer Email")
                receipt_discount_code = gr.Textbox(label="Discount Code (Optional)")
                generate_receipt_btn = gr.Button("Generate Receipt")
                receipt_output = gr.Textbox(label="Receipt", lines=20)
                generate_receipt_btn.click(
                    fn=generate_receipt,
                    inputs=[customer_name, customer_email, receipt_discount_code],
                    outputs=receipt_output
                )
            
            with gr.Column():
                email_input = gr.Textbox(label="Email Address")
                send_btn = gr.Button("Send Receipt")
                email_output = gr.Textbox(label="Email Status")
                send_btn.click(fn=send_receipt_by_email, inputs=[receipt_output, email_input], outputs=email_output)
    
    with gr.Tab("Inventory Tracking"):
        gr.Markdown("## Inventory Management")
        
        with gr.Row():
            with gr.Column():
                view_inventory_btn = gr.Button("View Inventory")
                inventory_output = gr.Textbox(label="Inventory Status", lines=10)
                view_inventory_btn.click(fn=view_inventory, outputs=inventory_output)
            
            with gr.Column():
                update_item_id = gr.Textbox(label="Item ID")
                update_quantity = gr.Number(label="New Quantity", value=10, minimum=0, step=1)
                update_btn = gr.Button("Update Stock")
                update_output = gr.Textbox(label="Update Result")
                update_btn.click(fn=update_item_stock, inputs=[update_item_id, update_quantity], outputs=update_output)
        
        gr.Markdown("## Stock Reports")
        
        with gr.Row():
            with gr.Column():
                out_of_stock_btn = gr.Button("List Out-of-Stock Items")
                out_of_stock_output = gr.Textbox(label="Out-of-Stock Items", lines=5)
                out_of_stock_btn.click(fn=list_out_of_stock, outputs=out_of_stock_output)
            
            with gr.Column():
                threshold_input = gr.Number(label="Threshold", value=5, minimum=1, step=1)
                low_stock_btn = gr.Button("List Low-Stock Items")
                low_stock_output = gr.Textbox(label="Low-Stock Items", lines=5)
                low_stock_btn.click(fn=list_low_stock, inputs=threshold_input, outputs=low_stock_output)

if __name__ == "__main__":
    app.launch()