import asyncio
from typing import List

from pydantic import BaseModel

from ..core import BaseClient
from ..types import AccountType, Currency

PATH = "/users/{user_uuid}/accounts"


class Institution(BaseModel):
    name: str
    display_name: str


class Account(BaseModel):
    acct_uuid: str
    institution: Institution
    currency: Currency
    types: List[AccountType]


class AccountsMeta(BaseModel):
    user_uuid: str
    client_uuid: str


class AccountsResponse(BaseModel):
    meta: AccountsMeta
    accounts: List[Account]

    class Config:
        fields = {"meta": "_meta"}


class BaseAccountsResource:
    def __init__(self, client: BaseClient):
        self._client = client

    async def _get(self, user_uuid: str) -> List[Account]:
        async with self._client.session() as session:
            response = await session.get(PATH.format(user_uuid=user_uuid))

        assert response.status_code == 200, response.text
        return AccountsResponse(**response.json()).accounts


class AsyncAccountsResource(BaseAccountsResource):
    async def get(self, user_uuid: str) -> List[Account]:
        return await self._get(user_uuid)


class SyncAccountsResource(BaseAccountsResource):
    def get(self, user_uuid: str) -> List[Account]:
        return asyncio.run(self._get(user_uuid))
