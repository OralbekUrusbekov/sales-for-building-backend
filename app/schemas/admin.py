from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    title: str
    body: str
    is_read: bool
    created_at: datetime


class DashboardOut(BaseModel):
    leads_new: int
    leads_total: int
    orders_new: int
    orders_total: int
    revenue_done: int
    deals_open: int
    deals_pipeline: int
    reviews_pending: int
    products: int
    masters: int
