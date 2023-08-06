from typing import TypedDict


class BackendConfigType(TypedDict):
    alias: str
    backend: str
    host: str
    global_path: str
    simg_path: str
    runtimes: list[str]