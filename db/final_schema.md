# Overview

- This is the final schema design for the cleaned tables, this modeling uses **Star Schema** modelling

## dim_customers

- Gives a stable information about the customer

| Column                   |          Type |   Key  | Nullable | Description                                                 |
| ------------------------ | ------------: | :----: | :------: | ----------------------------------------------------------- |
| customer_id              |   VARCHAR(36) | **PK** |  **NO**  | Stable customer identifier (one row per real person)        |
| customer_unqiue_id       |   VARCHAR(32) |        |    NO    | Platform snapshot id (one snapshot per customer-row in raw) |
| customer_city            |  VARCHAR(100) |        |    YES   | City name                                                   |
| customer_state           |    VARCHAR(8) |        |    YES   | State / region code                                         |
| first_order_date         |          DATE |        |    YES   | Date of first order (DATE, no time)                         |
| last_order_date          |          DATE |        |    YES   | Date of most recent order (DATE)                            |
| num_orders               |       INTEGER |        |    NO    | Number of orders (default 0)                                |
| total_revenue            | NUMERIC(14,2) |        |    NO    | Lifetime revenue (currency — two decimals)                  |
| active                   |       BOOLEAN |        |    NO    | Is customer active (default FALSE)                          |

## dim_products

- Gives information about the products

| Column                | Type          | PK  | Nullable    | Description                   |
| --------------------- | ------------- | --- | ----------- | ----------------------------- |
| product_id            | VARCHAR(40)   | YES | NO          | Product primary key (hash id) |
| product_category_name | VARCHAR(30)   | NO  | NO          | Category (or 'unknown')       |
| product_weight_g      | INTEGER       | NO  | YES         | Weight in grams               |
| product_length_cm     | NUMERIC(10,2) | NO  | YES         | Length in cm                  |
| product_height_cm     | NUMERIC(10,2) | NO  | YES         | Height in cm                  |
| product_width_cm      | NUMERIC(10,2) | NO  | YES         | Width in cm                   |
| product_volume_cm3    | NUMERIC(10,2) | NO  | YES         | Derived volume in cm³         |

## dim_orders

- Gives information about the orders

| Column                        | Type          | PK  | Nullable | Description                              |
| ----------------------------- | ------------- | --- | -------- | ---------------------------------------- |
| order_id                      | VARCHAR(32)   | YES | NO       | Order identifier                         |
| customer_unique_id            | VARCHAR(36)   | FK  | NO       | FK → dim_customers(customer_unique_id)   |
| order_status                  | VARCHAR(20)   |     | NO*      | Order status (delivered, shipped, etc.)  |
| order_purchase_timestamp      | TIMESTAMP     |     | NO       | When order was created                   |
| order_approved_at             | TIMESTAMP     |     | YES      | When order was approved (nullable)       |
| order_delivered_customer_date | TIMESTAMP     |     | YES      | When order was delivered (nullable)      |
| delayed_days                  | INTEGER       |     | YES      | Delivery delay in days (can be negative) |
| order_total                   | NUMERIC(14,2) |     | YES      | Total revenue for this order             |
| total_freight                 | NUMERIC(10,2) |     | YES      | Total freight for this order             |
| num_items                     | INTEGER       |     | NO       | Number of items in the order (default 0) |

## fact_order_items

- It is the master table

| Column        | Type          | PK (composite) | Nullable | Description                        |
| ------------- | ------------- | -------------- | -------- | ---------------------------------- |
| order_id      | VARCHAR(32)   | YES            | NO       | Order identifier (FK → dim_orders) |
| order_item_id | INTEGER       | YES            | NO       | Item number within the order       |
| product_id    | VARCHAR(40)*  | NO (FK)        | NO       | Product identifier                 |
| seller_id     | VARCHAR(32)   | NO             | YES      | Seller id                          |
| price         | NUMERIC(10,2) | NO             | **NO**   | Unit price                         |
| freight_value | NUMERIC(10,2) | NO             | **NO**   | Freight value                      |
