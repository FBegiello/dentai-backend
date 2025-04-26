import os
from typing import Any, Callable, Generator, List, Protocol
from cryptography.fernet import Fernet
from pydantic import AnyHttpUrl, Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from openai import OpenAI

CallableGenerator = Generator[Callable[..., Any], None, None]


class Decryptor(Protocol):
    def decrypt(self, value: bytes) -> bytes:
        ...  # fmt: skip


class FakeFernet:
    def decrypt(self, value: bytes) -> bytes:
        return value


class EncryptedField(str):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update(type="str", writeOnly=True)

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield cls.validate

    @classmethod
    def validate(cls, value: str, validation_info: ValidationInfo) -> "EncryptedField":
        if isinstance(value, cls):
            return value
        return cls(value)

    def __init__(self, value: str):
        print(value)
        print(value.splitlines())
        print("".join(value.splitlines()))
        print("".join(value.splitlines()).strip())
        self._secret_value = "".join(value.splitlines()).strip().encode("utf-8")
        print(self._secret_value)
        self.decrypted = False

    def get_decrypted_value(self, decryptor: Decryptor) -> str:
        if not self.decrypted:
            value = decryptor.decrypt(self._secret_value)
            self._secret_value = value
            self.decrypted = True
        return self._secret_value.decode("utf-8")


class FernetDecryptorField(str):
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update(type="str", writeOnly=True)

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield cls.validate

    @classmethod
    def validate(cls, value: str, validation_info: ValidationInfo) -> Decryptor:
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
    BACKEND_CORS_ALLOW_ALL: bool = True

    DATABASE_URI: PostgresDsn

    LOGGING_CONF_FILE: str = "logging.conf"

    OPENAI_API_KEY: str

    OPENAI_CLIENT: OpenAI = OpenAI()

    # Models
    LLM_MODEL: str = "gpt-4.1"
    LLM_MODEL_COMPLEX: str = "o3-mini"
    LLM_MODEL_TTS: str = "gpt-4o-mini-tts"
    LLM_MODEL_WORKERS: str | dict = "gpt-4o-mini"

    LLM_MODEL_TTS_VOICE: str = "coral"

    # Data
    DATA_PATH: str = "./data/dent-hist.md"
    TEMP_AUDIO_PATH: str = "./data/audio.mp3"

    @field_validator("*", mode="after")
    def _decryptor(cls, v, validation_info: ValidationInfo, *args, **kwargs):
        if isinstance(v, EncryptedField):
            print(f"-> Decrypting {validation_info.field_name}")
            v = v.get_decrypted_value(validation_info.data["FERNET_DECRYPTOR"])
            print(v)
            return v
        return v

    @field_validator("*", mode="after")
    def assemble_model_type(cls, v, validation_info: ValidationInfo):
        if isinstance(v, dict) and validation_info.field_name.startswith("LLM_MODEL"):
            if validation_info.data["DEBUG"]:
                return v["DEBUG"]
            else:
                return v["PROD"]
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="after")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=os.environ.get("ENV", ".env"),
        extra="allow",
    )


settings = Settings()
