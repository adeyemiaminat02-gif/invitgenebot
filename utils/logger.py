import logging
from utils.config import Config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
)

logger = logging.getLogger("InVitGeneBot")
