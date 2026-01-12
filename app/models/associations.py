"""Association tables for many-to-many relationships."""
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base


# Association table for customers and categories (many-to-many)
customer_categories = Table(
    'customer_categories',
    Base.metadata,
    Column('customer_id', Integer, ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


# Association table for customers and groups (many-to-many)
customer_groups = Table(
    'customer_groups',
    Base.metadata,
    Column('customer_id', Integer, ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
)
