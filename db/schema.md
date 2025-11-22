# Tables

    Customer
    Orders
    Products
    Order_items

## Table 1 : Customer

    customer_id:    unique identifier
    first_name:     firstname of the customer
    last_name:      lastname of the customer
    email:          email of the customer
    age:            age of the customer
    country:        customer's country
    active:         Is the customer active or not
    created_on:     customer signed up on

### Relationships (Customer)

    customer -> ONE TO MANY (orders)

## Table 2 : Products

    product_id:     unique identifier
    name:           name of the product
    category:       product category
    brand:          product's brand

### Relationships (Products)

    product -> ONE TO MANY (order_items)

## Table 3 : Orders

    order_id:       unique identifier
    customer_id:    (Foreign key, References Customer(customer_id))
    order_date:     Order placed on
    ship_date:      Shipped on
    delivery_date:  Delivered on
    order_status:   Current stage of the order

### Relationships (Orders)

    orders -> ONE TO MANY (order_items)
    
## Table 4 : Order_items

    order_item_id: unique identifier
    order_id : (Foreign Key, References Orders(order_id))
    product_id : (Foreign Key, References Products(product_id))
    quantity: Quantity of the unit
    unit_price: Price of the unit
    sale : quantity * unit_price
