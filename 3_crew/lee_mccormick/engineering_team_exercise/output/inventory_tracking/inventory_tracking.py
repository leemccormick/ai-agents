from typing import List, Dict, Optional

class MenuItem:
    def __init__(self, item_id: str, name: str, description: str, price: float):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.price = price

class InventoryManager:
    """Track the availability of menu items and manage stock levels accordingly."""
    
    def __init__(self):
        # Initialize with empty inventory
        # Dictionary maps item_id to current stock quantity
        self.inventory: Dict[str, int] = {}
        # Keep a reference to menu items for easy access
        self.menu_items: Dict[str, MenuItem] = {}
    
    def add_menu_item(self, item: MenuItem, initial_stock: int = 0) -> None:
        """Adds a new menu item to the inventory tracking system."""
        if item.item_id in self.inventory:
            raise ValueError(f"Item with ID {item.item_id} already exists in inventory")
        
        self.inventory[item.item_id] = initial_stock
        self.menu_items[item.item_id] = item
    
    def check_stock(self, item: MenuItem) -> bool:
        """Checks if an item is in stock and returns True or False."""
        if item.item_id not in self.inventory:
            raise ValueError(f"Item with ID {item.item_id} not found in inventory")
        
        return self.inventory[item.item_id] > 0
    
    def update_stock_level(self, item: MenuItem, new_quantity: int) -> None:
        """Updates the stock level for a given item."""
        if item.item_id not in self.inventory:
            raise ValueError(f"Item with ID {item.item_id} not found in inventory")
        
        if new_quantity < 0:
            raise ValueError("Stock level cannot be negative")
        
        self.inventory[item.item_id] = new_quantity
    
    def get_out_of_stock_items(self) -> List[MenuItem]:
        """Returns a list of items that are currently out of stock."""
        out_of_stock = []
        
        for item_id, quantity in self.inventory.items():
            if quantity == 0:
                out_of_stock.append(self.menu_items[item_id])
        
        return out_of_stock
    
    def get_stock_level(self, item: MenuItem) -> int:
        """Gets the current stock level for a given item."""
        if item.item_id not in self.inventory:
            raise ValueError(f"Item with ID {item.item_id} not found in inventory")
        
        return self.inventory[item.item_id]
    
    def decrease_stock(self, item: MenuItem, quantity: int = 1) -> bool:
        """Decreases the stock level when items are sold.
        Returns True if successful, False if insufficient stock."""
        if item.item_id not in self.inventory:
            raise ValueError(f"Item with ID {item.item_id} not found in inventory")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        current_stock = self.inventory[item.item_id]
        
        if current_stock < quantity:
            return False  # Not enough stock
        
        self.inventory[item.item_id] = current_stock - quantity
        return True
    
    def increase_stock(self, item: MenuItem, quantity: int = 1) -> None:
        """Increases the stock level when items are restocked."""
        if item.item_id not in self.inventory:
            raise ValueError(f"Item with ID {item.item_id} not found in inventory")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        self.inventory[item.item_id] += quantity
    
    def get_low_stock_items(self, threshold: int = 5) -> List[MenuItem]:
        """Returns a list of items with stock level below the specified threshold."""
        low_stock = []
        
        for item_id, quantity in self.inventory.items():
            if 0 < quantity < threshold:
                low_stock.append(self.menu_items[item_id])
        
        return low_stock
