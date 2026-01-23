"""Customer management module"""
import json
import os

class CustomerManager:
    def __init__(self, file_path="customers.json"):
        self.file_path = file_path
        self.customers = []
        self.load_customers()

    def load_customers(self):
        """Load customers from JSON file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.customers = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.customers = []
        else:
            self.customers = []

    def save_customers(self):
        """Save customers to JSON file"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.customers, f, indent=2)

    def add_customer(self, name):
        """Add a new customer"""
        if name.strip() and name not in self.customers:
            self.customers.append(name)
            self.save_customers()
            return True
        return False

    def remove_customer(self, name):
        """Remove a customer"""
        if name in self.customers:
            self.customers.remove(name)
            self.save_customers()
            return True
        return False

    def edit_customer(self, old_name, new_name):
        """Edit a customer's name"""
        if old_name in self.customers and new_name.strip():
            index = self.customers.index(old_name)
            self.customers[index] = new_name
            self.save_customers()
            return True
        return False

    def get_customers(self):
        """Get all customers"""
        return sorted(self.customers)
