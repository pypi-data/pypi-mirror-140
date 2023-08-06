from .core import BaseClient
from .resources.accounts import AsyncAccountsResource, SyncAccountsResource
from .resources.alerts import AsyncAlertsResource, SyncAlertsResource
from .resources.balances import AsyncBalancesResource, SyncBalancesResource
from .resources.credit_report import AsyncCreditReportResource, SyncCreditReportResource
from .resources.transactions import AsyncTransactionsResource, SyncTransactionsResource
from .resources.users import AsyncUsersResource, SyncUsersResource


class AsyncClient(BaseClient):
    @property
    def accounts(self) -> AsyncAccountsResource:
        return AsyncAccountsResource(self)

    @property
    def alerts(self) -> AsyncAlertsResource:
        return AsyncAlertsResource(self)

    @property
    def balances(self) -> AsyncBalancesResource:
        return AsyncBalancesResource(self)

    @property
    def credit_report(self) -> AsyncCreditReportResource:
        return AsyncCreditReportResource(self)

    @property
    def transactions(self) -> AsyncTransactionsResource:
        return AsyncTransactionsResource(self)

    @property
    def users(self) -> AsyncUsersResource:
        return AsyncUsersResource(self)


class Client(BaseClient):
    @property
    def accounts(self) -> SyncAccountsResource:
        return SyncAccountsResource(self)

    @property
    def alerts(self) -> SyncAlertsResource:
        return SyncAlertsResource(self)

    @property
    def balances(self) -> SyncBalancesResource:
        return SyncBalancesResource(self)

    @property
    def credit_report(self) -> SyncCreditReportResource:
        return SyncCreditReportResource(self)

    @property
    def transactions(self) -> SyncTransactionsResource:
        return SyncTransactionsResource(self)

    @property
    def users(self) -> SyncUsersResource:
        return SyncUsersResource(self)
