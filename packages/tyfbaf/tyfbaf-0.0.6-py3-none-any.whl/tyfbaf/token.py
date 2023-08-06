from typing import Optional
from .http import post


def request(username: str, password: str) -> Optional[str]:
    response = post(
        "/logon/long",
        body={"userName": username, "password": password, "auth": "secEnterprise"},
    )
    if "logonToken" in response:
        return response.get("logonToken")
    elif response.get("error_code", "") == "FWB 00008":
        raise ValueError(response.get("message"))


def invalidate(token: str) -> None:
    response = post("/logoff", token=token)

    if response.get("error_code", "") == "FWM 02024":
        raise ValueError(response.get("message"))
