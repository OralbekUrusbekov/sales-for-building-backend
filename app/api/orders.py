from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbDep, OptionalUser, StaffUser
from app.models import Order, OrderItem, Product
from app.schemas.common import Page
from app.schemas.orders import OrderCreate, OrderOut, OrderStatusIn
from app.services.notifier import notify
from app.services.numbering import next_order_number

router = APIRouter()

SHIPPING_FLAT = 2500


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, db: DbDep, user: OptionalUser) -> Order:
    product_ids = [i.product_id for i in data.items]
    products = {
        p.id: p
        for p in await db.scalars(select(Product).where(Product.id.in_(product_ids)))
    }
    missing = set(product_ids) - set(products)
    if missing:
        raise HTTPException(400, f"Unknown product ids: {sorted(missing)}")

    items: list[OrderItem] = []
    subtotal = 0
    for line in data.items:
        product = products[line.product_id]
        subtotal += product.price * line.quantity
        items.append(
            OrderItem(
                product_id=product.id,
                name=product.name,
                price=product.price,
                quantity=line.quantity,
                unit=product.unit,
            )
        )

    shipping = 0 if data.delivery == "pickup" else SHIPPING_FLAT
    order = Order(
        number=await next_order_number(db),
        user_id=user.id if user else None,
        customer_name=data.customer_name,
        phone=data.phone,
        address=data.address,
        delivery=data.delivery,
        payment=data.payment,
        comment=data.comment,
        status="new",
        subtotal=subtotal,
        shipping=shipping,
        total=subtotal + shipping,
        items=items,
    )
    db.add(order)
    await notify(
        db,
        type="order",
        title="Новый заказ материалов",
        body=f"{order.number} · {data.customer_name} · {order.total} ₸",
    )
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/mine", response_model=list[OrderOut])
async def my_orders(db: DbDep, user: CurrentUser) -> list[Order]:
    rows = await db.scalars(
        select(Order)
        .where(Order.user_id == user.id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return list(rows)


@router.get("", response_model=Page[OrderOut])
async def list_orders(
    db: DbDep,
    _: StaffUser,
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=500),
) -> Page[OrderOut]:
    stmt = select(Order).options(selectinload(Order.items))
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(Order.customer_name.ilike(like) | Order.phone.ilike(like) | Order.number.ilike(like))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        await db.scalars(
            stmt.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        )
    )
    return Page.build(
        [OrderOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.get("/{number}", response_model=OrderOut)
async def get_order(number: str, db: DbDep, user: CurrentUser) -> Order:
    order = await db.scalar(
        select(Order).where(Order.number == number).options(selectinload(Order.items))
    )
    if not order:
        raise HTTPException(404, "Order not found")
    if user.role == "customer" and order.user_id != user.id:
        raise HTTPException(403, "Not your order")
    return order


@router.patch("/{number}/status", response_model=OrderOut)
async def set_order_status(number: str, data: OrderStatusIn, db: DbDep, _: StaffUser) -> Order:
    order = await db.scalar(
        select(Order).where(Order.number == number).options(selectinload(Order.items))
    )
    if not order:
        raise HTTPException(404, "Order not found")
    order.status = data.status
    await db.commit()
    await db.refresh(order)
    return order
