import ray

from sinagot.config import get_settings
from sinagot.logger import get_logger

RAY_PREFIX = "RAY_"


def init_ray() -> None:

    if not ray.is_initialized():
        settings = get_settings()
        prefix_len = len(RAY_PREFIX)
        kwargs = {
            key.lower()[prefix_len:]: value
            for key, value in settings.dict().items()
            if key.upper().startswith(RAY_PREFIX) and (value is not None)
        }

        init_message = ray.init(ignore_reinit_error=True, **kwargs)
        logger = get_logger()
        logger.debug("ray init %s", init_message)
