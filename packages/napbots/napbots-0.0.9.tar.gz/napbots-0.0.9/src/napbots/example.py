__author__ = "Hugo Inzirillo"

import sys


from datetime import datetime, timezone


from napbots.api.authentication import Scope
from napbots.api.client.client import client
from napbots.api.data.model import (
    EligibleComponentList,
    EligibleComponent,
    Strategy,
    UnderlyingList,
    ProductCode,
    Underlying,
    ExposureType,
)


if __name__ == "__main__":
    client = client(
        client_id="hougo", client_secret="", scope=[Scope.READ, Scope.WRITE]
    )
    now = datetime.now(tz=timezone.utc)
    component_list = EligibleComponentList()
    component_list.append(
        EligibleComponent(
            product_code=ProductCode.ETH_USD, exposure_type=ExposureType.LO
        )
    )
    strategy = Strategy("ALPHA", component_list, cron="0 0 1 0/1 * *")
    client.get_strategy("STRAT_NAPBOTS_HOUGO_ALPHA")
    client.create_strategy(strategy)
