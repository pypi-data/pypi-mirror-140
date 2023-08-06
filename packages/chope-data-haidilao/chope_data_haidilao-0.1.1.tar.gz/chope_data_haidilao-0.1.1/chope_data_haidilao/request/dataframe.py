from typing import List
import pandas as pd
from datetime import datetime


class RequestDataframeBuilder:
    def __init__(self):
        pass

    def build(self, entity_type: str, entities: List[str]) -> pd.DataFrame:
        request_df = pd.DataFrame(
            data={entity_type: entities, "timestamp": datetime.now()}
        )
        return request_df
