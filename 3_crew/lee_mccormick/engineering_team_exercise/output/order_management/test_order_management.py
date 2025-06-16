import unittest
from order_management import MenuItem, CartItem, MenuManager, CartManager

class TestMenuItem(unittest.TestCase):
    def setUp(self):
        self.item = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
    
    def test_init(self):
        self.assertEqual(self.item.item_id, "123")
        self.assertEqual(self.item.name, "Burger")
        self.assertEqual(self.item.description, "Juicy beef burger")
        self.assertEqual(self.item.price, 9.99)

class TestCartItem(unittest.TestCase):
    def setUp(self):
        self.menu_item = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        self.cart_item = CartItem(self.menu_item, 2)
    
    def test_init(self):
        self.assertEqual(self.cart_item.menu_item, self.menu_item)
        self.assertEqual(self.cart_item.quantity, 2)

class TestMenuManager(unittest.TestCase):
    def setUp(self):
        self.menu_manager = MenuManager()
        self.burger = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        self.pizza = MenuItem("456", "Pizza", "Cheese pizza", 12.99)
        self.menu_manager.menu_items = [self.burger, self.pizza]
    
    def test_view_menu(self):
        menu = self.menu_manager.view_menu()
        self.assertEqual(len(menu), 2)
        self.assertIn(self.burger, menu)
        self.assertIn(self.pizza, menu)
    
    def test_search_item_found(self):
        found_item = self.menu_manager.search_item("Burger")
        self.assertEqual(found_item, self.burger)
    
    def test_search_item_case_insensitive(self):
        found_item = self.menu_manager.search_item("burger")
        self.assertEqual(found_item, self.burger)
    
    def test_search_item_not_found(self):
        found_item = self.menu_manager.search_item("Salad")
        self.assertIsNone(found_item)

class TestCartManager(unittest.TestCase):
    def setUp(self):
        self.cart_manager = CartManager()
        self.burger = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        self.pizza = MenuItem("456", "Pizza", "Cheese pizza", 12.99)
    
    def test_add_to_cart_new_item(self):
        self.cart_manager.add_to_cart(self.burger, 2)
        cart_items = self.cart_manager.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].menu_item, self.burger)
        self.assertEqual(cart_items[0].quantity, 2)
    
    def test_add_to_cart_existing_item(self):
        self.cart_manager.add_to_cart(self.burger, 2)
        self.cart_manager.add_to_cart(self.burger, 1)
        cart_items = self.cart_manager.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].quantity, 3)
    
    def test_add_to_cart_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.cart_manager.add_to_cart(self.burger, 0)
        with self.assertRaises(ValueError):
            self.cart_manager.add_to_cart(self.burger, -1)
    
    def test_remove_from_cart(self):
        self.cart_manager.add_to_cart(self.burger, 2)
        self.cart_manager.add_to_cart(self.pizza, 1)
        self.cart_manager.remove_from_cart(self.burger)
        cart_items = self.cart_manager.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].menu_item, self.pizza)
    
    def test_remove_from_cart_not_in_cart(self):
        with self.assertRaises(ValueError):
            self.cart_manager.remove_from_cart(self.burger)
    
    def test_update_quantity(self):
        self.cart_manager.add_to_cart(self.burger, 2)
        self.cart_manager.update_quantity(self.burger, 5)
        cart_items = self.cart_manager.get_cart_items()
        self.assertEqual(cart_items[0].quantity, 5)
    
    def test_update_quantity_invalid(self):
        self.cart_manager.add_to_cart(self.burger, 2)
        with self.assertRaises(ValueError):
            self.cart_manager.update_quantity(self.burger, 0)
    
    def test_update_quantity_item_not_in_cart(self):
        with self.assertRaises(ValueError):
            self.cart_manager.update_quantity(self.burger, 3)
    
    def test_clear_cart(self):
        self.cart_manager.add_to_cart(self.burger, 2)
        self.cart_manager.add_to_cart(self.pizza, 1)
        self.cart_manager.clear_cart()
        self.assertEqual(len(self.cart_manager.get_cart_items()), 0)

if __name__ == "__main__":
    unittest.main()
