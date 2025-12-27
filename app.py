from flask import Flask, jsonify, request
import mysql.connector
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging
import config
import sys

app = Flask(__name__)

# Log to journalctl
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


def get_connection():
    return mysql.connector.connect(
        host=config.RDS_ENDPOINT,
        user=config.DB_USER,
        password=config.DB_PASS,
        database=config.DB_NAME
    )

@app.route('/')
def health():
    return jsonify({"status":"OK"})

@app.route('/products')
def get_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route('/purchase', methods=['POST'])
def purchase():
    data = request.get_json()

    # Basic validation [required (name, email & items)]
    if not data or 'buyer_name' not in data or 'buyer_email' not in data or 'items' not in data:
        return jsonify({"success": False, "message": "Missing data fields (name, email, items)"}), 400

    buyer_name = data['buyer_name']
    buyer_email = data['buyer_email']
    items = data['items']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        total_price = 0.0
        order_details = []

        # Validate stock for all products first
        for item in items:
            pid = item['product_id']
            qty = item.get('quantity', 1)

            cursor.execute("SELECT name, price, stock FROM products WHERE product_id = %s", (pid,))
            product = cursor.fetchone()

            if not product: # Incorrect product NOT EXISTING IN DB
                raise Exception(f"Product ID {pid} not found.")
            if product['stock'] < qty: # Not enough stock
                raise Exception(f"Not enough stock for {product['name']}, (available: {product['stock']}, requested: {qty}).")

            # Calculate order summary
            subtotal = float(product['price']) * qty
            total_price += subtotal
            order_details.append({
                "id": pid,
                "name": product['name'],
                "qty": qty,
                "price": product['price'],
                "subtotal": subtotal
            })

        # All stock valid, proceed with update (reduce stock) and sales insert (register sales in sales table)
        for item in items:
            pid = item['product_id']
            qty = item.get('quantity', 1)
            cursor.execute("UPDATE products SET stock = stock - %s WHERE product_id = %s", (qty, pid))
            cursor.execute("""
                INSERT INTO sales (product_id, buyer_name, buyer_email, quantity, sale_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (pid, buyer_name, buyer_email, qty, datetime.now()))

        conn.commit()

        # Prepare email with all the products 
        order_lines = "".join([
            f"<tr><td>{d['name']}</td><td>{d['qty']}</td><td>${d['price']:.2f}</td><td>${d['subtotal']:.2f}</td></tr>"
            for d in order_details
        ])
        email_html = f"""
        <html>
        <body style="font-family:Arial, sans-serif;">
          <h2>Thank you for your purchase, {buyer_name}!</h2>
          <p>Here are your order details:</p>
          <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>Product</th><th>Quantity</th><th>Price</th><th>Subtotal</th></tr>
            {order_lines}
            <tr><td colspan="3" align="right"><b>Total:</b></td><td><b>${total_price:.2f}</b></td></tr>
          </table>
          <br/>
          <p>Your order will arrive within <b>5 business days</b>.</p>
          <p>For support, contact us at <b>+52 55 1234 5678</b>.</p>
          <p>Thank you for shopping with Mini Amazon!</p>
        </body>
        </html>
        """

        # Send email
        try:
            ses = boto3.client('ses', region_name=config.AWS_REGION)
            ses.send_email(
                Source=config.SES_SOURCE,
                Destination={'ToAddresses': [buyer_email]},
                Message={
                    'Subject': {'Data': 'Mini Amazon - Order Confirmation'},
                    'Body': {
                        'Html': {'Data': email_html},
                        'Text': {'Data': f"Thank you {buyer_name} for your order! Total: ${total_price:.2f}"}
                    }
                }
            )
            logging.info(f"Purchase email sent to {buyer_email}")
        except ClientError as e:
            logging.error(f"SES send_email failed: {e}")


        logging.info(f"Order successful for {buyer_name} ({buyer_email}), total ${total_price:.2f}")
        return jsonify({"success": True, "total": total_price})

    except Exception as e:
        conn.rollback()
        logging.error(f"Error processing order: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
