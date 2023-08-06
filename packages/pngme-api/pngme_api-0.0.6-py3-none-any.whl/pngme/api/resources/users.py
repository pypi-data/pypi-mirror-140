import asyncio
from abc import ABC
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ..core import BaseClient, with_concurrency_limit
from ..encoders import encode_query_params

PATH = "/users"


class User(BaseModel):
    uuid: str
    first_name: str
    last_name: str
    email: str
    primary_phone_number: str
    primary_phone_imei: Optional[str]
    secondary_phone_number: Optional[str]
    secondary_phone_imei: Optional[str]
    is_kyc_verified: bool
    device_id: str
    external_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class UsersMeta(BaseModel):
    client_uuid: str
    created_before: datetime
    created_after: datetime
    search: str
    total_users_count: int
    page: int
    max_pages: int


class UsersResponse(BaseModel):
    meta: UsersMeta
    users: List[User]

    class Config:
        fields = {"meta": "_meta"}


class BaseUsersResource(ABC):
    def __init__(self, client: BaseClient):
        self._client = client

    async def _get_page(self, search: Optional[str], page: int = 1) -> UsersResponse:
        async with self._client.session() as session:
            response = await session.get(
                PATH,
                params=encode_query_params(
                    search=search,
                    page=page,
                ),
            )

        assert response.status_code == 200, response.text
        return UsersResponse(**response.json())

    async def _get(self, search: Optional[str] = None) -> List[User]:
        response = await self._get_page(search)
        max_pages = response.meta.max_pages
        if max_pages > 1:
            coroutines = [
                self._get_page(search, page + 2) for page in range(max_pages - 1)
            ]
            response_pages = await asyncio.gather(
                *with_concurrency_limit(coroutines, self._client.concurrency_limit),
            )
            responses = (response, *response_pages)
        else:
            responses = (response,)

        return [user for response in responses for user in response.users]


class AsyncUsersResource(BaseUsersResource):
    async def get(self, search: Optional[str] = None) -> List[User]:
        return await self._get(search)


class SyncUsersResource(BaseUsersResource):
    def get(self, search: Optional[str] = None) -> List[User]:
        return asyncio.run(self._get(search))
