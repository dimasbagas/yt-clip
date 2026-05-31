from config import NVENC_ENABLED, NVENC_AVAILABLE
import logging

logger = logging.getLogger(__name__)


def check_nvenc() -> bool:
    return NVENC_AVAILABLE

