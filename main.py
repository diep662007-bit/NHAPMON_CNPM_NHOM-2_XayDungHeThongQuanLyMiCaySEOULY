from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="API Quan Ly Quan Mi Cay SEOULY")

# --- 1. KẾT NỐI CƠ SỞ DỮ LIỆU & KHỞI TẠO BẢNG ---
def init_db():
    conn = sqlite3.connect("micay.db")
    cursor = conn.cursor()
    
    # Bảng tài khoản (Users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL -- 'admin' hoặc 'staff'
        )
    """)
    
    # Bảng thực đơn mì cay (Menu)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            spicy_level INTEGER NOT NULL -- Cấp độ cay tối đa (vd: cấp 0 - 7)
        )
    """)
    
    conn.commit()
    conn.close()

# Khởi chạy tạo cơ sở dữ liệu khi ứng dụng bật lên
init_db()

# --- 2. ĐỊNH NGHĨA MODEL DỮ LIỆU (Pydantic) ---
class UserLogin(BaseModel):
    username: str
    password: str

class MenuItem(BaseModel):
    name: str
    price: float
    spicy_level: int

# --- 3. API QUẢN LÝ TÀI KHOẢN / ĐĂNG NHẬP ---
@app.post("/api/login")
def login(user: UserLogin):
    conn = sqlite3.connect("micay.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user.username, user.password))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu!")
    return {"message": "Đăng nhập thành công!", "username": db_user[1], "role": db_user[3]}

# --- 4. API QUẢN LÝ THỰC ĐƠN (MENU: THÊM, SỬA, XÓA, XEM) ---

# Lấy danh sách món mì
@app.get("/api/menu")
def get_menu():
    conn = sqlite3.connect("micay.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    rows = cursor.fetchall()
    conn.close()
    
    menu_list = [{"id": r[0], "name": r[1], "price": r[2], "spicy_level": r[3]} for r in rows]
    return menu_list

# Thêm món mì mới
@app.post("/api/menu")
def add_menu_item(item: MenuItem):
    conn = sqlite3.connect("micay.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO menu (name, price, spicy_level) VALUES (?, ?, ?)", (item.name, item.price, item.spicy_level))
    conn.commit()
    conn.close()
    return {"message": "Thêm món mì thành công!"}

# Sửa thông tin món mì
@app.put("/api/menu/{item_id}")
def update_menu_item(item_id: int, item: MenuItem):
    conn = sqlite3.connect("micay.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE menu SET name = ?, price = ?, spicy_level = ? WHERE id = ?", (item.name, item.price, item.spicy_level, item_id))
    conn.commit()
    conn.close()
    return {"message": f"Cập nhật món ID {item_id} thành công!"}

# Xóa món mì
@app.delete("/api/menu/{item_id}")
def delete_menu_item(item_id: int):
    conn = sqlite3.connect("micay.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": f"Đã xóa món ID {item_id}!"}