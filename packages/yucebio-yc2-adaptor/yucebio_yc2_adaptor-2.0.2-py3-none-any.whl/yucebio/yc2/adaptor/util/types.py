from typing import Any, TypedDict


class CromwellBackendType(TypedDict):
    name: str
    owner: str
    alias: str
    host: str
    backend: str
    global_path: str
    simg_path: str

class RestfulResponseType(TypedDict):
    code: int
    message: str
    data: Any
    total: int


class WorkflowType(TypedDict):
    _id: str
    prefix: str
    cromwell_id: str
    workflow_name: str
    backend: CromwellBackendType

    status: str
    submission: str
    start: str
    end: str

    owner: str
    sample_ids: str
    running_tasks: list[str]

    calls: dict

class UserType(TypedDict):
    name: str      # 用户名
    exp: int       # 过期时间. utc时区的时间戳

class CromwellMetadataType(TypedDict):
    id: str
    workflowName: str
    submittedFiles: dict
    inputs: dict
    outputs: dict
    calls: dict
    status: str
    start: str
    end: str

