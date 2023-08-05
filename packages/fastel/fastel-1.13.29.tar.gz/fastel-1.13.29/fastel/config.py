from typing import Any, Dict


class SdkConfig:
    auth_host: str = ""
    payment_host: str = ""
    client_id: str = ""
    client_secret: str = ""
    extra_config: Dict[str, Any] = {}

    @classmethod
    def put_configs(cls, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if not hasattr(cls, key):
                print("SdkConfig: no such key", key, "/", value)
            else:
                setattr(cls, key, value)

    @classmethod
    def get_config(cls, key: str, default_value: Any = None) -> Any:
        return getattr(cls, key, default_value)

    @classmethod
    def put_extras(cls, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            cls.extra_config[key] = value

    @classmethod
    def get_extra(cls, key: str, default_value: Any = None) -> Any:
        return cls.extra_config.get(key, default_value)
