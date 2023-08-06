from typing import List
import logging

logger = logging.getLogger(__name__)

from .merchant import MerchantList


def get_entity_list(entity_type: str) -> List[str]:
    if entity_type.lower() == "merchant":
        getter = MerchantList()
    else:
        logger.error(f"Not found entity_type = {entity_type}!")

    return getter.get()
