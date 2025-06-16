from typing import List, Optional

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

class MenuManager:
    """Manage and maintain the digital menu, providing facilities to view and search for menu items."""
    
    def __init__(self):
        # Initialize with an empty menu list - in a real implementation, this would be loaded from a database
        self.menu_items: List[MenuItem] = []
    
    def view_menu(self) -> List[MenuItem]:
        """Returns the list of all menu items."""
        return self.menu_items
    
    def search_item(self, item_name: str) -> Optional[MenuItem]:
        """Searches for an item by name and returns the MenuItem if found, otherwise None."""
        item_name = item_name.lower()  # Case-insensitive search
        
        for item in self.menu_items:
            if item.name.lower() == item_name:
                return item
        
        return None

class CartManager:
    """Handle operations related to adding items to a customer's cart and managing cart contents."""
    
    def __init__(self):
        # Initialize with an empty cart
        self.cart_items: List[CartItem] = []
    
    def add_to_cart(self, item: MenuItem, quantity: int) -> None:
        """Adds a specified quantity of an item to the cart."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        # Check if the item is already in the cart
        for cart_item in self.cart_items:
            if cart_item.menu_item.item_id == item.item_id:
                # Update existing cart item quantity
                cart_item.quantity += quantity
                return
        
        # Item not in cart, add a new cart item
        self.cart_items.append(CartItem(item, quantity))
    
    def remove_from_cart(self, item: MenuItem) -> None:
        """Removes an item from the cart."""
        for i, cart_item in enumerate(self.cart_items):
            if cart_item.menu_item.item_id == item.item_id:
                del self.cart_items[i]
                return
        
        # If we reach here, the item was not in the cart
        raise ValueError(f"Item {item.name} not found in cart")
    
    def get_cart_items(self) -> List[CartItem]:
        """Returns a list of all items currently in the cart."""
        return self.cart_items
