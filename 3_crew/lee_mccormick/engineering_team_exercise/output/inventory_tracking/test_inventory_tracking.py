import unittest
from inventory_tracking import MenuItem, InventoryManager

class TestMenuItem(unittest.TestCase):
    def setUp(self):
        self.item = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
    
    def test_init(self):
        self.assertEqual(self.item.item_id, "123")
        self.assertEqual(self.item.name, "Burger")
        self.assertEqual(self.item.description, "Juicy beef burger")
        self.assertEqual(self.item.price, 9.99)

class TestInventoryManager(unittest.TestCase):
    def setUp(self):
        self.inventory_manager = InventoryManager()
        self.burger = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        self.pizza = MenuItem("456", "Pizza", "Cheese pizza", 12.99)
        self.salad = MenuItem("789", "Salad", "Fresh garden salad", 7.99)
    
    def test_add_menu_item(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.assertEqual(self.inventory_manager.inventory["123"], 10)
        self.assertEqual(self.inventory_manager.menu_items["123"], self.burger)
    
    def test_add_menu_item_default_stock(self):
        self.inventory_manager.add_menu_item(self.burger)
        self.assertEqual(self.inventory_manager.inventory["123"], 0)
    
    def test_add_menu_item_duplicate(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        with self.assertRaises(ValueError):
            self.inventory_manager.add_menu_item(self.burger, 5)
    
    def test_check_stock_in_stock(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.assertTrue(self.inventory_manager.check_stock(self.burger))
    
    def test_check_stock_out_of_stock(self):
        self.inventory_manager.add_menu_item(self.burger, 0)
        self.assertFalse(self.inventory_manager.check_stock(self.burger))
    
    def test_check_stock_not_in_inventory(self):
        with self.assertRaises(ValueError):
            self.inventory_manager.check_stock(self.burger)
    
    def test_update_stock_level(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.inventory_manager.update_stock_level(self.burger, 15)
        self.assertEqual(self.inventory_manager.inventory["123"], 15)
    
    def test_update_stock_level_to_zero(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.inventory_manager.update_stock_level(self.burger, 0)
        self.assertEqual(self.inventory_manager.inventory["123"], 0)
    
    def test_update_stock_level_negative(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        with self.assertRaises(ValueError):
            self.inventory_manager.update_stock_level(self.burger, -1)
    
    def test_update_stock_level_not_in_inventory(self):
        with self.assertRaises(ValueError):
            self.inventory_manager.update_stock_level(self.burger, 5)
    
    def test_get_out_of_stock_items(self):
        self.inventory_manager.add_menu_item(self.burger, 0)
        self.inventory_manager.add_menu_item(self.pizza, 5)
        self.inventory_manager.add_menu_item(self.salad, 0)
        out_of_stock = self.inventory_manager.get_out_of_stock_items()
        self.assertEqual(len(out_of_stock), 2)
        self.assertIn(self.burger, out_of_stock)
        self.assertIn(self.salad, out_of_stock)
        self.assertNotIn(self.pizza, out_of_stock)
    
    def test_get_stock_level(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.assertEqual(self.inventory_manager.get_stock_level(self.burger), 10)
    
    def test_get_stock_level_not_in_inventory(self):
        with self.assertRaises(ValueError):
            self.inventory_manager.get_stock_level(self.burger)
    
    def test_decrease_stock_success(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        result = self.inventory_manager.decrease_stock(self.burger, 3)
        self.assertTrue(result)
        self.assertEqual(self.inventory_manager.inventory["123"], 7)
    
    def test_decrease_stock_insufficient(self):
        self.inventory_manager.add_menu_item(self.burger, 2)
        result = self.inventory_manager.decrease_stock(self.burger, 3)
        self.assertFalse(result)
        self.assertEqual(self.inventory_manager.inventory["123"], 2)  # Stock shouldn't change
    
    def test_decrease_stock_default_quantity(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.inventory_manager.decrease_stock(self.burger)  # Default quantity is 1
        self.assertEqual(self.inventory_manager.inventory["123"], 9)
    
    def test_decrease_stock_invalid_quantity(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        with self.assertRaises(ValueError):
            self.inventory_manager.decrease_stock(self.burger, 0)
        with self.assertRaises(ValueError):
            self.inventory_manager.decrease_stock(self.burger, -1)
    
    def test_decrease_stock_not_in_inventory(self):
        with self.assertRaises(ValueError):
            self.inventory_manager.decrease_stock(self.burger, 1)
    
    def test_increase_stock(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.inventory_manager.increase_stock(self.burger, 5)
        self.assertEqual(self.inventory_manager.inventory["123"], 15)
    
    def test_increase_stock_default_quantity(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        self.inventory_manager.increase_stock(self.burger)  # Default quantity is 1
        self.assertEqual(self.inventory_manager.inventory["123"], 11)
    
    def test_increase_stock_invalid_quantity(self):
        self.inventory_manager.add_menu_item(self.burger, 10)
        with self.assertRaises(ValueError):
            self.inventory_manager.increase_stock(self.burger, 0)
        with self.assertRaises(ValueError):
            self.inventory_manager.increase_stock(self.burger, -1)
    
    def test_increase_stock_not_in_inventory(self):
        with self.assertRaises(ValueError):
            self.inventory_manager.increase_stock(self.burger, 5)
    
    def test_get_low_stock_items(self):
        self.inventory_manager.add_menu_item(self.burger, 3)
        self.inventory_manager.add_menu_item(self.pizza, 10)
        self.inventory_manager.add_menu_item(self.salad, 0)
        low_stock = self.inventory_manager.get_low_stock_items(threshold=5)
        self.assertEqual(len(low_stock), 1)
        self.assertIn(self.burger, low_stock)
        self.assertNotIn(self.pizza, low_stock)  # Above threshold
        self.assertNotIn(self.salad, low_stock)  # Zero stock (out of stock, not low stock)
    
    def test_get_low_stock_items_custom_threshold(self):
        self.inventory_manager.add_menu_item(self.burger, 3)
        self.inventory_manager.add_menu_item(self.pizza, 7)
        low_stock = self.inventory_manager.get_low_stock_items(threshold=8)
        self.assertEqual(len(low_stock), 2)
        self.assertIn(self.burger, low_stock)
        self.assertIn(self.pizza, low_stock)

if __name__ == "__main__":
    unittest.main()
