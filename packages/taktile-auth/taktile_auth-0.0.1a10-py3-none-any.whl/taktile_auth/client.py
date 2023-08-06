import typing as t

import jwt
import requests
from jwt import PyJWKClient
from pydantic import UUID4, AnyHttpUrl, ValidationError

from taktile_auth.exceptions import InvalidAuthException
from taktile_auth.schemas.token import TaktileIdToken
from taktile_auth.settings import settings

ALGORITHM = "RS256"
AUTH_SERVER_URL = {
    "local": "http://taktile-api.local.taktile.com:8000",
    "dev": "https://taktile-api.dev.taktile.com",
    "stg": "https://taktile-api.stg.taktile.com",
    "prod": "https://taktile-api.prod.taktile.com",
    "expo": "https://taktile-api.expo.taktile.com",
}


class AuthClient:
    def __init__(
        self,
        url: AnyHttpUrl = AUTH_SERVER_URL[settings.ENV],
    ) -> None:
        self.public_key_url = f"{url}/.well-known/jwks.json"
        self.access_token_url = f"{url}/api/v1/login/access-token"
        self.client = PyJWKClient(self.public_key_url)

    def decode_id_token(self, token: str) -> TaktileIdToken:
        try:
            key = self.client.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token,
                key,
                algorithms=[ALGORITHM],
                audience=settings.ENV,
            )
            token_data = TaktileIdToken(**payload)
        except jwt.ExpiredSignatureError:
            raise InvalidAuthException("signature-expired")
        except (jwt.PyJWTError, ValidationError):
            raise InvalidAuthException("could-not-validate")

        return token_data

    def get_access(
        self,
        api_key: t.Optional[UUID4],
        id_token: t.Optional[str],
    ) -> TaktileIdToken:
        if not api_key and not id_token:
            raise InvalidAuthException("no-auth-proved")
        if not id_token:
            res = requests.post(
                self.access_token_url, headers={"X-Api-Key": api_key}
            )
            res.raise_for_status()
            parsed_id_token = res.json()["id_token"]
        else:
            parsed_id_token = id_token.replace("Bearer ", "", 1)
        return self.decode_id_token(parsed_id_token)
