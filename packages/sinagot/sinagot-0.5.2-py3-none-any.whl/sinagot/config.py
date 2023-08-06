from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_prefix = "SINAGOT_"

    LOGGING_LEVEL: str = "WARNING"
    RAY_LOCAL_MODE: bool = False
    RAY_LOGGING_LEVEL: str = "WARNING"
    RAY_ADDRESS: Optional[str]
    RAY_NUM_CPUS: Optional[int]
    RAY_NUM_GPUS: Optional[int]


def get_settings() -> Settings:
    return Settings()
