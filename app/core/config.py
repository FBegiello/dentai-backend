import os
from typing import Any, Callable, Generator, List, Protocol, Union

from cryptography.fernet import Fernet
from pydantic.v1 import AnyHttpUrl, BaseSettings, Field, PostgresDsn, validator

CallableGenerator = Generator[Callable[..., Any], None, None]


class Decryptor(Protocol):
    def decrypt(self, value: bytes) -> bytes:
        ...  # fmt: skip


class FakeFernet:
    def decrypt(self, value: bytes) -> bytes:
        return value


class EncryptedField(str):
    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update(type="str", writeOnly=True)

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> "EncryptedField":
        if isinstance(value, cls):
            return value
        return cls(value)

    def __init__(self, value: str):
        self._secret_value = value.encode("utf-8")
        self.decrypted = False

    def get_decrypted_value(self, decryptor: Decryptor) -> str:
        if not self.decrypted:
            value = decryptor.decrypt(self._secret_value)
            self._secret_value = value
            self.decrypted = True
        return self._secret_value.decode("utf-8")


class FernetDecryptorField(str):
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        print(field_schema)
        field_schema.update(type="str", writeOnly=True)

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> Decryptor:
        master_key = os.environ.get(value)
        if not master_key:
            return FakeFernet()
        return Fernet(os.environ[value])


class Settings(BaseSettings):

    # name of env variable that hold master key
    FERNET_DECRYPTOR: FernetDecryptorField = Field("MASTER_KEY")  # type: ignore

    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: AnyHttpUrl
    VERSION: str = "0.0.1"

    DEBUG: bool = False

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    BACKEND_CORS_ALLOW_ALL: bool = False

    OPENAI_API_KEY: str

    @validator("*")
    def _decryptor(cls, v, values):
        if isinstance(v, EncryptedField):
            return v.get_decrypted_value(values["FERNET_DECRYPTOR"])
        return v

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DATABASE_URI: PostgresDsn

    LOGGING_CONF_FILE: str = "logging.conf"

    class Config:
        case_sensitive = True
        env_file = os.environ.get("ENV", ".env")


settings = Settings()
