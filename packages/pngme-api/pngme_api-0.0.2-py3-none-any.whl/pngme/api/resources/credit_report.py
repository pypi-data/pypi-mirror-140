import asyncio
from typing import Any, Dict, Optional

from ..core import BaseClient

POST_PATH = "/users/{user_uuid}/creditreport"
GET_PATH = "/users/{user_uuid}/creditreport/{report_id}"


CreditReport = Dict[str, Any]


class BaseCreditReportResource:
    def __init__(self, client: BaseClient):
        self._client = client

    async def _create(self, user_uuid: str) -> str:
        async with self._client.session() as session:
            response = await session.post(POST_PATH.format(user_uuid=user_uuid))

        assert response.status_code == 201
        report_id = str(response.json()["credit_report_id"])
        return report_id

    async def _get_by_id(
        self, user_uuid: str, report_id: str
    ) -> Optional[CreditReport]:
        while True:
            async with self._client.session() as session:
                response = await session.get(
                    GET_PATH.format(user_uuid=user_uuid, report_id=report_id)
                )

            assert response.status_code == 200
            body: Dict[str, Any] = response.json()
            report_status = body["credit_report_status"]

            if report_status == "PENDING":
                await asyncio.sleep(5)
            elif report_status == "SUCCEEDED":
                report: CreditReport = body["credit_report"]
                return report
            else:
                return None

    async def _get(self, user_uuid: str) -> Optional[CreditReport]:
        report_id = await self._create(user_uuid)
        report = await self._get_by_id(user_uuid, report_id)
        return report


class AsyncCreditReportResource(BaseCreditReportResource):
    async def get(self, user_uuid: str) -> Optional[CreditReport]:
        return await self._get(user_uuid)


class SyncCreditReportResource(BaseCreditReportResource):
    def get(self, user_uuid: str) -> Optional[CreditReport]:
        return asyncio.run(self._get(user_uuid))
