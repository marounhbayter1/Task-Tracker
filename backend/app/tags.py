from typing import Any


MAX_TAG_COUNT = 10
MAX_TAG_LENGTH = 30


def normalize_tags(
    value: Any,
    *,
    max_count: int | None = MAX_TAG_COUNT,
    max_length: int | None = MAX_TAG_LENGTH,
) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, list):
        raise ValueError("Tags must be provided as a list of strings")

    normalized: list[str] = []

    for item in value:
        if not isinstance(item, str):
            raise ValueError("Each tag must be a string")

        tag = item.strip()
        if not tag:
            raise ValueError("Tag values must not be blank")

        if max_length is not None and len(tag) > max_length:
            raise ValueError("Tag values must be 30 characters or fewer")

        normalized.append(tag)

    if max_count is not None and len(normalized) > max_count:
        raise ValueError("Tags must be 10 or fewer")

    return normalized
