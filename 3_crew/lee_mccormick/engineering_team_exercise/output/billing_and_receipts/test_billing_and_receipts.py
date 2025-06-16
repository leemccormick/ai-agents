import unittest
from datetime import datetime
from unittest.mock import patch
from billing_and_receipts import MenuItem, CartItem, OrderDetails, BillingProcessor, ReceiptGenerator

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

class TestOrderDetails(unittest.TestCase):
    def setUp(self):
        menu_item = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        cart_item = CartItem(menu_item, 2)
        self.order_details = OrderDetails(
            order_id="ORD123",
            cart_items=[cart_item],
            customer_name="John Doe",
            customer_email="john@example.com",
            subtotal=19.98,
            tax=1.60,
            discount=0.0,
            total=21.58
        )
    
    def test_init(self):
        self.assertEqual(self.order_details.order_id, "ORD123")
        self.assertEqual(len(self.order_details.cart_items), 1)
        self.assertEqual(self.order_details.customer_name, "John Doe")
        self.assertEqual(self.order_details.customer_email, "john@example.com")
        self.assertEqual(self.order_details.subtotal, 19.98)
        self.assertEqual(self.order_details.tax, 1.60)
        self.assertEqual(self.order_details.discount, 0.0)
        self.assertEqual(self.order_details.total, 21.58)
        self.assertIsInstance(self.order_details.timestamp, datetime)

class TestBillingProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = BillingProcessor(tax_rate=0.08)
        self.burger = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        self.pizza = MenuItem("456", "Pizza", "Cheese pizza", 12.99)
        self.cart_items = [
            CartItem(self.burger, 2),
            CartItem(self.pizza, 1)
        ]
    
    def test_init(self):
        self.assertEqual(self.processor.tax_rate, 0.08)
        self.assertIn("WELCOME10", self.processor.discount_codes)
        self.assertEqual(self.processor.current_subtotal, 0.0)
    
    def test_calculate_subtotal(self):
        subtotal = self.processor.calculate_subtotal(self.cart_items)
        expected = (9.99 * 2) + (12.99 * 1)
        self.assertAlmostEqual(subtotal, expected, places=2)
        self.assertAlmostEqual(self.processor.current_subtotal, expected, places=2)
    
    def test_apply_discount_percentage(self):
        self.processor.calculate_subtotal(self.cart_items)
        discount = self.processor.apply_discount("WELCOME10")
        expected_discount = self.processor.current_subtotal * 0.10
        self.assertAlmostEqual(discount, expected_discount, places=2)
    
    def test_apply_discount_fixed_amount(self):
        self.processor.calculate_subtotal(self.cart_items)
        discount = self.processor.apply_discount("FREESHIP")
        self.assertEqual(discount, 5.00)
    
    def test_apply_discount_case_insensitive(self):
        self.processor.calculate_subtotal(self.cart_items)
        discount = self.processor.apply_discount("welcome10")
        expected_discount = self.processor.current_subtotal * 0.10
        self.assertAlmostEqual(discount, expected_discount, places=2)
    
    def test_apply_discount_invalid_code(self):
        self.processor.calculate_subtotal(self.cart_items)
        discount = self.processor.apply_discount("INVALID")
        self.assertEqual(discount, 0.0)
    
    def test_apply_discount_without_subtotal(self):
        with self.assertRaises(ValueError):
            self.processor.apply_discount("WELCOME10")

class TestReceiptGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ReceiptGenerator()
        burger = MenuItem("123", "Burger", "Juicy beef burger", 9.99)
        pizza = MenuItem("456", "Pizza", "Cheese pizza", 12.99)
        cart_items = [
            CartItem(burger, 2),
            CartItem(pizza, 1)
        ]
        self.order_details = OrderDetails(
            order_id="ORD123",
            cart_items=cart_items,
            customer_name="John Doe",
            customer_email="john@example.com",
            subtotal=32.97,
            tax=2.64,
            discount=3.30,
            total=32.31
        )
    
    def test_generate_receipt(self):
        receipt = self.generator.generate_receipt(self.order_details)
        # Check that the receipt contains key information
        self.assertIn("ORDER RECEIPT", receipt)
        self.assertIn("Order ID: ORD123", receipt)
        self.assertIn("Customer: John Doe", receipt)
        self.assertIn("Burger", receipt)
        self.assertIn("Pizza", receipt)
        self.assertIn("Subtotal: $32.97", receipt)
        self.assertIn("Tax: $2.64", receipt)
        self.assertIn("Discount: -$3.30", receipt)
        self.assertIn("Total: $32.31", receipt)
    
    @patch('builtins.print')
    def test_send_receipt_via_email(self, mock_print):
        receipt = self.generator.generate_receipt(self.order_details)
        self.generator.send_receipt_via_email("john@example.com", receipt)
        mock_print.assert_called_once_with("Receipt sent to john@example.com")

if __name__ == "__main__":
    unittest.main()
