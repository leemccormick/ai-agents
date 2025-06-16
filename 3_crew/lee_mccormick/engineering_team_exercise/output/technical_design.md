# Technical Design Document

## Module: order_management

### Class: MenuManager
- **Responsibility**: Manage and maintain the digital menu, providing facilities to view and search for menu items.
- **Methods**:
  - `view_menu(self) -> List[MenuItem]`: Returns the list of all menu items.
  - `search_item(self, item_name: str) -> Optional[MenuItem]`: Searches for an item by name and returns the `MenuItem` if found, otherwise `None`.

### Class: CartManager
- **Responsibility**: Handle operations related to adding items to a customer's cart and managing cart contents.
- **Methods**:
  - `add_to_cart(self, item: MenuItem, quantity: int) -> None`: Adds a specified quantity of an item to the cart.
  - `remove_from_cart(self, item: MenuItem) -> None`: Removes an item from the cart.
  - `get_cart_items(self) -> List[CartItem]`: Returns a list of all items currently in the cart.

---

## Module: billing_and_receipts

### Class: BillingProcessor
- **Responsibility**: Calculate order totals including taxes and apply discounts.
- **Methods**:
  - `calculate_subtotal(self, cart_items: List[CartItem]) -> float`: Calculates and returns the subtotal of the order.
  - `apply_discount(self, code: str) -> float`: Applies a discount to the current order and returns the discount amount.

### Class: ReceiptGenerator
- **Responsibility**: Generate digital or printable receipts for customers based on their orders.
- **Methods**:
  - `generate_receipt(self, order_details: OrderDetails) -> str`: Generates a textual receipt and returns it.
  - `send_receipt_via_email(self, email: str, receipt: str) -> None`: Sends the generated receipt to a customer's email.

---

## Module: inventory_tracking

### Class: InventoryManager
- **Responsibility**: Track the availability of menu items and manage stock levels accordingly.
- **Methods**:
  - `check_stock(self, item: MenuItem) -> bool`: Checks if an item is in stock and returns `True` or `False`.
  - `update_stock_level(self, item: MenuItem, new_quantity: int) -> None`: Updates the stock level for a given item.
  - `get_out_of_stock_items(self) -> List[MenuItem]`: Returns a list of items that are currently out of stock.