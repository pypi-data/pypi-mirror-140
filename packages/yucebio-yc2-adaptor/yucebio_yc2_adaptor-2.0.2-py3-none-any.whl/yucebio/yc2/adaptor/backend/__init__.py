from .base import BaseAdaptor, PLACEHOLDER_GLOBAL_PATH, PLACEHOLDER_SIMG_PATH
from .sge import Adaptor as SgeAdaptor
from .bcs import Adaptor as BcsAdaptor
from .aws import Adaptor as AwsAdaptor
from .types import BackendConfigType

SUPPORTTED_BACKENDS = {
    SgeAdaptor.PLATFORM.lower(): SgeAdaptor,
    BcsAdaptor.PLATFORM.lower(): BcsAdaptor,
    AwsAdaptor.PLATFORM.lower(): AwsAdaptor
}

def create_adaptor(backend_config: BackendConfigType = None) -> BaseAdaptor:
    baseAdaptor = BaseAdaptor()

    if not backend_config:
        return baseAdaptor

    # 支持配置别名
    backend = backend_config.get('backend', backend_config.get('platform'))
    if backend not in SUPPORTTED_BACKENDS:
        raise RuntimeError(f"无效云平台类型，仅支持{list(SUPPORTTED_BACKENDS)}")
    cls: type[BaseAdaptor] = SUPPORTTED_BACKENDS[backend]
    return cls(backend_config)