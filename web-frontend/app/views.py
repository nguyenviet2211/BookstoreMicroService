from django.shortcuts import render, redirect
from django.contrib import messages
from .services import (
    book_client, catalog_client, customer_client, cart_client,
    order_client, ship_client, pay_client, comment_client, recommender_client,
)


# ─── Helpers ──────────────────────────────────────────────
def _get_customer(request):
    cid = request.session.get("customer_id")
    if not cid:
        return None
    return customer_client.get(f"/api/customers/{cid}/")


def _get_cart(request):
    cart_id = request.session.get("cart_id")
    if not cart_id:
        return None
    return cart_client.get(f"/api/carts/{cart_id}/")


# ─── Home ─────────────────────────────────────────────────
def home(request):
    books = book_client.get("/api/books/") or []
    categories = catalog_client.get("/api/categories/") or []
    return render(request, "home.html", {
        "books": books[:8],
        "categories": categories,
    })


# ─── Books ────────────────────────────────────────────────
def book_list(request):
    q = request.GET.get("q", "")
    cat = request.GET.get("category", "")
    params = {}
    if cat:
        params["category_id"] = cat
    books = book_client.get("/api/books/", params=params) or []
    if q:
        q_lower = q.lower()
        books = [b for b in books if q_lower in b.get("title", "").lower()
                 or q_lower in b.get("author", "").lower()]
    categories = catalog_client.get("/api/categories/") or []
    return render(request, "books/list.html", {
        "books": books,
        "categories": categories,
        "query": q,
        "selected_category": cat,
    })


def book_detail(request, book_id):
    book = book_client.get(f"/api/books/{book_id}/")
    if not book:
        messages.error(request, "Không tìm thấy sách.")
        return redirect("book_list")
    reviews = comment_client.get("/api/reviews/", params={"book_id": book_id}) or []
    avg = comment_client.get(f"/api/reviews/book/{book_id}/average/")
    return render(request, "books/detail.html", {
        "book": book,
        "reviews": reviews,
        "avg_rating": avg,
    })


def category_books(request, cat_id):
    category = catalog_client.get(f"/api/categories/{cat_id}/")
    books = book_client.get("/api/books/", params={"category_id": cat_id}) or []
    categories = catalog_client.get("/api/categories/") or []
    return render(request, "books/list.html", {
        "books": books,
        "categories": categories,
        "selected_category": str(cat_id),
        "current_category": category,
        "query": "",
    })


# ─── Account ──────────────────────────────────────────────
def register(request):
    if request.method == "POST":
        data = {
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "phone": request.POST.get("phone", ""),
            "address": request.POST.get("address", ""),
        }
        result = customer_client.post("/api/customers/", json=data)
        if result and "id" in result:
            request.session["customer_id"] = result["id"]
            request.session["customer_name"] = result["name"]
            # Find cart
            cart = cart_client.get(f"/api/carts/{result['id']}/")
            if cart and "id" in cart:
                request.session["cart_id"] = result["id"]
            messages.success(request, "Đăng ký thành công!")
            return redirect("home")
        messages.error(request, "Đăng ký thất bại. Email có thể đã tồn tại.")
    return render(request, "account/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        customers = customer_client.get("/api/customers/") or []
        found = next((c for c in customers if c.get("email") == email), None)
        if found:
            request.session["customer_id"] = found["id"]
            request.session["customer_name"] = found["name"]
            request.session["cart_id"] = found["id"]
            messages.success(request, f"Xin chào, {found['name']}!")
            return redirect("home")
        messages.error(request, "Email không tồn tại.")
    return render(request, "account/login.html")


def logout_view(request):
    request.session.flush()
    messages.info(request, "Đã đăng xuất.")
    return redirect("home")


def account(request):
    customer = _get_customer(request)
    if not customer:
        return redirect("login")
    cid = request.session["customer_id"]
    orders = order_client.get("/api/orders/", params={"customer_id": cid}) or []
    return render(request, "account/profile.html", {
        "customer": customer,
        "orders": orders,
    })


# ─── Cart ─────────────────────────────────────────────────
def cart_view(request):
    if not request.session.get("customer_id"):
        messages.warning(request, "Vui lòng đăng nhập để xem giỏ hàng.")
        return redirect("login")
    cart = _get_cart(request)
    items = cart.get("items", []) if cart else []
    # Enrich items with book info
    enriched = []
    total = 0
    for item in items:
        book = book_client.get(f"/api/books/{item['book_id']}/")
        if book:
            item["book"] = book
            item["subtotal"] = float(book.get("price", 0)) * item.get("quantity", 0)
            total += item["subtotal"]
        enriched.append(item)
    return render(request, "cart/cart.html", {"items": enriched, "total": total})


def cart_add(request, book_id):
    if not request.session.get("customer_id"):
        messages.warning(request, "Vui lòng đăng nhập.")
        return redirect("login")
    cart_id = request.session.get("cart_id")
    qty = int(request.POST.get("quantity", 1))
    # Check if book already in cart, update qty
    cart = _get_cart(request)
    if cart:
        existing = next((i for i in cart.get("items", []) if i["book_id"] == book_id), None)
        if existing:
            new_qty = existing["quantity"] + qty
            cart_client.put(f"/api/carts/{cart_id}/items/{existing['id']}/", json={"quantity": new_qty})
            messages.success(request, "Đã cập nhật giỏ hàng.")
            return redirect("cart")
    cart_client.post(f"/api/carts/{cart_id}/items/", json={"book_id": book_id, "quantity": qty})
    messages.success(request, "Đã thêm vào giỏ hàng.")
    return redirect("cart")


def cart_update(request, item_id):
    cart_id = request.session.get("cart_id")
    qty = int(request.POST.get("quantity", 1))
    if qty < 1:
        return cart_remove(request, item_id)
    cart_client.put(f"/api/carts/{cart_id}/items/{item_id}/", json={"quantity": qty})
    return redirect("cart")


def cart_remove(request, item_id):
    cart_id = request.session.get("cart_id")
    cart_client.delete(f"/api/carts/{cart_id}/items/{item_id}/")
    messages.info(request, "Đã xóa khỏi giỏ hàng.")
    return redirect("cart")


# ─── Checkout & Orders ────────────────────────────────────
def checkout(request):
    if not request.session.get("customer_id"):
        return redirect("login")
    cart = _get_cart(request)
    items = cart.get("items", []) if cart else []
    if not items:
        messages.warning(request, "Giỏ hàng trống.")
        return redirect("cart")

    # Enrich items
    enriched = []
    total = 0
    for item in items:
        book = book_client.get(f"/api/books/{item['book_id']}/")
        if book:
            item["book"] = book
            item["subtotal"] = float(book.get("price", 0)) * item.get("quantity", 0)
            total += item["subtotal"]
        enriched.append(item)

    if request.method == "POST":
        cid = request.session["customer_id"]
        order_items = []
        for item in enriched:
            if "book" in item:
                order_items.append({
                    "book_id": item["book_id"],
                    "quantity": item["quantity"],
                    "price": str(item["book"]["price"]),
                })
        order_data = {
            "customer_id": cid,
            "shipping_address": request.POST.get("address", ""),
            "payment_method": request.POST.get("payment_method", "cash_on_delivery"),
            "shipping_method": request.POST.get("shipping_method", "standard"),
            "items": order_items,
        }
        result = order_client.post("/api/orders/", json=order_data)
        if result and "id" in result:
            # Clear cart
            cart_id = request.session.get("cart_id")
            cart_client.delete(f"/api/carts/{cart_id}/")
            messages.success(request, f"Đặt hàng thành công! Mã đơn: #{result['id']}")
            return redirect("order_detail", order_id=result["id"])
        messages.error(request, "Đặt hàng thất bại. Vui lòng thử lại.")

    customer = _get_customer(request)
    return render(request, "cart/checkout.html", {
        "items": enriched,
        "total": total,
        "customer": customer,
    })


def order_list(request):
    if not request.session.get("customer_id"):
        return redirect("login")
    cid = request.session["customer_id"]
    orders = order_client.get("/api/orders/", params={"customer_id": cid}) or []
    return render(request, "orders/list.html", {"orders": orders})


def order_detail(request, order_id):
    order = order_client.get(f"/api/orders/{order_id}/")
    if not order:
        messages.error(request, "Không tìm thấy đơn hàng.")
        return redirect("order_list")
    # Enrich items with book info
    for item in order.get("items", []):
        book = book_client.get(f"/api/books/{item['book_id']}/")
        if book:
            item["book"] = book
    # Get shipment & payment
    shipments = ship_client.get("/api/shipments/", params={"order_id": order_id}) or []
    payments = pay_client.get("/api/payments/", params={"order_id": order_id}) or []
    return render(request, "orders/detail.html", {
        "order": order,
        "shipment": shipments[0] if shipments else None,
        "payment": payments[0] if payments else None,
    })


# ─── Reviews ──────────────────────────────────────────────
def add_review(request, book_id):
    if not request.session.get("customer_id"):
        messages.warning(request, "Vui lòng đăng nhập để đánh giá.")
        return redirect("login")
    if request.method == "POST":
        data = {
            "customer_id": request.session["customer_id"],
            "book_id": book_id,
            "rating": int(request.POST.get("rating", 5)),
            "comment": request.POST.get("comment", ""),
        }
        result = comment_client.post("/api/reviews/", json=data)
        if result:
            messages.success(request, "Đánh giá thành công!")
        else:
            messages.error(request, "Không thể gửi đánh giá.")
    return redirect("book_detail", book_id=book_id)
