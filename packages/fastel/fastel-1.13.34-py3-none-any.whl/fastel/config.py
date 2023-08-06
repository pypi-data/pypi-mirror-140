import os
from typing import Any, Dict


class SdkConfigCls:
    sdk_client: str = ""
    stage: str = ""
    client_secret: str = ""
    extra_config: Dict[str, Any] = {}

    @property
    def provider(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[0]

    @property
    def client_id(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[1]

    @property
    def package(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[-1]

    @property
    def is_service(self) -> bool:
        return True if self.provider == "serivce" else False

    @property
    def auth_host(self) -> str:
        if self.stage == "stg" and self.package == "revtel":
            return "https://auth-stg.revtel-api.com/v4"
        elif self.stage == "prod" and self.package == "revtel":
            return "https://auth.revtel-api.com/v4"
        else:
            return ""

    @property
    def payment_host(self) -> str:
        if self.stage == "stg" and self.package == "revtel":
            return "https://payment-stg.revtel-api.com/v3"
        elif self.stage == "prod" and self.package == "revtel":
            return "https://payment.revtel-api.com/v3"
        else:
            return ""

    def put_extras(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            self.extra_config[key] = value

    def get_extra(self, key: str, default_value: Any = None) -> Any:
        return self.extra_config.get(key, default_value)


SdkConfig = SdkConfigCls()


def sdk_auto_config(sdk_client: str = "") -> None:
    global SdkConfig
    print("SdkConfig", SdkConfig)

    def get_env_or_raise(key: str, raise_exception: bool = True) -> str:
        value: str = os.environ.get(key, "")
        if value == "" and raise_exception:
            raise AttributeError(f"[sdk_auto_config] {key} not found")
        return value

    client_id = get_env_or_raise("CLIENT_ID")

    # if not sdk_client initial app by revtel
    if not sdk_client:
        sdk_client = f"app.{client_id}.revtel"

    # common env vars
    SdkConfig.stage = get_env_or_raise("STAGE")

    SdkConfig.sdk_client = sdk_client
    SdkConfig.client_secret = get_env_or_raise("CLIENT_SECRET")
