-- store-schema.sql
CREATE DATABASE IF NOT EXISTS store;
USE store;

CREATE TABLE IF NOT EXISTS products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(255),
  price DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL DEFAULT 0,
  image_key VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sales (
  sale_id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT,
  buyer_name VARCHAR(100),
  buyer_email VARCHAR(100),
  quantity INT,
  sale_date DATETIME,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert 6 sample products (change image_key to your S3 keys)
INSERT IGNORE INTO products (name, description, price, stock, image_key) VALUES
('Red Mug', 'Ceramic red mug', 9.99, 10, 'red-mug.jpeg'),
('Blue Shirt', 'Comfort tee', 19.99, 10, 'blue-shirt.jpeg'),
('Notepad', 'A5 lined notepad', 4.99, 10, 'notepad.jpeg'),
('Headphones', 'On-ear headphones', 29.99, 10, 'headphones.jpeg'),
('Water Bottle', '500ml bottle', 12.00, 10, 'bottle.jpeg'),
('Backpack', 'Daypack 20L', 39.99, 10, 'backpack.jpeg');


