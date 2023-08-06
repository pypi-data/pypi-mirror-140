__author__ = "Hugo Inzirillo"

from datetime import datetime
from typing import Union, List

from flask import Response

from napbots.api.authentication.auth import ClientCredentials, Scope
from napbots.api.base.base import BaseClient
from napbots.api.data.model import SignalList, Signal, Strategy, UnderlyingList


class NapbotsApiClient(BaseClient):
    _base_url = "https://api.napbots.com"

    def __init__(self, credentials: ClientCredentials):
        super().__init__()
        self.credentials = credentials

    def create_strategy(
            self,
            strategy: Strategy
    ) -> Response:
        return self._post("/v1/strategy", data=strategy)

    def get_strategy(
            self,
            strategy_id
    ) -> Strategy:
        json = self._get("/v1/strategy/{strategyID}".format(strategyID=strategy_id))
        return Strategy.from_json(**json.get("data"))

    def get_all_strategy(
            self,
            client_id
    ) -> list:
        json = self._get("/v1/strategy/all/for-owner/{client_id}".format(client_id=client_id))
        return list(map(lambda x: Strategy.from_json(**x), json.get("data")))

    def send_signal(
            self,
            strategy_id: str,
            ts: datetime,
            underlyings: UnderlyingList
    ):
        signal = Signal(strategy_id, ts, underlyings)
        return self._post("/v1/reweight", data=signal)


    def get_signals(
            self,
            strategy_id: str,
            start_ts: datetime,
            end_ts: datetime
    ) -> SignalList:
        route = "/v1/reweight/for-strategy/{strategyID}/between/{startTs}/{endTs}".format(
            strategyID=strategy_id,
            startTs=start_ts.strftime("%Y-%m-%dT%H:%M:%S"),
            endTs=end_ts.strftime("%Y-%m-%dT%H:%M:%S")
        )
        json = self._get(route=route)
        return SignalList(map(lambda x: Signal.from_json(**x), json.get("data")))

    def get_last_signal_executed(self, strategy_id: str) -> Signal:
        route = "/v1/reweight/last/for-strategy/{strategyId}".format(
            strategyId=strategy_id
        )
        json = self._get(route=route)
        return Signal.from_json(**json.get("data"))

    def get_last_signal_pushed(self, strategy_id: str, ts: datetime) -> Signal:
        route = "/v1/reweight/last/for-strategy/{strategyId}/rebalancing-ts/{rebalancingTs}".format(
            strategyId=strategy_id, rebalancingTs=ts.strftime("%Y-%m-%dT%H:%M:%S")
        )
        json = self._get(route=route)
        return Signal.from_json(**json.get("data"))


def client(
        client_id: str,
        client_secret: str,
        scope: Union[List[str], List[Scope]]
) -> NapbotsApiClient:
    credentials = ClientCredentials(client_id, client_secret, scope)
    return NapbotsApiClient(credentials)
