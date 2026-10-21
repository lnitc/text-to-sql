"""
BigQuery schema definitions for the thelook_ecommerce public dataset.

This module contains the hardcoded schema for the tables we'll be querying.
In production, this could be fetched dynamically from BigQuery.

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
            "name": "category",
            "type": "STRING",
            "description": "Product category",
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
            "name": "cost",
            "type": "FLOAT64",
            "description": "Cost to produce",
        },
        {
            "name": "distribution_centers",
            "type": "STRING",
            "description": "Distribution center codes",
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
            "description": "Order ID (foreign key)",
        },
        {
            "name": "product_id",
            "type": "INTEGER",
            "description": "Product ID (foreign key to products)",
        },
        {
            "name": "inventory_item_id",
            "type": "INTEGER",
            "description": "Inventory item ID",
        },
        {
            "name": "user_id",
            "type": "INTEGER",
            "description": "User ID (customer)",
        },
        {
            "name": "sale_price",
            "type": "FLOAT64",
            "description": "Sale price in USD",
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
            "name": "status",
            "type": "STRING",
            "description": "Order item status (Pending, Processing, Shipped, Delivered, Returned, Cancelled)",
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
            "description": "User ID (customer)",
        },
        {
            "name": "status",
            "type": "STRING",
            "description": "Order status",
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
            "name": "city",
            "type": "STRING",
            "description": "City",
        },
        {
            "name": "state",
            "type": "STRING",
            "description": "State",
        },
        {
            "name": "postal_code",
            "type": "STRING",
            "description": "Postal code",
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
            "name": "gender",
            "type": "STRING",
            "description": "Gender",
        },
        {
            "name": "birth_date",
            "type": "DATE",
            "description": "Birth date",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "description": "When user account was created",
        },
        {
            "name": "updated_at",
            "type": "TIMESTAMP",
            "description": "When user profile was last updated",
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
