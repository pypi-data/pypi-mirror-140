import logging

logger = logging.getLogger(__name__)
from typing import List


class PatternFormatter:
    @staticmethod
    def format(pattern: str) -> List[str]:
        output = []
        if ":" not in pattern:
            # Assume the query is for feature name
            fields = ["feature_id", "description"]
            for field in fields:
                query = PatternFormatter._format(field, pattern)
                output.append(query)
        else:
            output.append(pattern)
        return output

    @staticmethod
    def _format(field: str, pattern: str) -> str:
        """Ref: https://googleapis.dev/python/aiplatform/latest/aiplatform_v1/featurestore_service.html"""
        output = f"{field}: {pattern}"

        return output
