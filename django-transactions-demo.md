
# 💾 Django Transaction Demo

سلام دوستان 👋  
در این پروژه قصد داریم نحوه مدیریت تراکنش‌ها در Django رو به‌صورت عملی بررسی کنیم.  
📌 توضیحات کامل در مورد مفهوم تراکنش، ویژگی‌های ACID، مدیریت تراکنش‌ها و مثال‌های کاربردی رو می‌تونید در مقاله لینکدین من بخونید:  
🔗 [مطالعه مقاله در لینکدین](https://www.linkedin.com/pulse/%25D8%25AA%25D8%25B1%25D8%25A7%25DA%25A9%25D9%2586%25D8%25B4%25D9%2587%25D8%25A7-transactions-%25D8%25AF%25D8%25B1-%25D8%25AF%25DB%258C%25D8%25AA%25D8%25A7%25D8%25A8%25DB%258C%25D8%25B3-%25D9%2588-%25D8%25AC%25D9%2586%25DA%25AF%25D9%2588-abbasali-rezaei-i3xuf)

---

## 📦 سناریوی عملی

فرض کنید یک کاربر داره سفارشی ثبت می‌کنه:

1. ثبت سفارش در جدول `Order`  
2. کم‌کردن موجودی کالا از جدول `Product`  
3. ثبت آیتم‌ها در جدول `OrderItem`

هدف ما اینه که این عملیات به‌صورت امن، اتمیک و بدون خطاهای همزمانی انجام بشه.

---

## 🧪 مدل‌های استفاده‌شده

```python
# models.py

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)

class Order(models.Model):
    user = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
```

---

## ✅ سناریو اول – تراکنش اتوماتیک با `atomic()`، به همراه `select_for_update()` و `savepoint()`

📘 **هدف:**
- استفاده از تراکنش اتوماتیک برای اطمینان از اتمیک بودن عملیات  
- قفل کردن محصولات با `select_for_update()`  
- ذخیره فقط آیتم‌هایی که موجودی کافی دارند، بقیه حذف بشن

```python
from django.db import transaction
from .models import Product, Order, OrderItem

def create_order_atomic(user, product_items):
    """
    product_items = [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 5},
    ]
    """
    order = None
    with transaction.atomic():
        order = Order.objects.create(user=user)
        for item in product_items:
            savepoint = transaction.savepoint()
            try:
                product = Product.objects.select_for_update().get(id=item["product_id"])
                if product.stock < item["quantity"]:
                    raise ValueError("Insufficient stock")
                product.stock -= item["quantity"]
                product.save()
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"]
                )
            except Exception as e:
                print(f"Skipping item due to error: {e}")
                transaction.savepoint_rollback(savepoint)
    return order
```

---

## 🟠 سناریو دوم – تراکنش دستی با `set_autocommit(False)`، همراه با `select_for_update()` و `savepoint()`

📘 **هدف:**
- کنترل کامل روی `commit()` و `rollback()`  
- همان رفتار بالا، ولی با مدیریت دستی تراکنش

```python
from django.db import transaction
from .models import Product, Order, OrderItem

def create_order_manual(user, product_items):
    """
    product_items = [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 5},
    ]
    """
    order = None
    try:
        transaction.set_autocommit(False)
        order = Order.objects.create(user=user)
        for item in product_items:
            savepoint = transaction.savepoint()
            try:
                product = Product.objects.select_for_update().get(id=item["product_id"])
                if product.stock < item["quantity"]:
                    raise ValueError("Insufficient stock")
                product.stock -= item["quantity"]
                product.save()
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"]
                )
            except Exception as e:
                print(f"Skipping item due to error: {e}")
                transaction.savepoint_rollback(savepoint)
        transaction.commit()
    except Exception as e:
        print(f"Rolling back entire order: {e}")
        transaction.rollback()
    finally:
        transaction.set_autocommit(True)
    return order
```

---

## 🎯 جمع‌بندی

در این پروژه یاد گرفتیم چطور با استفاده از Django:

- تراکنش‌ها رو به‌صورت اتوماتیک یا دستی مدیریت کنیم  
- از `select_for_update()` برای جلوگیری از Race Condition استفاده کنیم  
- با `savepoint()` فقط بخش‌هایی از تراکنش رو rollback کنیم  
- عملیات روی دیتابیس رو امن، تمیز و قابل اعتماد نگه داریم

---


📌 برای مطالعه توضیحات کامل، به مقاله لینکدین من سر بزنید:  
🔗 [مطالعه مقاله در لینکدین](https://www.linkedin.com/pulse/%25D8%25AA%25D8%25B1%25D8%25A7%25DA%25A9%25D9%2586%25D8%25B4%25D9%2587%25D8%25A7-transactions-%25D8%25AF%25D8%25B1-%25D8%25AF%25DB%258C%25D8%25AA%25D8%25A7%25D8%25A8%25DB%258C%25D8%25B3-%25D9%2588-%25D8%25AC%25D9%2586%25DA%25AF%25D9%2588-abbasali-rezaei-i3xuf)
