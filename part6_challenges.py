from decimal import Decimal
from django.db import models
from django.db.models import Case, F, Q, When
from core.models import Category, Product

# --- Setup sample products so you can test all 4 challenges ---
electronics, _ = Category.objects.get_or_create(name="Electronics")
gadgets, _ = Category.objects.get_or_create(name="Gadgets")

p1, _ = Product.objects.get_or_create(
    name="Gaming Laptop",
    defaults={
        "category": electronics,
        "price": Decimal("35000.00"),
        "max_allowed_price": Decimal("40000.00"),
        "stock_quantity": 5,
        "reorder_level": 10,
        "is_promotional": False,
        "status": "NORMAL",
        "warehouse_country": "China",
    },
)

p2, _ = Product.objects.get_or_create(
    name="Smart Watch",
    defaults={
        "category": gadgets,
        "price": Decimal("9000.00"),
        "max_allowed_price": Decimal("10000.00"),
        "stock_quantity": 15,
        "reorder_level": 10,
        "is_promotional": True,
        "status": "DISCOUNTED",
        "warehouse_country": "Thailand",
    },
)

# --- Challenge 1: Advanced Conditional Search (Q Objects) ---
challenge_1 = Product.objects.filter(
    (Q(category__name="Electronics") & Q(price__gt=Decimal("10000")))
    | (Q(status="DISCOUNTED") & ~Q(warehouse_country="China"))
)
print("Challenge 1:", list(challenge_1))

# --- Challenge 2: Dynamic Stock Threshold Alert (F + Q) ---
challenge_2 = Product.objects.filter(
    Q(stock_quantity__lte=F("reorder_level"))
    | (Q(is_promotional=True) & Q(stock_quantity__lt=F("reorder_level") * 2))
)
print("Challenge 2:", list(challenge_2))

# --- Challenge 3: Atomic 15% Price Increase with Ceiling (F + Case/When) ---
price_field = models.DecimalField(max_digits=10, decimal_places=2)
factor = Decimal("1.15")

Product.objects.filter(category__name="Gadgets").update(
    price=Case(
        When(
            price__gt=F("max_allowed_price") / factor,
            then=F("max_allowed_price"),
        ),
        default=F("price") * factor,
        output_field=price_field,
    )
)
for prod in Product.objects.filter(category__name="Gadgets"):
    print("Challenge 3 Updated Price:", prod.name, prod.price)

# --- Challenge 4: Atomic Purchase Guard (Race Condition Prevention) ---
X = 3  # Quantity to buy
updated_count = Product.objects.filter(
    id=p1.id,
    stock_quantity__gte=X,
).update(
    stock_quantity=F("stock_quantity") - X,
    total_sold=F("total_sold") + X,
    total_revenue=F("total_revenue") + (X * F("price")),
)
print("Challenge 4 Purchase Succeeded:", updated_count == 1)