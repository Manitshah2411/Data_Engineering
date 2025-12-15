
DROP TABLE IF EXISTS warehouse.dim_customers;
CREATE TABLE IF NOT EXISTS warehouse.dim_customers (
    customer_unique_id VARCHAR(32) NOT NULL,
    customer_id VARCHAR(36),
    customer_city VARCHAR(60),
    customer_state CHAR(2),
    first_order_date DATE,
    last_order_date DATE,
    num_orders INTEGER NOT NULL,
    total_revenue NUMERIC(14,2) NOT NULL,
    active BOOLEAN NOT NULL,

    CONSTRAINT pk_dim_customers PRIMARY KEY (customer_unique_id)
);


SELECT COUNT(*) FROM warehouse.dim_customers;