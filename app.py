from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('mis_project_regenerated.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()

    # Total penjualan keseluruhan
    total_sales = conn.execute('SELECT SUM(TotalSales) as total FROM Transactions').fetchone()['total']

    # Top 5 produk berdasarkan penjualan
    top_products = conn.execute('''
        SELECT p.ProductName, SUM(t.TotalSales) as total
        FROM Transactions t
        JOIN Products p ON t.ProductID = p.ProductID
        GROUP BY t.ProductID
        ORDER BY total DESC
        LIMIT 5
    ''').fetchall()

    # Total sales per store
    sales_per_store = conn.execute('''
        SELECT s.StoreName, SUM(t.TotalSales) as total
        FROM Transactions t
        JOIN Stores s ON t.StoreID = s.StoreID
        GROUP BY t.StoreID
        ORDER BY total DESC
    ''').fetchall()

    # Revenue trend per bulan (pakai kolom 'Date')
    monthly_revenue = conn.execute('''
        SELECT strftime('%Y-%m', Date) as month, SUM(TotalSales) as total
        FROM Transactions
        GROUP BY month
        ORDER BY month
    ''').fetchall()

    conn.close()

    return render_template(
        'sales.html',
        total_sales=total_sales,
        top_products=top_products,
        sales_per_store=sales_per_store,
        monthly_revenue=monthly_revenue
    )

@app.route('/customers')
def customer_dashboard():
    conn = get_db_connection()

    # Top 5 Pelanggan by Spend
    # Assuming 'Name' is the customer name column in your Customers table
    top_customers = conn.execute('''
        SELECT c.Name, SUM(t.TotalSales) AS total_spent
        FROM Transactions t
        JOIN Customers c ON t.CustomerID = c.CustomerID
        GROUP BY t.CustomerID
        ORDER BY total_spent DESC
        LIMIT 5
    ''').fetchall()

    # --- Metrics using your specified columns (Gender, Age, Region, LoyaltyStatus) ---

    # Customer Count by Gender
    customers_by_gender = conn.execute('''
        SELECT Gender, COUNT(*) AS count
        FROM Customers
        GROUP BY Gender
    ''').fetchall()

    # Customer Count by Age Group (example: 0-20, 21-40, 41-60, 61+)
    customers_by_age_group = conn.execute('''
        SELECT
            CASE
                WHEN Age BETWEEN 0 AND 20 THEN '0-20'
                WHEN Age BETWEEN 21 AND 40 THEN '21-40'
                WHEN Age BETWEEN 41 AND 60 THEN '41-60'
                ELSE '61+'
            END AS age_group,
            COUNT(*) AS count
        FROM Customers
        GROUP BY age_group
        ORDER BY age_group
    ''').fetchall()

    # Customer Count by Region
    customers_by_region = conn.execute('''
        SELECT Region, COUNT(*) AS count
        FROM Customers
        GROUP BY Region
        ORDER BY count DESC
    ''').fetchall()

    # Customer Count by Loyalty Status
    customers_by_loyalty = conn.execute('''
        SELECT LoyaltyStatus, COUNT(*) AS count
        FROM Customers
        GROUP BY LoyaltyStatus
        ORDER BY count DESC
    ''').fetchall()


    conn.close()
    return render_template('customers.html',
                           top_customers=top_customers,
                           customers_by_gender=customers_by_gender,
                           customers_by_age_group=customers_by_age_group,
                           customers_by_region=customers_by_region,
                           customers_by_loyalty=customers_by_loyalty)

# --- Product Dashboard Route ---
@app.route('/products')
def product_dashboard():
    conn = get_db_connection()

    # Total jumlah produk
    total_products = conn.execute('SELECT COUNT(*) as total FROM Products').fetchone()['total']

    # Jumlah produk per kategori
    products_by_category = conn.execute('''
        SELECT Category, COUNT(*) AS count
        FROM Products
        GROUP BY Category
        ORDER BY count DESC
    ''').fetchall()

    # Jumlah produk per pemasok (supplier)
    products_by_supplier = conn.execute('''
        SELECT Supplier, COUNT(*) AS count
        FROM Products
        GROUP BY Supplier
        ORDER BY count DESC
    ''').fetchall()

    # Produk di bawah level pemesanan ulang (reorder level)
    # This query is removed as per the request to remove "Produk di Bawah Level Pemesanan Ulang" from product.html
    # products_below_reorder = conn.execute('''
    #     SELECT ProductName, StockLevel, ReorderLevel
    #     FROM Products
    #     WHERE StockLevel <= ReorderLevel
    #     ORDER BY ProductName
    # ''').fetchall()

    # Rata-rata Unit Cost dan Unit Price
    avg_unit_cost = conn.execute('SELECT AVG(UnitCost) as avg_cost FROM Products').fetchone()['avg_cost']
    avg_unit_price = conn.execute('SELECT AVG(UnitPrice) as avg_price FROM Products').fetchone()['avg_price']

    conn.close()

    return render_template('products.html',
                           total_products=total_products,
                           products_by_category=products_by_category,
                           products_by_supplier=products_by_supplier,
                           # products_below_reorder=products_below_reorder, # Removed from context
                           avg_unit_cost=avg_unit_cost,
                           avg_unit_price=avg_unit_price)

# --- Employee Dashboard Route ---
@app.route('/employees')
def employee_dashboard():
    conn = get_db_connection()

    # Total karyawan
    total_employees = conn.execute('SELECT COUNT(*) as total FROM Employees').fetchone()['total']

    # Karyawan per peran (role)
    employees_by_role = conn.execute('''
        SELECT Role, COUNT(*) AS count
        FROM Employees
        GROUP BY Role
        ORDER BY count DESC
    ''').fetchall()

    # Karyawan per toko (store) - Gabungkan dengan tabel Stores untuk nama toko
    employees_by_store = conn.execute('''
        SELECT s.StoreName, COUNT(e.EmployeeID) AS count
        FROM Employees e
        JOIN Stores s ON e.StoreID = s.StoreID
        GROUP BY s.StoreName
        ORDER BY count DESC
    ''').fetchall()

    # Rata-rata gaji
    avg_salary = conn.execute('SELECT AVG(Salary) as avg_salary FROM Employees').fetchone()['avg_salary']

    # Karyawan dengan skor kinerja di bawah ambang batas (misalnya, < 70)
    low_performance_employees = conn.execute('''
        SELECT Name, Role, PerformanceScore
        FROM Employees
        WHERE PerformanceScore < 70
        ORDER BY PerformanceScore ASC
    ''').fetchall()

    # Karyawan baru per bulan (asumsi kolom HireDate ada)
    new_hires_monthly = conn.execute('''
        SELECT strftime('%Y-%m', HireDate) AS month, COUNT(*) AS new_hires
        FROM Employees
        GROUP BY month
        ORDER BY month
    ''').fetchall()

    conn.close()

    return render_template('employees.html',
                           total_employees=total_employees,
                           employees_by_role=employees_by_role,
                           employees_by_store=employees_by_store,
                           avg_salary=avg_salary,
                           low_performance_employees=low_performance_employees,
                           new_hires_monthly=new_hires_monthly)

# --- Transaction Dashboard Route ---
@app.route('/transactions')
def transaction_dashboard():
    conn = get_db_connection()

    # Total jumlah transaksi
    total_transactions = conn.execute('SELECT COUNT(*) as total FROM Transactions').fetchone()['total']

    # Total Sales keseluruhan
    total_sales_transactions = conn.execute('SELECT SUM(TotalSales) as total FROM Transactions').fetchone()['total']

    # Transaksi per metode pembayaran
    transactions_by_payment_method = conn.execute('''
        SELECT PaymentMethod, COUNT(*) AS count
        FROM Transactions
        GROUP BY PaymentMethod
        ORDER BY count DESC
    ''').fetchall()

    # Transaksi per toko (gabungkan dengan tabel Stores untuk nama toko)
    transactions_by_store = conn.execute('''
        SELECT s.StoreName, COUNT(t.TransactionID) AS count, SUM(t.TotalSales) AS total_sales
        FROM Transactions t
        JOIN Stores s ON t.StoreID = s.StoreID
        GROUP BY s.StoreName
        ORDER BY count DESC
    ''').fetchall()

    # Transaksi per bulan (menggunakan kolom 'Date')
    transactions_monthly = conn.execute('''
        SELECT strftime('%Y-%m', Date) AS month, COUNT(*) AS count, SUM(TotalSales) AS total_sales
        FROM Transactions
        GROUP BY month
        ORDER BY month
    ''').fetchall()

    # Top 10 Transaksi Terbaru
    latest_transactions = conn.execute('''
        SELECT
            t.TransactionID,
            t.Date,
            s.StoreName,
            p.ProductName,
            c.Name AS CustomerName,
            t.Quantity,
            t.UnitPrice,
            t.TotalSales,
            t.PaymentMethod
        FROM Transactions t
        JOIN Stores s ON t.StoreID = s.StoreID
        JOIN Products p ON t.ProductID = p.ProductID
        JOIN Customers c ON t.CustomerID = c.CustomerID
        ORDER BY t.Date DESC
        LIMIT 10
    ''').fetchall()

    conn.close()

    return render_template('transactions.html',
                           total_transactions=total_transactions,
                           total_sales_transactions=total_sales_transactions,
                           transactions_by_payment_method=transactions_by_payment_method,
                           transactions_by_store=transactions_by_store,
                           transactions_monthly=transactions_monthly,
                           latest_transactions=latest_transactions)

# Opsional: debug info untuk lihat struktur tabel
@app.route('/debug')
def debug():
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_info = {}
    for table in tables:
        table_name = table['name']
        columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        table_info[table_name] = [f"{col['name']} ({col['type']})" for col in columns]
    conn.close()
    return '<br><br>'.join([f"Table: {name}<br>" + '<br>'.join(cols) for name, cols in table_info.items()])

if __name__ == '__main__':
    app.run(debug=True)