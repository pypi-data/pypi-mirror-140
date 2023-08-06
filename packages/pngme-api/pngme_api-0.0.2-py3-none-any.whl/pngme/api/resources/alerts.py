import asyncio
from datetime import datetime
from typing import List, Optional, Sequence, Set

from pydantic import BaseModel

from ..core import BaseClient, limit_concurrency
from ..encoders import encode_query_params

PATH = "/users/{user_uuid}/accounts/{account_uuid}/alerts"


class Alert(BaseModel):
    smslog_id: str
    ts: int
    smslog_body: str
    labels: Set[str]


class AlertsMeta(BaseModel):
    page: int
    utc_starttime: Optional[datetime] = None
    utc_endtime: Optional[datetime] = None
    acct_uuid: str
    user_uuid: str
    total_alerts_count: int
    max_pages: int
    client_uuid: str


class AlertsResponse(BaseModel):
    meta: AlertsMeta
    alerts: List[Alert]

    class Config:
        fields = {"meta": "_meta"}


class BaseAlertsResource:
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
    ) -> AlertsResponse:
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
        return AlertsResponse(**response.json())

    async def _get(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
    ) -> List[Alert]:
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
                *limit_concurrency(coroutines, self._client.concurrency_limit)
            )
            responses = (response, *response_pages)
        else:
            responses = (response,)

        return [alert for response in responses for alert in response.alerts]


class AsyncAlertsResource(BaseAlertsResource):
    async def get(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
    ) -> List[Alert]:
        return await self._get(
            user_uuid=user_uuid,
            account_uuid=account_uuid,
            utc_starttime=utc_starttime,
            utc_endtime=utc_endtime,
            labels=labels,
        )


class SyncAlertsResource(BaseAlertsResource):
    def get(
        self,
        user_uuid: str,
        account_uuid: str,
        utc_starttime: Optional[datetime] = None,
        utc_endtime: Optional[datetime] = None,
        labels: Optional[Sequence[str]] = None,
    ) -> List[Alert]:
        return asyncio.run(
            self._get(
                user_uuid=user_uuid,
                account_uuid=account_uuid,
                utc_starttime=utc_starttime,
                utc_endtime=utc_endtime,
                labels=labels,
            )
        )
