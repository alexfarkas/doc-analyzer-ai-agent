from pydantic_core import Url


def normalize_url(url: str) -> str:
    try:
        return str(Url(url))
    except ValueError:
        return url
