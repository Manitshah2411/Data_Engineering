# Tables

- Customers
- Orders
- Products
- Order_Items

---

## Table 1: Customers (Logical Schema)

### Raw Columns (customers)

- customer_id (PK)
- customer_unique_id
- customer_zip_code_prefix
- customer_city
- customer_state

### Relationships (customers)

- customer → ONE TO MANY → orders

---

## Table 2: Products (Logical Schema)

### Raw Columns (products)

- product_id (PK)
- product_category_name
- product_name_lenght
- product_description_lenght
- product_photos_qty
- product_weight_g
- product_length_cm
- product_height_cm
- product_width_cm

### Relationships (products)

- product → ONE TO MANY → order_items

---

## Table 3: Orders (Logical Schema)

### Raw Columns (Orders)

- order_id (PK)
- customer_id (FK → customers.customer_id)
- order_status
- order_purchase_timestamp
- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date
- order_estimated_delivery_date

### Relationships (Orders)

- orders → MANY TO ONE → customers
- orders → ONE TO MANY → order_items

---

## Table 4: Order_Items (Logical Schema)

### Raw Columns (Order_Items)

- order_item_id (PK)
- order_id (FK → orders.order_id)
- product_id (FK → products.product_id)
- seller_id
- shipping_limit_date
- price
- freight_value

### Relationships (Order_items)

- order_items → MANY TO ONE → orders
- order_items → MANY TO ONE → products
