import ninja
from authentication.auth import AuthBearer

api = ninja.NinjaAPI(auth = AuthBearer())

api.add_router("admin/", "api.routers.admin_router.router", tags = ["Admin"])
api.add_router("user/", "api.routers.user_router.router", tags = ["User"])
api.add_router("data/", "api.routers.knowledge_router.router", tags = ["Knowledge graph"])
api.add_router("ontology/", "api.routers.ontology_router.router", tags = ["Ontology"])
api.add_router("debug/", "api.routers.debug_router.router", tags = ["Debug"])
api.add_router("debug-mw/", "api.routers.debug_mw_router.router", tags = ["Debug-MW"])
api.add_router("review/", "api.routers.reviewer_router.router", tags = ["Reviewer"])
api.add_router("study/", "api.routers.study_router.router", tags=["Study"])
api.add_router("data/", "api.routers.data_router.router", tags = ["Data"])
api.add_router("system/", "api.routers.system_router.router", tags = ["System"])
