"""
BigQuery schema definitions for the thelook_ecommerce public dataset.

This module contains the hardcoded schema for the tables we'll be querying.
Field names were verified against the live dataset metadata; keep them in sync
if the dataset changes. In production, this could be fetched dynamically.

Reference: https://console.cloud.google.com/bigquery?project=bigquery-public-data&d=thelook_ecommerce
"""

# Schema for bigquery-public-data.thelook_ecommerce.products
PRODUCTS_SCHEMA = {
    "table": "products",
    "dataset": "thelook_ecommerce",
    "project": "bigquery-public-data",
    "fields": [
        {
            "name": "id",
            "type": "INTEGER",
            "description": "Product ID (primary key)",
        },
        {
            "name": "cost",
            "type": "FLOAT64",
            "description": "Cost to produce in USD",
        },
        {
            "name": "category",
            "type": "STRING",
            "description": "Product category (e.g. Jeans, Tops & Tees, Accessories)",
        },
        {
            "name": "name",
            "type": "STRING",
            "description": "Product name",
        },
        {
            "name": "brand",
            "type": "STRING",
            "description": "Product brand",
        },
        {
            "name": "retail_price",
            "type": "FLOAT64",
            "description": "Retail price in USD",
        },
        {
            "name": "department",
            "type": "STRING",
            "description": "Department: 'Men' or 'Women'",
        },
        {
            "name": "sku",
            "type": "STRING",
            "description": "Stock keeping unit",
        },
        {
            "name": "distribution_center_id",
            "type": "INTEGER",
            "description": "Distribution center ID",
        },
    ],
}

# Schema for bigquery-public-data.thelook_ecommerce.order_items
ORDER_ITEMS_SCHEMA = {
    "table": "order_items",
    "dataset": "thelook_ecommerce",
    "project": "bigquery-public-data",
    "fields": [
        {
            "name": "id",
            "type": "INTEGER",
            "description": "Order item ID (primary key)",
        },
        {
            "name": "order_id",
            "type": "INTEGER",
            "description": "Order ID (foreign key to orders.order_id)",
        },
        {
            "name": "user_id",
            "type": "INTEGER",
            "description": "User ID (foreign key to users.id)",
        },
        {
            "name": "product_id",
            "type": "INTEGER",
            "description": "Product ID (foreign key to products.id)",
        },
        {
            "name": "inventory_item_id",
            "type": "INTEGER",
            "description": "Inventory item ID",
        },
        {
            "name": "status",
            "type": "STRING",
            "description": "Order status: 'Processing', 'Shipped', 'Complete', 'Returned' or 'Cancelled'",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "description": "When order item was created",
        },
        {
            "name": "shipped_at",
            "type": "TIMESTAMP",
            "description": "When order item was shipped",
        },
        {
            "name": "delivered_at",
            "type": "TIMESTAMP",
            "description": "When order item was delivered",
        },
        {
            "name": "returned_at",
            "type": "TIMESTAMP",
            "description": "When order item was returned (if applicable)",
        },
        {
            "name": "sale_price",
            "type": "FLOAT64",
            "description": "Sale price in USD (use SUM(sale_price) for revenue)",
        },
    ],
}

# Schema for bigquery-public-data.thelook_ecommerce.orders
ORDERS_SCHEMA = {
    "table": "orders",
    "dataset": "thelook_ecommerce",
    "project": "bigquery-public-data",
    "fields": [
        {
            "name": "order_id",
            "type": "INTEGER",
            "description": "Order ID (primary key)",
        },
        {
            "name": "user_id",
            "type": "INTEGER",
            "description": "User ID (foreign key to users.id)",
        },
        {
            "name": "status",
            "type": "STRING",
            "description": "Order status: 'Processing', 'Shipped', 'Complete', 'Returned' or 'Cancelled'",
        },
        {
            "name": "gender",
            "type": "STRING",
            "description": "Customer gender: 'M' or 'F'",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "description": "When order was created",
        },
        {
            "name": "returned_at",
            "type": "TIMESTAMP",
            "description": "When order was returned",
        },
        {
            "name": "shipped_at",
            "type": "TIMESTAMP",
            "description": "When order was shipped",
        },
        {
            "name": "delivered_at",
            "type": "TIMESTAMP",
            "description": "When order was delivered",
        },
        {
            "name": "num_of_item",
            "type": "INTEGER",
            "description": "Number of items in order",
        },
    ],
}

# Schema for bigquery-public-data.thelook_ecommerce.users
USERS_SCHEMA = {
    "table": "users",
    "dataset": "thelook_ecommerce",
    "project": "bigquery-public-data",
    "fields": [
        {
            "name": "id",
            "type": "INTEGER",
            "description": "User ID (primary key)",
        },
        {
            "name": "first_name",
            "type": "STRING",
            "description": "First name",
        },
        {
            "name": "last_name",
            "type": "STRING",
            "description": "Last name",
        },
        {
            "name": "email",
            "type": "STRING",
            "description": "Email address",
        },
        {
            "name": "age",
            "type": "INTEGER",
            "description": "Age in years",
        },
        {
            "name": "gender",
            "type": "STRING",
            "description": "Gender: 'M' or 'F'",
        },
        {
            "name": "state",
            "type": "STRING",
            "description": "State",
        },
        {
            "name": "street_address",
            "type": "STRING",
            "description": "Street address",
        },
        {
            "name": "postal_code",
            "type": "STRING",
            "description": "Postal code",
        },
        {
            "name": "city",
            "type": "STRING",
            "description": "City",
        },
        {
            "name": "country",
            "type": "STRING",
            "description": "Country",
        },
        {
            "name": "latitude",
            "type": "FLOAT64",
            "description": "Latitude",
        },
        {
            "name": "longitude",
            "type": "FLOAT64",
            "description": "Longitude",
        },
        {
            "name": "traffic_source",
            "type": "STRING",
            "description": "Acquisition channel (e.g. Search, Organic, Facebook, Email, Display)",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "description": "When user account was created",
        },
    ],
}

# Combined schema dict for easy lookup
SCHEMAS = {
    "products": PRODUCTS_SCHEMA,
    "order_items": ORDER_ITEMS_SCHEMA,
    "orders": ORDERS_SCHEMA,
    "users": USERS_SCHEMA,
}


def get_schema_for_table(table_name: str) -> dict | None:
    """
    Get schema definition for a table.
    
    Args:
        table_name: Table name (e.g., "products", "order_items")
    
    Returns:
        Schema dict or None if table not found
    """
    return SCHEMAS.get(table_name)


def get_all_schemas() -> dict:
    """Get all available schemas."""
    return SCHEMAS


def format_schema_for_agent(table_name: str) -> str:
    """
    Format schema as a string for the LLM agent.
    
    Args:
        table_name: Table name
    
    Returns:
        Formatted schema string
    
    Example:
        >>> print(format_schema_for_agent("products"))
        Table: bigquery-public-data.thelook_ecommerce.products
        Fields:
        - id (INTEGER): Product ID (primary key)
        - category (STRING): Product category
        ...
    """
    schema = get_schema_for_table(table_name)
    if not schema:
        return f"Table '{table_name}' not found in available schemas"
    
    lines = [
        f"Table: `{schema['project']}.{schema['dataset']}.{schema['table']}`",
        "Fields:",
    ]
    
    for field in schema["fields"]:
        lines.append(
            f"  - {field['name']} ({field['type']}): {field['description']}"
        )
    
    return "\n".join(lines)
