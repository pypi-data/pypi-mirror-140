import asyncio
from datetime import datetime
from typing import List, Optional, Sequence, Set

from pydantic import BaseModel

from ..core import BaseClient, with_concurrency_limit
from ..encoders import encode_query_params
from ..types import AccountType, Currency

PATH = "/users/{user_uuid}/accounts/{account_uuid}/balances"


class BalanceRecord(BaseModel):
    account_type: Optional[AccountType]
    description: Optional[str]
    balance: int
    ts: int
    currency: Optional[Currency]
    labels: Set[str]


class BalancesMeta(BaseModel):
    page: int
    utc_starttime: Optional[datetime] = None
    utc_endtime: Optional[datetime] = None
    acct_uuid: str
    user_uuid: str
    total_balances_count: int
    max_pages: int
    client_uuid: str


class BalancesAccount(BaseModel):
    account_number: str
    account_type: Optional[AccountType]
    records: List[BalanceRecord]


class BalancesResponse(BaseModel):
    meta: BalancesMeta
    balances: List[BalancesAccount]

    class Config:
        fields = {"meta": "_meta"}


class BaseBalancesResource:
    def __init__(self, client: BaseClient):
        self._client = client

    async def _get_page(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
        page: int = 1,
    ) -> BalancesResponse:
        async with self._client.session() as session:
            response = await session.get(
                PATH.format(user_uuid=user_uuid, account_uuid=account_uuid),
                params=encode_query_params(
                    utc_starttime=utc_starttime,
                    utc_endtime=utc_endtime,
                    labels=labels,
                    page=page,
                ),
            )

        assert response.status_code == 200, response.text
        return BalancesResponse(**response.json())

    async def _get(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
    ) -> List[BalanceRecord]:
        response = await self._get_page(
            user_uuid=user_uuid,
            account_uuid=account_uuid,
            utc_starttime=utc_starttime,
            utc_endtime=utc_endtime,
            labels=labels,
        )
        max_pages = response.meta.max_pages
        if max_pages > 1:
            coroutines = [
                self._get_page(
                    user_uuid=user_uuid,
                    account_uuid=account_uuid,
                    utc_starttime=utc_starttime,
                    utc_endtime=utc_endtime,
                    labels=labels,
                    page=page + 2,
                )
                for page in range(max_pages - 1)
            ]
            response_pages = await asyncio.gather(
                *with_concurrency_limit(coroutines, self._client.concurrency_limit)
            )
            responses = (response, *response_pages)
        else:
            responses = (response,)

        return [
            record
            for response in responses
            for balance_account in response.balances
            for record in balance_account.records
        ]


class AsyncBalancesResource(BaseBalancesResource):
    async def get(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
    ) -> List[BalanceRecord]:
        return await self._get(
            user_uuid=user_uuid,
            account_uuid=account_uuid,
            utc_starttime=utc_starttime,
            utc_endtime=utc_endtime,
            labels=labels,
        )


class SyncBalancesResource(BaseBalancesResource):
    def get(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
    ) -> List[BalanceRecord]:
        return asyncio.run(
            self._get(
                user_uuid=user_uuid,
                account_uuid=account_uuid,
                utc_starttime=utc_starttime,
                utc_endtime=utc_endtime,
                labels=labels,
            )
        )
