from fastapi import APIRouter

from .v1 import (
    admin,
    agents,
    analytics,
    auth,
    billing,
    flows,
    jobs,
    knowledge,
    mcp,
    public,
    tickets,
    tools,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(admin.router)
api_router.include_router(knowledge.router)
api_router.include_router(tickets.router)
api_router.include_router(flows.router)
api_router.include_router(agents.router)
api_router.include_router(tools.router)
api_router.include_router(mcp.router)
api_router.include_router(analytics.router)
api_router.include_router(billing.router)
api_router.include_router(jobs.router)
api_router.include_router(public.router)

