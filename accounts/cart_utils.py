from .models import Cart


def get_or_create_cart(request):
    """
    এই function login user অথবা guest user
    দুইজনের cart handle করবে
    """

    # ✅ যদি user login করা থাকে
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )
        return cart

    # ✅ guest user হলে session create করো
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # session দিয়ে cart বের বা create
    cart, created = Cart.objects.get_or_create(
        session_key=session_key
    )

    return cart