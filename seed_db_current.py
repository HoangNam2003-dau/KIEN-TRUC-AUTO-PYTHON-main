import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kientrucauto.db"

CUSTOMERS = [
    ("Nguyễn Văn An", "an.nguyen@gmail.com", "0905123456"),
    ("Trần Thị Bình", "binh.tran@gmail.com", "0905777888"),
    ("Lê Minh Khang", "khang.le@gmail.com", "0905666999"),
    ("Phạm Gia Huy", "huy.pham@gmail.com", "0912345678"),
    ("Đỗ Thu Hà", "ha.do@gmail.com", "0911456789"),
    ("Võ Quốc Bảo", "bao.vo@gmail.com", "0933555777"),
    ("Bùi Thanh Tùng", "tung.bui@gmail.com", "0944666888"),
    ("Ngô Hải Yến", "yen.ngo@gmail.com", "0977888999"),
    ("Hoàng Đức Long", "long.hoang@gmail.com", "0988123123"),
    ("Mai Khánh Linh", "linh.mai@gmail.com", "0966777444"),
    ("Phan Nhật Nam", "nam.phan@gmail.com", "0955333222"),
    ("Dương Quỳnh Anh", "anh.duong@gmail.com", "0922444666"),
]

DEPOSIT_NOTES = [
    "Khách giữ xe để chờ chọn màu",
    "Khách muốn nhận xe trong tháng",
    "Cọc giữ xe sau khi lái thử",
    "Khách chờ phê duyệt hồ sơ trả góp",
]

ORDER_NOTES = [
    "Khách nhận xe tại showroom",
    "Hỗ trợ đăng ký xe và biển số",
    "Thanh toán chuyển khoản",
    "Chuẩn bị bàn giao cuối tuần",
    "Khách mua xe gia đình",
]

STATUSES = ["Chờ xác nhận", "Đã xác nhận", "Hoàn tất"]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE,
        type TEXT NOT NULL,
        category TEXT,
        price INTEGER NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        seats INTEGER,
        fuel TEXT,
        image TEXT,
        description TEXT
    );
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        total_spent INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS auth_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        customer_id INTEGER,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_code TEXT UNIQUE NOT NULL,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Chờ xác nhận',
        total_amount INTEGER NOT NULL,
        note TEXT
    );
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        unit_price INTEGER NOT NULL,
        line_total INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deposit_code TEXT UNIQUE NOT NULL,
        customer_id INTEGER,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        car_id INTEGER NOT NULL,
        deposit_amount INTEGER NOT NULL,
        note TEXT,
        status TEXT NOT NULL DEFAULT 'Chờ xác nhận',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS inventory_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        action TEXT NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()

def ensure_customers_and_accounts(conn):
    cur = conn.cursor()
    ids = []
    created_customers = 0
    created_accounts = 0

    for idx, (name, email, phone) in enumerate(CUSTOMERS, start=1):
        row = cur.execute(
            "SELECT id FROM customers WHERE phone = ? OR email = ? LIMIT 1",
            (phone, email),
        ).fetchone()

        if row:
            customer_id = row["id"]
        else:
            cur.execute(
                "INSERT INTO customers (name, email, phone, total_spent, created_at) VALUES (?, ?, ?, 0, ?)",
                (name, email, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            customer_id = cur.lastrowid
            created_customers += 1

        username = f"khachhang{idx}"
        auth = cur.execute(
            "SELECT id FROM auth_users WHERE username = ? LIMIT 1",
            (username,),
        ).fetchone()

        if not auth:
            cur.execute(
                "INSERT INTO auth_users (username, password, role, customer_id, created_at) VALUES (?, ?, 'customer', ?, ?)",
                (username, "123456", customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            created_accounts += 1

        ids.append(customer_id)

    conn.commit()
    return ids, created_customers, created_accounts

def seed_orders(conn, customer_ids):
    cur = conn.cursor()
    cars = cur.execute("SELECT id, name, price FROM cars ORDER BY id").fetchall()
    if not cars:
        raise RuntimeError("Bảng cars đang trống. Hãy chạy app.py trước để tạo dữ liệu xe.")

    created_orders = 0
    base_date = datetime.now() - timedelta(days=30)

    for i in range(20):
        customer_id = customer_ids[i % len(customer_ids)]
        selected = random.sample(list(cars), k=1 if i % 4 else 2)
        order_code = f"DHSEED{datetime.now().strftime('%y%m%d')}{i+1:03d}"

        if cur.execute("SELECT id FROM orders WHERE order_code = ?", (order_code,)).fetchone():
            continue

        total_amount = 0
        order_lines = []
        for car in selected:
            qty = 1
            unit_price = int(car["price"])
            line_total = unit_price * qty
            total_amount += line_total
            order_lines.append((car["id"], qty, unit_price, line_total))

        order_date = (base_date + timedelta(days=i, hours=i % 6)).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(STATUSES)
        note = random.choice(ORDER_NOTES)

        cur.execute(
            "INSERT INTO orders (order_code, customer_id, order_date, status, total_amount, note) VALUES (?, ?, ?, ?, ?, ?)",
            (order_code, customer_id, order_date, status, total_amount, note),
        )
        order_id = cur.lastrowid

        for car_id, qty, unit_price, line_total in order_lines:
            cur.execute(
                "INSERT INTO order_items (order_id, car_id, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?)",
                (order_id, car_id, qty, unit_price, line_total),
            )

        cur.execute(
            "UPDATE customers SET total_spent = total_spent + ? WHERE id = ?",
            (total_amount, customer_id),
        )
        created_orders += 1

    conn.commit()
    return created_orders

def seed_deposits(conn, customer_ids):
    cur = conn.cursor()
    cars = cur.execute("SELECT id, price FROM cars ORDER BY id").fetchall()
    created = 0

    for i in range(6):
        customer_id = customer_ids[i % len(customer_ids)]
        customer = cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        car = cars[i % len(cars)]
        deposit_code = f"DCSEED{datetime.now().strftime('%y%m%d')}{i+1:03d}"

        if cur.execute("SELECT id FROM deposits WHERE deposit_code = ?", (deposit_code,)).fetchone():
            continue

        deposit_amount = max(5000000, int(car["price"] * 0.05))
        created_at = (datetime.now() - timedelta(days=5-i)).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute(
            """
            INSERT INTO deposits (
                deposit_code, customer_id, customer_name, phone, email,
                car_id, deposit_amount, note, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                deposit_code,
                customer_id,
                customer["name"],
                customer["phone"],
                customer["email"],
                car["id"],
                deposit_amount,
                random.choice(DEPOSIT_NOTES),
                "Chờ xác nhận" if i % 2 == 0 else "Đã xác nhận",
                created_at,
            ),
        )
        created += 1

    conn.commit()
    return created

def main():
    conn = get_db()
    ensure_schema(conn)
    customer_ids, created_customers, created_accounts = ensure_customers_and_accounts(conn)
    created_orders = seed_orders(conn, customer_ids)
    created_deposits = seed_deposits(conn, customer_ids)
    conn.close()

    print("Đã seed dữ liệu thành công.")
    print(f"Khách hàng mới thêm: {created_customers}")
    print(f"Tài khoản đăng nhập mới thêm: {created_accounts}")
    print(f"Đơn hàng mới thêm: {created_orders}")
    print(f"Phiếu đặt cọc mới thêm: {created_deposits}")
    print("Tài khoản mẫu: khachhang1 -> khachhang12 | mật khẩu: 123456")

if __name__ == "__main__":
    main()
