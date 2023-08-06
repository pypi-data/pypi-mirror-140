from typing import List


class PatternFormatter:
    @staticmethod
    def format(pattern: str) -> List[str]:
        fields = ["feature_id", "description"]
        output = []
        for field in fields:
            query = PatternFormatter._format(field, pattern)
            output.append(query)
        return output

    @staticmethod
    def _format(field: str, pattern: str) -> str:
        """Ref: https://googleapis.dev/python/aiplatform/latest/aiplatform_v1/featurestore_service.html"""
        output = pattern
        if ":" not in pattern:
            # Assume the query is for feature name
            output = f"{field}: {pattern}"

        return output
