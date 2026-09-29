from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
import sqlite3
from pathlib import Path
from datetime import datetime
from io import BytesIO
from werkzeug.utils import secure_filename
import csv
import io

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kientrucauto.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.secret_key = "kien-truc-auto-secret-key"
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

INITIAL_CARS = [
    {
        "name": "VinFast Fadil",
        "slug": "fadil",
        "type": "Xe Xăng",
        "category": "Hatchback",
        "price": 425000000,
        "stock": 7,
        "seats": 5,
        "fuel": "Xăng",
        "image": "Fadil.png",
        "description": "Dòng hatchback nhỏ gọn, tiết kiệm chi phí, phù hợp người mới mua xe và di chuyển hằng ngày.",
    },
    {
        "name": "VinFast Lux A2.0",
        "slug": "lux-a20",
        "type": "Xe Xăng",
        "category": "Sedan",
        "price": 950000000,
        "stock": 4,
        "seats": 5,
        "fuel": "Xăng",
        "image": "vinfast-lux-a20-den.png",
        "description": "Sedan sang trọng, thiết kế hiện đại, phù hợp cho cá nhân và doanh nghiệp.",
    },
    {
        "name": "VinFast Lux SA2.0",
        "slug": "lux-sa20",
        "type": "Xe Xăng",
        "category": "SUV 7 chỗ",
        "price": 1360000000,
        "stock": 3,
        "seats": 7,
        "fuel": "Xăng",
        "image": "vinfast-lux-sa-20.png",
        "description": "SUV rộng rãi cho gia đình, khả năng vận hành ổn định, nội thất tiện nghi.",
    },
    {
        "name": "VinFast VF3",
        "slug": "vf3",
        "type": "Xe Điện",
        "category": "Mini EV",
        "price": 299000000,
        "stock": 8,
        "seats": 4,
        "fuel": "Điện",
        "image": "vinfast-vf3.png",
        "description": "Dòng xe điện cỡ nhỏ, linh hoạt trong đô thị, thiết kế trẻ trung.",
    },
    {
        "name": "VinFast VF5 Plus",
        "slug": "vf5-plus",
        "type": "Xe Điện",
        "category": "Crossover",
        "price": 529000000,
        "stock": 6,
        "seats": 5,
        "fuel": "Điện",
        "image": "vinfast-vf5-plus.png",
        "description": "Mẫu xe điện nhỏ gọn, phù hợp gia đình trẻ, nhiều công nghệ an toàn.",
    },
    {
        "name": "VinFast VF6",
        "slug": "vf6",
        "type": "Xe Điện",
        "category": "SUV",
        "price": 790000000,
        "stock": 5,
        "seats": 5,
        "fuel": "Điện",
        "image": "Vinfast-VF6.jpg",
        "description": "SUV điện tầm trung, thiết kế hiện đại, tối ưu cho nhu cầu di chuyển thành thị.",
    },
    {
        "name": "VinFast VF7 Plus",
        "slug": "vf7-plus",
        "type": "Xe Điện",
        "category": "SUV",
        "price": 999000000,
        "stock": 4,
        "seats": 5,
        "fuel": "Điện",
        "image": "VF7-Plus.jpg",
        "description": "SUV điện cá tính, trang bị hiện đại, phù hợp khách hàng thích công nghệ.",
    },
    {
        "name": "VinFast VF8",
        "slug": "vf8",
        "type": "Xe Điện",
        "category": "SUV",
        "price": 1120000000,
        "stock": 3,
        "seats": 5,
        "fuel": "Điện",
        "image": "Vinfast-VF8.jpg",
        "description": "SUV điện cao cấp, nội thất rộng, phục vụ tốt cho gia đình và công việc.",
    },
    {
        "name": "VinFast VF9 Plus",
        "slug": "vf9-plus",
        "type": "Xe Điện",
        "category": "SUV 7 chỗ",
        "price": 1680000000,
        "stock": 2,
        "seats": 7,
        "fuel": "Điện",
        "image": "VF9-Plus.jpg",
        "description": "SUV điện cỡ lớn, sang trọng, hướng đến gia đình đông người và doanh nghiệp.",
    },
    {
        "name": "VinFast Limo Green",
        "slug": "limo-green",
        "type": "Xe Điện",
        "category": "MPV",
        "price": 749000000,
        "stock": 5,
        "seats": 7,
        "fuel": "Điện",
        "image": "limogreen.png",
        "description": "Mẫu MPV điện rộng rãi, phù hợp gia đình và dịch vụ vận tải cao cấp.",
    },
    {
        "name": "VinFast Herio Green",
        "slug": "herio-green",
        "type": "Xe Điện",
        "category": "CUV",
        "price": 699000000,
        "stock": 5,
        "seats": 5,
        "fuel": "Điện",
        "image": "herio.png",
        "description": "Mẫu crossover điện hiện đại, thiết kế trẻ trung, phù hợp di chuyển đô thị.",
    },
    {
        "name": "VinFast Minio Green",
        "slug": "minio-green",
        "type": "Xe Điện",
        "category": "Mini EV",
        "price": 269000000,
        "stock": 8,
        "seats": 4,
        "fuel": "Điện",
        "image": "miniogreen.png",
        "description": "Mẫu mini EV nhỏ gọn, tiết kiệm chi phí, linh hoạt trong thành phố.",
    },
    {
        "name": "VinFast EC Van",
        "slug": "ecvan",
        "type": "Xe Điện",
        "category": "Van",
        "price": 359000000,
        "stock": 4,
        "seats": 2,
        "fuel": "Điện",
        "image": "ecvan.png",
        "description": "Mẫu xe van điện phục vụ vận chuyển hàng hóa, tối ưu cho kinh doanh.",
    },
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
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
            created_at TEXT NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Chờ xác nhận',
            total_amount INTEGER NOT NULL,
            note TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price INTEGER NOT NULL,
            line_total INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(car_id) REFERENCES cars(id)
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
            created_at TEXT NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(car_id) REFERENCES cars(id)
        );

        CREATE TABLE IF NOT EXISTS inventory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            action TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(car_id) REFERENCES cars(id)
        );
        """
    )

    customer_cols = [r[1] for r in cur.execute("PRAGMA table_info(customers)").fetchall()]
    if "created_at" not in customer_cols:
        cur.execute("ALTER TABLE customers ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
        cur.execute(
            "UPDATE customers SET created_at=? WHERE created_at=''",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),),
        )

    car_count = cur.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    if car_count == 0:
        for car in INITIAL_CARS:
            cur.execute(
                """
                INSERT INTO cars (name, slug, type, category, price, stock, seats, fuel, image, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    car["name"],
                    car["slug"],
                    car["type"],
                    car["category"],
                    car["price"],
                    car["stock"],
                    car["seats"],
                    car["fuel"],
                    car["image"],
                    car["description"],
                ),
            )

    admin = cur.execute("SELECT id FROM auth_users WHERE username='admin'").fetchone()
    if not admin:
        cur.execute(
            """
            INSERT INTO auth_users (username, password, role, customer_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", "123456", "admin", None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

    demo_customer = cur.execute("SELECT id FROM auth_users WHERE username='khachhang1'").fetchone()
    if not demo_customer:
        customer = cur.execute("SELECT * FROM customers WHERE phone='0905000001'").fetchone()
        if not customer:
            cur.execute(
                """
                INSERT INTO customers (name, email, phone, total_spent, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Khách Hàng Mẫu",
                    "kh1@example.com",
                    "0905000001",
                    0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            customer_id = cur.lastrowid
        else:
            customer_id = customer["id"]

        cur.execute(
            """
            INSERT INTO auth_users (username, password, role, customer_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("khachhang1", "123456", "customer", customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

    extra_cars = [
        {
            "name": "VinFast Limo Green",
            "slug": "limo-green",
            "type": "Xe Điện",
            "category": "MPV",
            "price": 749000000,
            "stock": 5,
            "seats": 7,
            "fuel": "Điện",
            "image": "limogreen.png",
            "description": "Mẫu MPV điện rộng rãi, phù hợp gia đình và dịch vụ vận tải cao cấp.",
        },
        {
            "name": "VinFast Herio Green",
            "slug": "herio-green",
            "type": "Xe Điện",
            "category": "CUV",
            "price": 699000000,
            "stock": 5,
            "seats": 5,
            "fuel": "Điện",
            "image": "herio.png",
            "description": "Mẫu crossover điện hiện đại, thiết kế trẻ trung, phù hợp di chuyển đô thị.",
        },
        {
            "name": "VinFast Minio Green",
            "slug": "minio-green",
            "type": "Xe Điện",
            "category": "Mini EV",
            "price": 269000000,
            "stock": 8,
            "seats": 4,
            "fuel": "Điện",
            "image": "miniogreen.png",
            "description": "Mẫu mini EV nhỏ gọn, tiết kiệm chi phí, linh hoạt trong thành phố.",
        },
        {
            "name": "VinFast EC Van",
            "slug": "ecvan",
            "type": "Xe Điện",
            "category": "Van",
            "price": 359000000,
            "stock": 4,
            "seats": 2,
            "fuel": "Điện",
            "image": "ecvan.png",
            "description": "Mẫu xe van điện phục vụ vận chuyển hàng hóa, tối ưu cho kinh doanh.",
        },
    ]

    for car in extra_cars:
        existed = cur.execute("SELECT id FROM cars WHERE slug=?", (car["slug"],)).fetchone()
        if not existed:
            cur.execute(
                """
                INSERT INTO cars (name, slug, type, category, price, stock, seats, fuel, image, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    car["name"],
                    car["slug"],
                    car["type"],
                    car["category"],
                    car["price"],
                    car["stock"],
                    car["seats"],
                    car["fuel"],
                    car["image"],
                    car["description"],
                ),
            )

    conn.commit()
    conn.close()


def fmt_vnd(value):
    try:
        return f"{int(value):,}".replace(",", ".") + " đ"
    except Exception:
        return "0 đ"


app.jinja_env.filters["vnd"] = fmt_vnd


def get_all_cars(type_filter=None):
    conn = get_db()
    if type_filter:
        rows = conn.execute("SELECT * FROM cars WHERE type=? ORDER BY id", (type_filter,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM cars ORDER BY id").fetchall()
    conn.close()
    return rows


def get_car(car_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    conn.close()
    return row


def get_cart():
    return session.setdefault("cart", {})


def cart_items_with_totals():
    cart = get_cart()
    items = []
    total = 0

    for car_id_str, quantity in cart.items():
        car = get_car(int(car_id_str))
        if not car:
            continue

        qty = int(quantity)
        line_total = int(car["price"]) * qty
        total += line_total

        items.append(
            {
                "car_id": car["id"],
                "name": car["name"],
                "image": car["image"],
                "type": car["type"],
                "category": car["category"],
                "price": car["price"],
                "stock": car["stock"],
                "quantity": qty,
                "line_total": line_total,
                "car": car,
            }
        )

    return items, total


def require_admin():
    return session.get("role") == "admin"


def require_customer():
    return session.get("role") == "customer"


def current_customer_id():
    return session.get("customer_id")


@app.context_processor
def inject_globals():
    items, total = cart_items_with_totals()
    current_customer = None

    if require_customer() and current_customer_id():
        conn = get_db()
        current_customer = conn.execute(
            "SELECT * FROM customers WHERE id=?",
            (current_customer_id(),),
        ).fetchone()
        conn.close()

    return {
        "cart_count": sum(i["quantity"] for i in items),
        "cart_total": total,
        "current_role": session.get("role"),
        "current_username": session.get("username"),
        "current_customer_name": session.get("customer_name"),
        "current_customer": current_customer,
    }


@app.route("/")
def index():
    return redirect(url_for("trangchu"))


@app.route("/trangchu.html")
def trangchu():
    return render_template("trangchu.html", cars=get_all_cars())


@app.route("/xexang.html")
def xexang():
    q = request.args.get("q", "").strip().lower()
    cars = get_all_cars("Xe Xăng")
    if q:
        cars = [
            c for c in cars
            if q in (c["name"] or "").lower()
            or q in (c["category"] or "").lower()
            or q in (c["type"] or "").lower()
            or q in (c["fuel"] or "").lower()
        ]
    return render_template("catalog.html", title="Xe Xăng", cars=cars)


@app.route("/xedien.html")
def xedien():
    q = request.args.get("q", "").strip().lower()
    cars = get_all_cars("Xe Điện")
    if q:
        cars = [
            c for c in cars
            if q in (c["name"] or "").lower()
            or q in (c["category"] or "").lower()
            or q in (c["type"] or "").lower()
            or q in (c["fuel"] or "").lower()
        ]
    return render_template("catalog.html", title="Xe Điện", cars=cars)


@app.route("/cuahang")
def cuahang():
    q = request.args.get("q", "").strip().lower()
    cars = get_all_cars()

    if q:
        cars = [
            c for c in cars
            if q in (c["name"] or "").lower()
            or q in (c["category"] or "").lower()
            or q in (c["type"] or "").lower()
            or q in (c["fuel"] or "").lower()
        ]

    return render_template("catalog.html", title="Cửa hàng", cars=cars)


@app.route("/tim-kiem")
def tim_kiem():
    q = request.args.get("q", "").strip().lower()
    cars = get_all_cars()

    if q:
        cars = [
            c for c in cars
            if q in (c["name"] or "").lower()
            or q in (c["category"] or "").lower()
            or q in (c["type"] or "").lower()
            or q in (c["fuel"] or "").lower()
        ]

    return render_template(
        "catalog.html",
        title=f"Kết quả tìm kiếm: {q}" if q else "Tìm kiếm xe",
        cars=cars,
    )


@app.route("/chitietxe/<int:car_id>.html")
def chitietxe(car_id):
    car = get_car(car_id)
    if not car:
        return "Không tìm thấy xe", 404
    return render_template("chitietxe.html", car=car)


@app.route("/giohang.html")
def giohang():
    cart_items, total = cart_items_with_totals()
    customer = None

    if require_customer() and current_customer_id():
        conn = get_db()
        customer = conn.execute("SELECT * FROM customers WHERE id=?", (current_customer_id(),)).fetchone()
        conn.close()

    return render_template("giohang.html", cart_items=cart_items, cart_total=total, current_customer=customer)


@app.route("/api/cart/add/<int:car_id>", methods=["POST"])
def api_cart_add(car_id):
    car = get_car(car_id)
    if not car:
        return jsonify({"ok": False, "message": "Xe không tồn tại"}), 404

    cart = get_cart()
    key = str(car_id)
    cart[key] = cart.get(key, 0) + 1
    session.modified = True

    cart_count = sum(int(v) for v in cart.values())
    return jsonify({"ok": True, "message": f"Đã thêm {car['name']} vào giỏ hàng", "cart_count": cart_count})


@app.route("/api/cart/update/<int:car_id>", methods=["POST"])
def api_cart_update(car_id):
    quantity = max(0, int(request.form.get("quantity", 1)))
    cart = get_cart()
    key = str(car_id)

    if quantity == 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    session.modified = True
    return redirect(url_for("giohang"))


@app.route("/api/cart/remove/<int:car_id>", methods=["POST"])
def api_cart_remove(car_id):
    cart = get_cart()
    cart.pop(str(car_id), None)
    session.modified = True
    return redirect(url_for("giohang"))


@app.route("/checkout", methods=["POST"])
def checkout():
    items, total = cart_items_with_totals()
    if not items:
        flash("Giỏ hàng đang trống.", "error")
        return redirect(url_for("giohang"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    note = request.form.get("note", "").strip()
    checkout_mode = request.form.get("checkout_mode", "order").strip()

    deposit_amount = int(total * 0.01) if checkout_mode == "deposit" else 0

    if not name or not phone:
        flash("Vui lòng nhập họ tên và số điện thoại.", "error")
        return redirect(url_for("giohang"))

    if checkout_mode == "deposit" and deposit_amount <= 0:
        flash("Vui lòng nhập số tiền đặt cọc hợp lệ.", "error")
        return redirect(url_for("giohang"))

    conn = get_db()
    cur = conn.cursor()

    customer = None
    if require_customer() and current_customer_id():
        customer = cur.execute(
            "SELECT * FROM customers WHERE id=?",
            (current_customer_id(),)
        ).fetchone()

    if not customer:
        customer = cur.execute(
            "SELECT * FROM customers WHERE phone=? OR (email<>'' AND email=?) LIMIT 1",
            (phone, email)
        ).fetchone()

    if customer:
        customer_id = customer["id"]
        cur.execute(
            "UPDATE customers SET name=?, email=?, phone=? WHERE id=?",
            (name, email, phone, customer_id)
        )
    else:
        cur.execute(
            """
            INSERT INTO customers (name, email, phone, total_spent, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, phone, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        customer_id = cur.lastrowid

    if checkout_mode == "order":
        order_status = "Chờ xác nhận"
    elif checkout_mode == "deposit":
        order_status = "Chờ đặt cọc"
    else:
        order_status = "Chờ tư vấn"

    order_code = f"DH{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cur.execute(
        """
        INSERT INTO orders (order_code, customer_id, order_date, status, total_amount, note)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            order_code,
            customer_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            order_status,
            total,
            note
        )
    )
    order_id = cur.lastrowid

    for item in items:
        car = item["car"]
        qty = item["quantity"]

        if car["stock"] < qty:
            conn.rollback()
            conn.close()
            flash(f"Xe {car['name']} không đủ tồn kho.", "error")
            return redirect(url_for("giohang"))

        cur.execute(
            """
            INSERT INTO order_items (order_id, car_id, quantity, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, car["id"], qty, car["price"], item["line_total"])
        )

        cur.execute(
            "UPDATE cars SET stock = stock - ? WHERE id=?",
            (qty, car["id"])
        )

    if checkout_mode == "order":
        cur.execute(
            "UPDATE customers SET total_spent = total_spent + ? WHERE id=?",
            (total, customer_id)
        )

    if checkout_mode == "deposit":
        first_car_id = items[0]["car_id"]
        deposit_code = f"DC{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
        cur.execute(
            """
            INSERT INTO deposits (
                deposit_code, customer_id, customer_name, phone, email,
                car_id, deposit_amount, note, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                deposit_code,
                customer_id,
                name,
                phone,
                email,
                first_car_id,
                deposit_amount,
                f"Đặt cọc từ giỏ hàng - đơn {order_code}. {note}".strip(),
                "Chờ xác nhận",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

    conn.commit()
    conn.close()

    session["cart"] = {}

    if checkout_mode == "order":
        flash("Đã gửi yêu cầu mua xe thành công.", "success")
    elif checkout_mode == "deposit":
        flash("Đã tạo yêu cầu đặt cọc thành công.", "success")
    else:
        flash("Đã gửi yêu cầu tư vấn trả góp.", "success")

    return redirect(url_for("invoice", order_id=order_id))


@app.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM auth_users WHERE username=? AND password=? LIMIT 1",
            (username, password),
        ).fetchone()

        customer_name = None
        if user and user["customer_id"]:
            customer = conn.execute(
                "SELECT * FROM customers WHERE id=?",
                (user["customer_id"],),
            ).fetchone()
            customer_name = customer["name"] if customer else username

        conn.close()

        if not user:
            flash("Sai tài khoản hoặc mật khẩu.", "error")
            return render_template("login.html")

        old_cart = session.get("cart", {})
        session.clear()
        session["cart"] = old_cart
        session["role"] = user["role"]
        session["username"] = user["username"]
        session["user_id"] = user["id"]

        if user["role"] == "customer":
            session["customer_id"] = user["customer_id"]
            session["customer_name"] = customer_name or user["username"]
            flash("Đăng nhập khách hàng thành công.", "success")
            return redirect(url_for("tai_khoan_kh"))

        flash("Đăng nhập quản trị thành công.", "success")
        return redirect(url_for("quantri"))

    return render_template("login.html")


@app.route("/dang-ky", methods=["GET", "POST"])
def dang_ky():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not phone or not username or not password:
            flash("Vui lòng nhập đầy đủ thông tin bắt buộc.", "error")
            return redirect("/dang-ky")

        conn = get_db()
        cur = conn.cursor()

        existed = cur.execute("SELECT id FROM auth_users WHERE username = ?", (username,)).fetchone()
        if existed:
            conn.close()
            flash("Tên đăng nhập đã tồn tại", "error")
            return redirect("/dang-ky")

        cur.execute(
            """
            INSERT INTO customers (name, email, phone, total_spent, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, phone, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        customer_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO auth_users (username, password, role, customer_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, password, "customer", customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

        conn.commit()
        conn.close()

        flash("Đăng ký thành công, hãy đăng nhập", "success")
        return redirect("/dang-nhap")

    return render_template("register.html")


@app.route("/dat-coc/<int:car_id>", methods=["POST"])
def dat_coc(car_id):
    customer_name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    note = request.form.get("note", "").strip()

    try:
        deposit_amount = int(float(request.form.get("deposit_amount", 0) or 0))
    except Exception:
        deposit_amount = 0

    if not customer_name or not phone or deposit_amount <= 0:
        flash("Vui lòng nhập đầy đủ thông tin và số tiền đặt cọc hợp lệ.", "error")
        return redirect(url_for("giohang"))

    conn = get_db()
    cur = conn.cursor()

    car = cur.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    if not car:
        conn.close()
        flash("Không tìm thấy xe để đặt cọc.", "error")
        return redirect(url_for("giohang"))

    customer_id = current_customer_id() if require_customer() else None

    if customer_id:
        cur.execute(
            "UPDATE customers SET name=?, email=?, phone=? WHERE id=?",
            (customer_name, email, phone, customer_id),
        )

    deposit_code = f"DC{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
    cur.execute(
        """
        INSERT INTO deposits (
            deposit_code, customer_id, customer_name, phone, email,
            car_id, deposit_amount, note, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            deposit_code,
            customer_id,
            customer_name,
            phone,
            email,
            car_id,
            deposit_amount,
            note,
            "Chờ xác nhận",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()

    flash("Đặt cọc thành công. Chúng tôi sẽ liên hệ với bạn sớm.", "success")
    return redirect(url_for("giohang"))


@app.route("/dang-xuat")
def dang_xuat():
    cart = session.get("cart", {})
    session.clear()
    session["cart"] = cart
    flash("Đã đăng xuất.", "success")
    return redirect(url_for("trangchu"))


@app.route("/tai-khoan-kh")
def tai_khoan_kh():
    if not require_customer():
        return redirect(url_for("dang_nhap"))

    conn = get_db()

    customer = conn.execute(
        "SELECT * FROM customers WHERE id=?",
        (current_customer_id(),)
    ).fetchone()

    orders = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE customer_id=?
        ORDER BY id DESC
        """,
        (current_customer_id(),)
    ).fetchall()

    deposits = conn.execute(
        """
        SELECT d.*, c.name AS car_name
        FROM deposits d
        JOIN cars c ON d.car_id = c.id
        WHERE d.customer_id=?
        ORDER BY d.id DESC
        """,
        (current_customer_id(),)
    ).fetchall()

    conn.close()

    return render_template(
        "customer_account.html",
        customer=customer,
        orders=orders,
        deposits=deposits
    )


@app.route("/quantri.html")
def quantri():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()

    stats = {
        "car_count": conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0],
        "customer_count": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
        "order_count": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "stock_total": conn.execute("SELECT COALESCE(SUM(stock),0) FROM cars").fetchone()[0],
        "revenue": conn.execute(
            "SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status != 'Đã hủy'"
        ).fetchone()[0],
    }

    top_car = conn.execute(
        """
        SELECT c.name, COALESCE(SUM(oi.quantity),0) AS sold_qty
        FROM cars c
        LEFT JOIN order_items oi ON c.id = oi.car_id
        GROUP BY c.id, c.name
        ORDER BY sold_qty DESC, c.name
        LIMIT 1
        """
    ).fetchone()

    top_customer = conn.execute(
        """
        SELECT c.name, COUNT(o.id) AS total_orders, COALESCE(SUM(o.total_amount),0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC, total_orders DESC, c.name
        LIMIT 1
        """
    ).fetchone()

    recent_orders = conn.execute(
        """
        SELECT o.*, c.name AS customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.id DESC
        LIMIT 5
        """
    ).fetchall()

    cars = conn.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()

    revenue_by_day = conn.execute(
        """
        SELECT substr(order_date, 1, 10) AS day,
               COALESCE(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status != 'Đã hủy'
        GROUP BY substr(order_date, 1, 10)
        ORDER BY day ASC
        LIMIT 15
        """
    ).fetchall()

    revenue_by_month = conn.execute(
        """
        SELECT substr(order_date, 1, 7) AS month,
               COALESCE(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status != 'Đã hủy'
        GROUP BY substr(order_date, 1, 7)
        ORDER BY month ASC
        """
    ).fetchall()

    best_selling_products = conn.execute(
        """
        SELECT c.name,
               COALESCE(SUM(oi.quantity), 0) AS sold_qty
        FROM cars c
        LEFT JOIN order_items oi ON c.id = oi.car_id
        GROUP BY c.id, c.name
        HAVING sold_qty > 0
        ORDER BY sold_qty DESC, c.name
        LIMIT 7
        """
    ).fetchall()

    top_spending_customers = conn.execute(
        """
        SELECT c.name,
               COALESCE(SUM(o.total_amount), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name
        HAVING total_spent > 0
        ORDER BY total_spent DESC, c.name
        LIMIT 7
        """
    ).fetchall()

    conn.close()

    return render_template(
        "quantri.html",
        stats=stats,
        top_car=top_car,
        top_customer=top_customer,
        recent_orders=recent_orders,
        cars=cars,
        revenue_by_day=revenue_by_day,
        revenue_by_month=revenue_by_month,
        best_selling_products=best_selling_products,
        top_spending_customers=top_spending_customers,
    )


@app.route("/admin/cars", methods=["GET", "POST"])
def admin_cars():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        form = request.form

        name = form.get("name", "").strip()
        slug = form.get("slug", "").strip() or name.lower().replace(" ", "-")
        car_type = form.get("type", "").strip()
        category = form.get("category", "").strip()
        fuel = form.get("fuel", "").strip()
        description = form.get("description", "").strip()

        try:
            price = int(form.get("price") or 0)
            stock = int(form.get("stock") or 0)
            seats = int(form.get("seats") or 0)
        except ValueError:
            conn.close()
            flash("Giá, tồn kho và số chỗ phải là số hợp lệ.", "error")
            return redirect(url_for("admin_cars"))

        image_file = request.files.get("image_file")
        image_name = ""

        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                save_path = Path(app.config["UPLOAD_FOLDER"]) / filename
                image_file.save(save_path)
                image_name = filename
            else:
                conn.close()
                flash("Ảnh không hợp lệ. Chỉ chấp nhận png, jpg, jpeg, webp.", "error")
                return redirect(url_for("admin_cars"))
        else:
            image_name = form.get("image", "").strip()

        if not name or not car_type or not category or not image_name:
            conn.close()
            flash("Vui lòng nhập đầy đủ thông tin xe và chọn ảnh.", "error")
            return redirect(url_for("admin_cars"))

        cur.execute(
            """
            INSERT INTO cars (name, slug, type, category, price, stock, seats, fuel, image, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, slug, car_type, category, price, stock, seats, fuel, image_name, description),
        )
        conn.commit()
        conn.close()

        flash("Đã thêm xe mới thành công.", "success")
        return redirect(url_for("admin_cars"))

    cars = cur.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin_cars.html", cars=cars)


@app.route("/admin/cars/restock/<int:car_id>", methods=["POST"])
def admin_restock_car(car_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    try:
        restock_quantity = int(request.form.get("restock_quantity", 0))
    except ValueError:
        flash("Số lượng nhập kho không hợp lệ.", "error")
        return redirect(url_for("admin_cars"))

    if restock_quantity <= 0:
        flash("Số lượng nhập kho phải lớn hơn 0.", "error")
        return redirect(url_for("admin_cars"))

    conn = get_db()
    car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()

    if not car:
        conn.close()
        flash("Không tìm thấy xe.", "error")
        return redirect(url_for("admin_cars"))

    conn.execute("UPDATE cars SET stock = stock + ? WHERE id=?", (restock_quantity, car_id))

    try:
        conn.execute(
            """
            INSERT INTO inventory_logs (car_id, quantity, action, note, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                car_id,
                restock_quantity,
                "IMPORT",
                f"Nhập thêm {restock_quantity} xe",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
    except Exception:
        pass

    conn.commit()
    conn.close()

    flash(f"Đã nhập thêm {restock_quantity} xe cho {car['name']}.", "success")
    return redirect(url_for("admin_cars"))


@app.route("/admin/cars/delete/<int:car_id>", methods=["POST"])
def admin_delete_car(car_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()
    used_count = conn.execute("SELECT COUNT(*) FROM order_items WHERE car_id=?", (car_id,)).fetchone()[0]

    if used_count > 0:
        conn.close()
        flash("Không thể xóa xe đã có trong đơn hàng.", "error")
        return redirect(url_for("admin_cars"))

    car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    if not car:
        conn.close()
        flash("Không tìm thấy xe.", "error")
        return redirect(url_for("admin_cars"))

    conn.execute("DELETE FROM cars WHERE id=?", (car_id,))
    conn.commit()
    conn.close()

    flash(f"Đã xóa xe {car['name']}.", "success")
    return redirect(url_for("admin_cars"))


@app.route("/admin/customers")
def admin_customers():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    sort_by = request.args.get("sort_by", "total_spent")
    order = request.args.get("order", "desc")

    if sort_by == "name":
        conn = get_db()
        customers = conn.execute("SELECT * FROM customers").fetchall()
        conn.close()

        customers = sorted(
            customers,
            key=lambda c: (c["name"].strip().split()[-1].lower(), c["name"].lower()),
            reverse=(order == "desc")
        )

        return render_template(
            "admin_customers.html",
            customers=customers,
            sort_by=sort_by,
            order=order
        )

    sort_column = "total_spent"
    sort_order = "ASC" if order == "asc" else "DESC"

    conn = get_db()
    customers = conn.execute(
        f"""
        SELECT *
        FROM customers
        ORDER BY {sort_column} {sort_order}, id DESC
        """
    ).fetchall()
    conn.close()

    return render_template(
        "admin_customers.html",
        customers=customers,
        sort_by=sort_by,
        order=order
    )


@app.route("/admin/customers/delete/<int:customer_id>", methods=["POST"])
def admin_delete_customer(customer_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()
    order_count = conn.execute("SELECT COUNT(*) FROM orders WHERE customer_id=?", (customer_id,)).fetchone()[0]

    if order_count > 0:
        conn.close()
        flash("Không thể xóa khách hàng đã có đơn hàng.", "error")
        return redirect(url_for("admin_customers"))

    conn.execute("DELETE FROM auth_users WHERE customer_id=?", (customer_id,))
    conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()

    flash("Đã xóa khách hàng.", "success")
    return redirect(url_for("admin_customers"))


@app.route("/admin/orders")
def admin_orders():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    sort_by = request.args.get("sort_by", "date")
    order = request.args.get("order", "desc")
    status_filter = request.args.get("status", "").strip()

    allowed_sort = {
        "date": "o.order_date",
        "status": "o.status",
        "total": "o.total_amount"
    }
    sort_column = allowed_sort.get(sort_by, "o.order_date")
    sort_order = "ASC" if order == "asc" else "DESC"

    conn = get_db()

    query = """
        SELECT o.*, c.name AS customer_name, c.phone, c.email
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
    """
    params = []

    if status_filter:
        query += " WHERE o.status = ? "
        params.append(status_filter)

    query += f" ORDER BY {sort_column} {sort_order}, o.id DESC"

    orders = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders,
        sort_by=sort_by,
        order=order,
        status_filter=status_filter
    )


@app.route("/admin/orders/update/<int:order_id>", methods=["POST"])
def admin_update_order(order_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    status = request.form.get("status", "Chờ xác nhận").strip()

    valid_statuses = [
        "Chờ xác nhận",
        "Chờ đặt cọc",
        "Chờ tư vấn",
        "Đã xác nhận",
        "Hoàn tất",
        "Đã hủy",
    ]

    if status not in valid_statuses:
        flash("Trạng thái đơn hàng không hợp lệ.", "error")
        return redirect(url_for("admin_orders"))

    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()

    flash("Đã cập nhật trạng thái đơn hàng.", "success")
    return redirect(url_for("admin_orders"))


@app.route("/admin/orders/delete/<int:order_id>", methods=["POST"])
def admin_delete_order(order_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()
    cur = conn.cursor()

    items = cur.execute("SELECT car_id, quantity FROM order_items WHERE order_id=?", (order_id,)).fetchall()
    for item in items:
        cur.execute("UPDATE cars SET stock = stock + ? WHERE id=?", (item["quantity"], item["car_id"]))

    cur.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()

    flash("Đã xóa đơn hàng và hoàn lại tồn kho.", "success")
    return redirect(url_for("admin_orders"))


@app.route("/admin/deposits")
def admin_deposits():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    status_filter = request.args.get("status", "").strip()
    order = request.args.get("order", "desc")

    sort_order = "ASC" if order == "asc" else "DESC"

    conn = get_db()

    query = """
        SELECT d.*, c.name AS car_name
        FROM deposits d
        JOIN cars c ON d.car_id = c.id
    """
    params = []

    if status_filter:
        query += " WHERE d.status = ? "
        params.append(status_filter)

    query += f" ORDER BY d.created_at {sort_order}, d.id DESC"

    deposits = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "admin_deposits.html",
        deposits=deposits,
        status_filter=status_filter,
        order=order
    )


@app.route("/admin/deposits/update/<int:deposit_id>", methods=["POST"])
def admin_update_deposit(deposit_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    status = request.form.get("status", "").strip()

    valid_statuses = [
        "Chờ xác nhận",
        "Đã xác nhận",
        "Đã thanh toán",
        "Đã hủy",
    ]

    if status not in valid_statuses:
        flash("Trạng thái đặt cọc không hợp lệ.", "error")
        return redirect(url_for("admin_deposits"))

    conn = get_db()
    conn.execute("UPDATE deposits SET status=? WHERE id=?", (status, deposit_id))
    conn.commit()
    conn.close()

    flash("Đã cập nhật trạng thái đặt cọc.", "success")
    return redirect(url_for("admin_deposits"))


@app.route("/admin/deposits/delete/<int:deposit_id>", methods=["POST"])
def admin_delete_deposit(deposit_id):
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()
    conn.execute("DELETE FROM deposits WHERE id=?", (deposit_id,))
    conn.commit()
    conn.close()

    flash("Đã xóa phiếu đặt cọc.", "success")
    return redirect(url_for("admin_deposits"))


@app.route("/admin/reports")
def admin_reports():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()

    revenue_by_day = conn.execute(
        """
        SELECT substr(order_date,1,10) AS day, COALESCE(SUM(total_amount),0) AS revenue
        FROM orders
        WHERE status != 'Đã hủy'
        GROUP BY substr(order_date,1,10)
        ORDER BY day DESC
        LIMIT 10
        """
    ).fetchall()

    best_sellers = conn.execute(
        """
        SELECT c.name, COALESCE(SUM(oi.quantity),0) AS sold_qty, COALESCE(SUM(oi.line_total),0) AS revenue
        FROM cars c
        LEFT JOIN order_items oi ON c.id = oi.car_id
        GROUP BY c.id, c.name
        ORDER BY sold_qty DESC, revenue DESC, c.name
        """
    ).fetchall()

    top_customers = conn.execute(
        """
        SELECT c.name, c.phone, COUNT(o.id) AS total_orders, COALESCE(SUM(o.total_amount),0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name, c.phone
        ORDER BY total_spent DESC, total_orders DESC, c.name
        """
    ).fetchall()

    conn.close()
    return render_template(
        "admin_reports.html",
        revenue_by_day=revenue_by_day,
        best_sellers=best_sellers,
        top_customers=top_customers,
    )


@app.route("/admin/invoice/<int:order_id>")
def invoice(order_id):
    conn = get_db()

    order = conn.execute(
        """
        SELECT o.*, c.name AS customer_name, c.phone, c.email
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id=?
        """,
        (order_id,),
    ).fetchone()

    items = conn.execute(
        """
        SELECT oi.*, c.name AS car_name
        FROM order_items oi
        JOIN cars c ON oi.car_id = c.id
        WHERE oi.order_id=?
        """,
        (order_id,),
    ).fetchall()

    conn.close()

    if not order:
        return "Không tìm thấy hóa đơn", 404

    return render_template("invoice.html", order=order, items=items)


@app.route("/admin/export/orders.csv")
def export_orders_csv():
    if not require_admin():
        return redirect(url_for("dang_nhap"))

    conn = get_db()
    rows = conn.execute(
        """
        SELECT o.order_code, o.order_date, c.name AS customer_name, c.phone, o.status, o.total_amount
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.id DESC
        """
    ).fetchall()
    conn.close()

    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(["Mã đơn", "Ngày", "Khách hàng", "SĐT", "Trạng thái", "Tổng tiền"])

    for r in rows:
        writer.writerow([r["order_code"], r["order_date"], r["customer_name"], r["phone"], r["status"], r["total_amount"]])

    data = text.getvalue().encode("utf-8-sig")
    return send_file(
        BytesIO(data),
        mimetype="text/csv",
        as_attachment=True,
        download_name="don_hang_kien_truc_auto.csv",
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)