"""
Script tạo dữ liệu mẫu cho tất cả microservices.
Chạy: python create_sample_data.py
Yêu cầu: pip install requests (hoặc chạy trực tiếp trên máy host)
"""
import requests
import time
import sys

# ── Base URLs ──────────────────────────────────────────────
STAFF_URL = "http://localhost:8001/api"
MANAGER_URL = "http://localhost:8002/api"
CUSTOMER_URL = "http://localhost:8003/api"
CATALOG_URL = "http://localhost:8004/api"
BOOK_URL = "http://localhost:8005/api"
CART_URL = "http://localhost:8006/api"
ORDER_URL = "http://localhost:8007/api"
SHIP_URL = "http://localhost:8008/api"
PAY_URL = "http://localhost:8009/api"
COMMENT_URL = "http://localhost:8010/api"
RECOMMENDER_URL = "http://localhost:8011/api"

created = {"success": 0, "failed": 0}


def post(url, data, label=""):
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code in (200, 201):
            created["success"] += 1
            return r.json()
        else:
            created["failed"] += 1
            print(f"  WARN [{r.status_code}] {label}: {r.text[:120]}")
            return None
    except Exception as e:
        created["failed"] += 1
        print(f"  ERR {label}: {e}")
        return None


# ═════════════════════════════════════════════════════════════
# 1. STAFF
# ═════════════════════════════════════════════════════════════
def create_staff():
    print("\n📋 Tạo nhân viên (staff-service:8001)...")
    staff_data = [
        {"username": "admin01", "email": "admin@bookstore.vn", "full_name": "Nguyễn Văn Admin", "phone": "0901000001", "role": "admin"},
        {"username": "nv_hoa", "email": "hoa@bookstore.vn", "full_name": "Trần Thị Hoa", "phone": "0901000002", "role": "staff"},
        {"username": "nv_minh", "email": "minh@bookstore.vn", "full_name": "Lê Văn Minh", "phone": "0901000003", "role": "staff"},
        {"username": "nv_lan", "email": "lan@bookstore.vn", "full_name": "Phạm Thị Lan", "phone": "0901000004", "role": "staff"},
        {"username": "nv_duc", "email": "duc@bookstore.vn", "full_name": "Hoàng Văn Đức", "phone": "0901000005", "role": "staff"},
    ]
    for s in staff_data:
        post(f"{STAFF_URL}/staff/", s, s["full_name"])


# ═════════════════════════════════════════════════════════════
# 2. MANAGER
# ═════════════════════════════════════════════════════════════
def create_managers():
    print("\n👔 Tạo quản lý (manager-service:8002)...")
    managers = [
        {"username": "mgr_sales", "email": "sales_mgr@bookstore.vn", "full_name": "Nguyễn Thị Mai", "phone": "0902000001", "department": "sales"},
        {"username": "mgr_inventory", "email": "inv_mgr@bookstore.vn", "full_name": "Trần Văn Hùng", "phone": "0902000002", "department": "inventory"},
        {"username": "mgr_ops", "email": "ops_mgr@bookstore.vn", "full_name": "Lê Thị Hương", "phone": "0902000003", "department": "operations"},
        {"username": "mgr_hr", "email": "hr_mgr@bookstore.vn", "full_name": "Phạm Văn Tùng", "phone": "0902000004", "department": "hr"},
    ]
    for m in managers:
        post(f"{MANAGER_URL}/managers/", m, m["full_name"])


# ═════════════════════════════════════════════════════════════
# 3. CUSTOMER
# ═════════════════════════════════════════════════════════════
def create_customers():
    print("\n👥 Tạo khách hàng (customer-service:8003)...")
    customers = [
        {"name": "Nguyễn Văn An", "email": "an@gmail.com", "phone": "0911000001", "address": "123 Lê Lợi, Q.1, TP.HCM"},
        {"name": "Trần Thị Bình", "email": "binh@gmail.com", "phone": "0911000002", "address": "456 Trần Hưng Đạo, Q.5, TP.HCM"},
        {"name": "Lê Văn Cường", "email": "cuong@gmail.com", "phone": "0911000003", "address": "789 Nguyễn Huệ, Q.1, TP.HCM"},
        {"name": "Phạm Thị Dung", "email": "dung@gmail.com", "phone": "0911000004", "address": "321 Hai Bà Trưng, Q.3, TP.HCM"},
        {"name": "Hoàng Văn Em", "email": "em@gmail.com", "phone": "0911000005", "address": "654 Điện Biên Phủ, Q.Bình Thạnh, TP.HCM"},
        {"name": "Vũ Thị Phương", "email": "phuong@gmail.com", "phone": "0911000006", "address": "12 Phạm Ngũ Lão, Q.1, TP.HCM"},
        {"name": "Đặng Văn Giang", "email": "giang@gmail.com", "phone": "0911000007", "address": "88 Bà Triệu, Hoàn Kiếm, Hà Nội"},
        {"name": "Bùi Thị Hạnh", "email": "hanh@gmail.com", "phone": "0911000008", "address": "45 Kim Mã, Ba Đình, Hà Nội"},
    ]
    results = []
    for c in customers:
        r = post(f"{CUSTOMER_URL}/customers/", c, c["name"])
        results.append(r)
    return results


# ═════════════════════════════════════════════════════════════
# 4. CATALOG (Categories)
# ═════════════════════════════════════════════════════════════
def create_categories():
    print("\n📂 Tạo danh mục (catalog-service:8004)...")
    categories = [
        {"name": "Văn học Việt Nam", "description": "Tiểu thuyết, truyện ngắn, thơ của các tác giả Việt Nam"},
        {"name": "Văn học nước ngoài", "description": "Tiểu thuyết, truyện ngắn dịch từ các nước"},
        {"name": "Kinh tế - Kinh doanh", "description": "Sách về kinh doanh, quản lý, tài chính, marketing"},
        {"name": "Khoa học - Công nghệ", "description": "Sách khoa học tự nhiên, công nghệ thông tin, lập trình"},
        {"name": "Tâm lý - Kỹ năng sống", "description": "Phát triển bản thân, tâm lý học, kỹ năng mềm"},
        {"name": "Thiếu nhi", "description": "Truyện thiếu nhi, sách giáo dục cho trẻ em"},
        {"name": "Giáo khoa - Tham khảo", "description": "Sách giáo khoa, sách tham khảo các cấp"},
        {"name": "Lịch sử - Địa lý", "description": "Sách về lịch sử Việt Nam và thế giới"},
    ]
    results = []
    for cat in categories:
        r = post(f"{CATALOG_URL}/categories/", cat, cat["name"])
        results.append(r)
    return results


# ═════════════════════════════════════════════════════════════
# 5. BOOKS
# ═════════════════════════════════════════════════════════════
def create_books():
    print("\n📚 Tạo sách (book-service:8005)...")
    books = [
        # Văn học Việt Nam (category_id=1)
        {"title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài", "isbn": "9786041234501", "price": "65000", "stock": 50, "category_id": 1,
         "description": "Câu chuyện phiêu lưu kinh điển của chú Dế Mèn qua nhiều vùng đất, gặp gỡ nhiều bạn bè.",
         "image_url": "https://picsum.photos/seed/book1/300/400"},
        {"title": "Số Đỏ", "author": "Vũ Trọng Phụng", "isbn": "9786041234502", "price": "89000", "stock": 35, "category_id": 1,
         "description": "Tiểu thuyết châm biếm xã hội Việt Nam những năm 1930, kể về nhân vật Xuân Tóc Đỏ.",
         "image_url": "https://picsum.photos/seed/book2/300/400"},
        {"title": "Truyện Kiều", "author": "Nguyễn Du", "isbn": "9786041234503", "price": "75000", "stock": 40, "category_id": 1,
         "description": "Kiệt tác văn học Việt Nam, kể về cuộc đời đầy sóng gió của nàng Kiều.",
         "image_url": "https://picsum.photos/seed/book3/300/400"},

        # Văn học nước ngoài (category_id=2)
        {"title": "Nhà Giả Kim", "author": "Paulo Coelho", "isbn": "9786041234504", "price": "79000", "stock": 60, "category_id": 2,
         "description": "Câu chuyện về chàng chăn cừu Santiago và hành trình đi tìm kho báu ở Kim tự tháp Ai Cập.",
         "image_url": "https://picsum.photos/seed/book4/300/400"},
        {"title": "Hoàng Tử Bé", "author": "Antoine de Saint-Exupéry", "isbn": "9786041234505", "price": "69000", "stock": 45, "category_id": 2,
         "description": "Câu chuyện đẹp về tình bạn, tình yêu và ý nghĩa cuộc sống từ hành tinh B612.",
         "image_url": "https://picsum.photos/seed/book5/300/400"},
        {"title": "Harry Potter và Hòn Đá Phù Thủy", "author": "J.K. Rowling", "isbn": "9786041234506", "price": "120000", "stock": 70, "category_id": 2,
         "description": "Cuốn đầu tiên trong series Harry Potter - cậu bé phù thủy nổi tiếng nhất thế giới.",
         "image_url": "https://picsum.photos/seed/book6/300/400"},
        {"title": "1984", "author": "George Orwell", "isbn": "9786041234507", "price": "95000", "stock": 30, "category_id": 2,
         "description": "Tiểu thuyết phản địa đàng kinh điển về một xã hội chuyên chế dưới sự kiểm soát của Big Brother.",
         "image_url": "https://picsum.photos/seed/book7/300/400"},

        # Kinh tế - Kinh doanh (category_id=3)
        {"title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "isbn": "9786041234508", "price": "86000", "stock": 80, "category_id": 3,
         "description": "Cuốn sách kinh điển về nghệ thuật giao tiếp và ứng xử trong cuộc sống.",
         "image_url": "https://picsum.photos/seed/book8/300/400"},
        {"title": "Cha Giàu Cha Nghèo", "author": "Robert Kiyosaki", "isbn": "9786041234509", "price": "110000", "stock": 55, "category_id": 3,
         "description": "Bài học về tài chính cá nhân từ hai người cha với hai tư duy khác nhau.",
         "image_url": "https://picsum.photos/seed/book9/300/400"},
        {"title": "Tư Duy Nhanh Và Chậm", "author": "Daniel Kahneman", "isbn": "9786041234510", "price": "159000", "stock": 25, "category_id": 3,
         "description": "Giải Nobel Kinh tế - Khám phá hai hệ thống tư duy của con người.",
         "image_url": "https://picsum.photos/seed/book10/300/400"},

        # Khoa học - Công nghệ (category_id=4)
        {"title": "Lược Sử Thời Gian", "author": "Stephen Hawking", "isbn": "9786041234511", "price": "135000", "stock": 20, "category_id": 4,
         "description": "Cuốn sách phổ biến khoa học nổi tiếng về vũ trụ, lỗ đen, Big Bang.",
         "image_url": "https://picsum.photos/seed/book11/300/400"},
        {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9786041234512", "price": "250000", "stock": 30, "category_id": 4,
         "description": "Cẩm nang viết mã sạch - kỹ năng quan trọng nhất cho lập trình viên.",
         "image_url": "https://picsum.photos/seed/book12/300/400"},
        {"title": "Sapiens: Lược Sử Loài Người", "author": "Yuval Noah Harari", "isbn": "9786041234513", "price": "189000", "stock": 40, "category_id": 4,
         "description": "Hành trình 70.000 năm từ loài vượn đến chủ nhân thế giới.",
         "image_url": "https://picsum.photos/seed/book13/300/400"},

        # Tâm lý - Kỹ năng sống (category_id=5)
        {"title": "Đời Ngắn Đừng Ngủ Dài", "author": "Robin Sharma", "isbn": "9786041234514", "price": "72000", "stock": 65, "category_id": 5,
         "description": "Những bài học thay đổi cuộc sống từ nhà diễn thuyết Robin Sharma.",
         "image_url": "https://picsum.photos/seed/book14/300/400"},
        {"title": "Nghĩ Giàu Làm Giàu", "author": "Napoleon Hill", "isbn": "9786041234515", "price": "98000", "stock": 50, "category_id": 5,
         "description": "Cuốn sách kinh điển về sức mạnh của tư duy tích cực và thành công.",
         "image_url": "https://picsum.photos/seed/book15/300/400"},
        {"title": "Sức Mạnh Của Thói Quen", "author": "Charles Duhigg", "isbn": "9786041234516", "price": "115000", "stock": 35, "category_id": 5,
         "description": "Hiểu cơ chế thói quen để thay đổi cuộc sống và sự nghiệp.",
         "image_url": "https://picsum.photos/seed/book16/300/400"},

        # Thiếu nhi (category_id=6)
        {"title": "Doraemon Tập 1", "author": "Fujiko F. Fujio", "isbn": "9786041234517", "price": "25000", "stock": 100, "category_id": 6,
         "description": "Tập 1 của bộ truyện Doraemon kinh điển.",
         "image_url": "https://picsum.photos/seed/book17/300/400"},
        {"title": "Conan Tập 1", "author": "Aoyama Gosho", "isbn": "9786041234518", "price": "25000", "stock": 90, "category_id": 6,
         "description": "Thám tử lừng danh Conan - tập đầu tiên.",
         "image_url": "https://picsum.photos/seed/book18/300/400"},

        # Giáo khoa (category_id=7)
        {"title": "Toán Cao Cấp Tập 1", "author": "Nguyễn Đình Trí", "isbn": "9786041234519", "price": "85000", "stock": 15, "category_id": 7,
         "description": "Giáo trình toán cao cấp dành cho sinh viên đại học kỹ thuật.",
         "image_url": "https://picsum.photos/seed/book19/300/400"},

        # Lịch sử (category_id=8)
        {"title": "Lịch Sử Việt Nam Bằng Tranh", "author": "Nhiều tác giả", "isbn": "9786041234520", "price": "55000", "stock": 45, "category_id": 8,
         "description": "Bộ sách lịch sử Việt Nam được minh họa sinh động bằng tranh.",
         "image_url": "https://picsum.photos/seed/book20/300/400"},
    ]
    results = []
    for b in books:
        r = post(f"{BOOK_URL}/books/", b, b["title"])
        results.append(r)
    return results


# ═════════════════════════════════════════════════════════════
# 6. CARTS
# ═════════════════════════════════════════════════════════════
def create_carts(customers):
    print("\n🛒 Tạo giỏ hàng (cart-service:8006)...")
    for c in customers:
        if c and "id" in c:
            # Create cart (ignore if already exists)
            post(f"{CART_URL}/carts/", {"customer_id": c["id"]}, f"Giỏ hàng khách #{c['id']}")
            # Add items to carts for first 3 customers
            if c["id"] <= 3:
                items_map = {
                    1: [{"book_id": 1, "quantity": 2}, {"book_id": 4, "quantity": 1}],
                    2: [{"book_id": 6, "quantity": 1}, {"book_id": 8, "quantity": 3}],
                    3: [{"book_id": 12, "quantity": 1}],
                }
                for item in items_map.get(c["id"], []):
                    post(f"{CART_URL}/carts/{c['id']}/items/", item, f"Cart item book#{item['book_id']}")


# ═════════════════════════════════════════════════════════════
# 7. SHIPMENTS (tạo trực tiếp cho demo)
# ═════════════════════════════════════════════════════════════
def create_shipments():
    print("\n🚚 Tạo đơn vận chuyển mẫu (ship-service:8008)...")
    shipments = [
        {"order_id": 1, "customer_id": 1, "address": "123 Lê Lợi, Q.1, TP.HCM", "method": "standard"},
        {"order_id": 2, "customer_id": 2, "address": "456 Trần Hưng Đạo, Q.5, TP.HCM", "method": "express"},
        {"order_id": 3, "customer_id": 1, "address": "123 Lê Lợi, Q.1, TP.HCM", "method": "overnight"},
    ]
    for s in shipments:
        post(f"{SHIP_URL}/shipments/reserve/", s, f"Shipment order#{s['order_id']}")


# ═════════════════════════════════════════════════════════════
# 8. PAYMENTS (tạo trực tiếp cho demo)
# ═════════════════════════════════════════════════════════════
def create_payments():
    print("\n💳 Tạo thanh toán mẫu (pay-service:8009)...")
    payments = [
        {"order_id": 1, "customer_id": 1, "amount": "209000", "method": "cash_on_delivery"},
        {"order_id": 2, "customer_id": 2, "amount": "378000", "method": "credit_card"},
        {"order_id": 3, "customer_id": 1, "amount": "250000", "method": "bank_transfer"},
    ]
    for p in payments:
        post(f"{PAY_URL}/payments/reserve/", p, f"Payment order#{p['order_id']}")
    # Confirm first 2 payments
    for oid in [1, 2]:
        post(f"{PAY_URL}/payments/confirm/", {"order_id": oid}, f"Confirm payment order#{oid}")


# ═════════════════════════════════════════════════════════════
# 9. ORDERS (tạo trực tiếp vào DB, không qua Saga)
# ═════════════════════════════════════════════════════════════
def create_orders():
    print("\n📦 Tạo đơn hàng mẫu (order-service:8007)...")
    orders = [
        {
            "customer_id": 1,
            "shipping_address": "123 Lê Lợi, Q.1, TP.HCM",
            "payment_method": "cash_on_delivery",
            "shipping_method": "standard",
            "items": [
                {"book_id": 1, "quantity": 2, "price": "65000"},
                {"book_id": 4, "quantity": 1, "price": "79000"},
            ]
        },
        {
            "customer_id": 2,
            "shipping_address": "456 Trần Hưng Đạo, Q.5, TP.HCM",
            "payment_method": "credit_card",
            "shipping_method": "express",
            "items": [
                {"book_id": 6, "quantity": 1, "price": "120000"},
                {"book_id": 8, "quantity": 3, "price": "86000"},
            ]
        },
        {
            "customer_id": 1,
            "shipping_address": "123 Lê Lợi, Q.1, TP.HCM",
            "payment_method": "bank_transfer",
            "shipping_method": "overnight",
            "items": [
                {"book_id": 12, "quantity": 1, "price": "250000"},
            ]
        },
        {
            "customer_id": 3,
            "shipping_address": "789 Nguyễn Huệ, Q.1, TP.HCM",
            "payment_method": "e_wallet",
            "shipping_method": "standard",
            "items": [
                {"book_id": 13, "quantity": 1, "price": "189000"},
                {"book_id": 15, "quantity": 1, "price": "98000"},
            ]
        },
    ]
    for o in orders:
        post(f"{ORDER_URL}/orders/", o, f"Order customer#{o['customer_id']}")


# ═════════════════════════════════════════════════════════════
# 10. REVIEWS
# ═════════════════════════════════════════════════════════════
def create_reviews():
    print("\n⭐ Tạo đánh giá (comment-rate-service:8010)...")
    reviews = [
        {"customer_id": 1, "book_id": 1, "rating": 5, "comment": "Sách rất hay, tuổi thơ của mình luôn gắn liền với Dế Mèn!"},
        {"customer_id": 2, "book_id": 1, "rating": 4, "comment": "Văn phong đẹp, nội dung sâu sắc."},
        {"customer_id": 3, "book_id": 1, "rating": 5, "comment": "Kiệt tác của văn học thiếu nhi Việt Nam."},
        {"customer_id": 1, "book_id": 4, "rating": 5, "comment": "Nhà Giả Kim thay đổi cách nhìn cuộc sống của tôi."},
        {"customer_id": 4, "book_id": 4, "rating": 4, "comment": "Câu chuyện đẹp và ý nghĩa."},
        {"customer_id": 2, "book_id": 6, "rating": 5, "comment": "Harry Potter quá tuyệt vời! Đọc mãi không chán."},
        {"customer_id": 5, "book_id": 6, "rating": 5, "comment": "Thế giới phép thuật rất cuốn hút."},
        {"customer_id": 3, "book_id": 6, "rating": 4, "comment": "Bản dịch tốt, giữ được tinh thần nguyên tác."},
        {"customer_id": 1, "book_id": 8, "rating": 5, "comment": "Cuốn sách mọi người nên đọc ít nhất một lần."},
        {"customer_id": 6, "book_id": 8, "rating": 4, "comment": "Bài học giao tiếp rất thực tế."},
        {"customer_id": 4, "book_id": 12, "rating": 5, "comment": "Clean Code là sách gối đầu giường của dev!"},
        {"customer_id": 5, "book_id": 12, "rating": 4, "comment": "Nội dung tốt, giúp cải thiện kỹ năng coding."},
        {"customer_id": 2, "book_id": 13, "rating": 5, "comment": "Sapiens mở ra góc nhìn mới về lịch sử loài người."},
        {"customer_id": 7, "book_id": 5, "rating": 5, "comment": "Hoàng Tử Bé - triết lý sâu sắc trong câu chuyện giản đơn."},
        {"customer_id": 8, "book_id": 7, "rating": 4, "comment": "1984 rất đáng suy ngẫm, đặc biệt trong thời đại số."},
        {"customer_id": 3, "book_id": 9, "rating": 4, "comment": "Bài học tài chính rất hữu ích cho người trẻ."},
        {"customer_id": 6, "book_id": 11, "rating": 5, "comment": "Stephen Hawking giải thích vũ trụ một cách dễ hiểu."},
        {"customer_id": 7, "book_id": 14, "rating": 4, "comment": "Sách nhẹ nhàng, nhiều bài học hay."},
        {"customer_id": 8, "book_id": 2, "rating": 5, "comment": "Số Đỏ - văn phong châm biếm sắc bén của Vũ Trọng Phụng."},
        {"customer_id": 1, "book_id": 3, "rating": 5, "comment": "Truyện Kiều là di sản văn học vô giá."},
    ]
    for r in reviews:
        post(f"{COMMENT_URL}/reviews/", r, f"Review book#{r['book_id']} by customer#{r['customer_id']}")


# ═════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("🏪 TẠO DỮ LIỆU MẪU CHO BOOKSTORE MICROSERVICES")
    print("=" * 60)

    # Check connectivity
    print("\n🔗 Kiểm tra kết nối các service...")
    services_ok = True
    for name, url in [
        ("staff", STAFF_URL), ("manager", MANAGER_URL), ("customer", CUSTOMER_URL),
        ("catalog", CATALOG_URL), ("book", BOOK_URL), ("cart", CART_URL),
        ("order", ORDER_URL), ("ship", SHIP_URL), ("pay", PAY_URL),
        ("comment-rate", COMMENT_URL),
    ]:
        try:
            r = requests.get(f"{url}/health/", timeout=5)
            print(f"  ✅ {name:20s} OK")
        except Exception:
            print(f"  ❌ {name:20s} KHÔNG KẾT NỐI ĐƯỢC")
            services_ok = False

    if not services_ok:
        ans = input("\nMột số service không kết nối được. Tiếp tục? (y/n): ")
        if ans.lower() != 'y':
            sys.exit(0)

    # Create data in order
    create_staff()
    create_managers()
    customers = create_customers()
    create_categories()
    books = create_books()

    time.sleep(1)  # Small delay to ensure data is committed

    create_carts(customers)
    create_orders()
    create_shipments()
    create_payments()
    create_reviews()

    print("\n" + "=" * 60)
    print(f"✅ HOÀN TẤT! Thành công: {created['success']} | Thất bại: {created['failed']}")
    print("=" * 60)
    print("\n📌 Truy cập web: http://localhost:8080")
    print("📌 Đăng nhập thử: email = an@gmail.com")
    print("📌 Các API endpoint:")
    print("   - Staff:      http://localhost:8001/api/staff/")
    print("   - Manager:    http://localhost:8002/api/managers/")
    print("   - Customer:   http://localhost:8003/api/customers/")
    print("   - Catalog:    http://localhost:8004/api/categories/")
    print("   - Book:       http://localhost:8005/api/books/")
    print("   - Cart:       http://localhost:8006/api/carts/")
    print("   - Order:      http://localhost:8007/api/orders/")
    print("   - Ship:       http://localhost:8008/api/shipments/")
    print("   - Payment:    http://localhost:8009/api/payments/")
    print("   - Review:     http://localhost:8010/api/reviews/")
