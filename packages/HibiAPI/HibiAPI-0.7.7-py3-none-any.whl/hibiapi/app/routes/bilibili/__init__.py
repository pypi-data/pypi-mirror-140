from hibiapi.api.bilibili import BilibiliConstants
from hibiapi.utils.routing import SlashRouter

from .v2 import router as RouterV2
from .v3 import router as RouterV3

__mount__, __config__ = "bilibili", BilibiliConstants.CONFIG
router = SlashRouter()
router.include_router(RouterV2, prefix="/v2")
router.include_router(RouterV3, prefix="/v3")
