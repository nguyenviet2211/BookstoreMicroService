def cart_count(request):
    """Add cart item count to all templates."""
    count = 0
    cart_id = request.session.get("cart_id")
    if cart_id:
        from .services import cart_client
        cart = cart_client.get(f"/api/carts/{cart_id}/")
        if cart and "items" in cart:
            count = sum(item.get("quantity", 0) for item in cart["items"])
    return {"cart_item_count": count}
