"""
MUC Database Dashboard
Author: Mohammad Zaid Khan
Description: A Flask web application to manage and view database content for parts, suppliers, and orders.
"""
from flask import Flask, request, jsonify, send_from_directory
import pymysql
import pymysql.cursors
import math
from datetime import datetime

app = Flask(__name__, static_folder='.')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'u63',
    'password': 'anythingPRESIDENTSdeveloped738',
    'db': 'u63',
}

def get_db_connection():
    try:
        return pymysql.connect(connect_timeout=5, cursorclass=pymysql.cursors.DictCursor, **DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/styles.css')
def serve_css():
    return send_from_directory(app.static_folder, 'styles.css')

@app.route('/main.js')
def serve_js():
    return send_from_directory(app.static_folder, 'main.js')

@app.route('/data')
def get_table_data():
    table = request.args.get('table')
    valid_tables = ['Suppliers', 'parts', 'Orders', 'Supplier_Phone_Numbers']
    
    if not table:
        return jsonify({'message': 'Table name is required'}), 400
    
    if table.lower() not in [t.lower() for t in valid_tables]:
        return jsonify({'message': f'Invalid table name. Must be one of: {", ".join(valid_tables)}'}), 400
    
    for valid_table in valid_tables:
        if valid_table.lower() == table.lower():
            table = valid_table
            break
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {table}')
            results = cursor.fetchall()
        conn.close()
        
        if not results:
            return jsonify([])
            
        return jsonify(results)
    except pymysql.err.OperationalError as e:
        return jsonify({'message': f'Database connection error: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500

@app.route('/add-supplier', methods=['POST'])
def add_supplier():
    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 415
        
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone_string = data.get('phone', '').strip()
    
    if not name:
        return jsonify({'message': 'Supplier name is required'}), 400
    
    if email and '@' not in email:
        return jsonify({'message': 'Invalid email format'}), 400
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT MAX(supplier_id) as max_id FROM Suppliers')
            result = cursor.fetchone()
            next_id = 1 if not result or result['max_id'] is None else result['max_id'] + 1
            
            cursor.execute('INSERT INTO Suppliers (supplier_id, name, email) VALUES (%s, %s, %s)', 
                          (next_id, name, email))
            
            if phone_string:
                phone_numbers = [p.strip() for p in phone_string.split(',') if p.strip()]
                
                for phone in phone_numbers:
                    cursor.execute('INSERT INTO Supplier_Phone_Numbers (supplier_id, phone_number) VALUES (%s, %s)',
                                  (next_id, phone))
            
            conn.commit()
        conn.close()
        return jsonify({'message': 'Supplier added successfully', 'id': next_id})
    except pymysql.err.OperationalError as e:
        return jsonify({'message': f'Database connection error: {str(e)}'}), 503
    except pymysql.err.IntegrityError as e:
        return jsonify({'message': f'Database integrity error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'message': f'Failed to add supplier: {str(e)}'}), 500

@app.route('/expenses')
def get_expenses():
    try:
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
        
        if start > end:
            return jsonify({'message': 'Start year must be less than or equal to end year'}), 400
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid year range'}), 400
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = """
                SELECT YEAR(order_date) as year, SUM(p.price * o.quantity) as total
                FROM Orders o
                JOIN parts p ON o.part_id = p._id
                WHERE YEAR(order_date) >= %s AND YEAR(order_date) <= %s
                GROUP BY YEAR(order_date)
            """
            cursor.execute(query, (start, end))
            results = cursor.fetchall()
        conn.close()
        
        yearly_expenses = {}
        for row in results:
            yearly_expenses[str(row['year'])] = float(row['total'])
        
        return jsonify(yearly_expenses)
    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500

@app.route('/budget-projection')
def budget_projection():
    try:
        years = int(request.args.get('years'))
        rate = float(request.args.get('rate'))
        
        if years <= 0:
            return jsonify({'message': 'Number of years must be greater than zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid parameters'}), 400
    
    try:
        current_year = datetime.now().year
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = """
                SELECT SUM(p.price * o.quantity) as total
                FROM Orders o
                JOIN parts p ON o.part_id = p._id
                WHERE YEAR(order_date) = %s
            """
            cursor.execute(query, (current_year,))
            result = cursor.fetchone()
        conn.close()
        
        base_amount = float(result['total']) if result and result['total'] else 10000
        
        projections = {}
        for i in range(1, years + 1):
            year = current_year + i
            projected = base_amount * math.pow(1 + (rate/100), i)
            projections[str(year)] = projected
        
        return jsonify(projections)
    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
