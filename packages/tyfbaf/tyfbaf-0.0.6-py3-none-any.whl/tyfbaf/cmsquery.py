from typing import Any, Callable, Optional
from .http import post, post_full_uri


def select(query: str, token: str):
    return post("/v1/cmsquery", body={"query": query}, token=token)


def select_all_entries(
    query: str, token: str, mapping: Optional[Callable[[Any], Any]] = None
):
    response = select(query=query, token=token)

    if "error_code" in response.keys():
        raise ValueError(response["message"])

    result = (
        response["entries"]
        if mapping is None
        else [mapping(entry) for entry in response["entries"]]
    )

    if "next" not in response.keys():
        return result

    uri = response["next"]["__deferred"]["uri"]
    last_uri = response["last"]["__deferred"]["uri"]

    while True:
        response = post_full_uri(uri, body={"query": query}, token=token)
        result.extend(
            response["entries"]
            if mapping is None
            else [mapping(entry) for entry in response["entries"]]
        )

        if response["__metadata"]["uri"] == last_uri:
            break
        else:
            uri = response["next"]["__deferred"]["uri"]

    return result
