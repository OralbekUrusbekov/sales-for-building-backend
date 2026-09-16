from fastapi import APIRouter

from app.api import (
    admin,
    auth,
    blog,
    calculator,
    catalog,
    crm,
    leads,
    manage,
    masters,
    orders,
    reviews,
    services,
    settings as settings_api,
    telegram,
    uploads,
    vacancies,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
api_router.include_router(masters.router, prefix="/masters", tags=["masters"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
api_router.include_router(blog.router, prefix="/blog", tags=["blog"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(manage.router, prefix="/manage", tags=["manage"])
api_router.include_router(settings_api.router, prefix="/settings", tags=["settings"])
api_router.include_router(settings_api.manage_router, prefix="/manage", tags=["manage"])
api_router.include_router(uploads.router, prefix="/manage/uploads", tags=["manage"])
