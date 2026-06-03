from fastapi import APIRouter

from app.api.routes import admin, assistant, audits, auth, health, integrations, memory, messages, rag, tasks, webhooks

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(audits.router, prefix="/audits", tags=["audits"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
