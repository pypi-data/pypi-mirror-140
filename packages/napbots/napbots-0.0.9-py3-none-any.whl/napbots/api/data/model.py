__author__ = "Hugo Inzirillo"

from datetime import datetime
from enum import Enum
from napbots.api.data.serializable import Serializable


def raise_error(_class):
    raise TypeError(f"components must be an instance of {_class}")


class ProductCode(Enum):
    BTC_USD = "BTC-USD"
    ETH_USD = "ETH-USD"
    ADA_USD = "ADA-USD"
    BNB_USD = "BNB-USD"
    MATIC_USD = "MATIC-USD"
    EOS_USD = "EOS-USD"
    XRP_USD = "XRP-USD"
    LTC_USD = "LTC-USD"
    XLM_USD = "XLM-USD"
    ZEC_USD = "ZEC-USD"
    BCH_USD = "BCH-USD"
    LINK_USD = "LINK-USD"
    SOL_USD = "SOL-USD"
    XTZ_USD = "XTZ-USD"
    DOT_USD = "DOT-USD"
    UNI_USD = "UNI-USD"


class ComponentList(list):
    pass


class UnderlyingList(list):
    pass


class SignalList(list):
    pass


class EligibleComponentList(list):
    pass


class ExposureType(Enum):
    LO = "LONG_ONLY"
    AR = "ABSOLUTE_RETURN"


class Data:
    """
    this class implement the global representation for data
    """

    def __repr__(self):
        kwargs = [f"{key}={value!r}" for key, value in self.__dict__.items() if key[0] != "_" or key[:2] != "__"]
        return "{}({})".format(type(self).__name__, "".join(kwargs))

    @classmethod
    def from_json(cls, **kwargs):
        raise NotImplemented

    @property
    def json(self):
        raise NotImplementedError


class Strategy(Data, Serializable):

    def __init__(
            self,
            label: str,
            components: EligibleComponentList,
            cron: str,
            strategy_id: str = None,
    ):
        if not isinstance(components, EligibleComponentList):
            raise_error(EligibleComponentList)
        self.strategy_id = strategy_id
        self.components = components
        self.label = label
        self.cron = cron

    @classmethod
    def from_json(cls, **kwargs):
        eligible_components = kwargs.get("eligibleComponents")
        eligible_component_list = EligibleComponentList(
            map(lambda x: EligibleComponent.from_json(**x), eligible_components))
        strategy_id = kwargs.get("strategyID")
        label = kwargs.get("label")
        cron = kwargs.get("reweigthCron")
        return cls(label, eligible_component_list, cron, strategy_id)

    @property
    def json(self):
        return dict(
            strategyID=self.strategy_id,
            eligibleComponents=[component.json for component in self.components],
            label=self.label,
            rebalancingCron=self.cron
        )


class Signal(Data, Serializable):

    def __init__(
            self,
            strategy_id: str,
            ts: datetime,
            underlyings: UnderlyingList

    ):
        if not isinstance(underlyings, UnderlyingList):
            raise_error(ComponentList)
        self.underlyings = underlyings
        self.strategy_id = strategy_id
        self.ts = ts

    @classmethod
    def from_json(cls, **kwargs):
        components = kwargs.get("componentsList")
        underlying_list = UnderlyingList(map(lambda x: Underlying.from_json(**x), components))
        strategy_id = kwargs.get("strategyID")
        ts = kwargs.get("ts")
        return cls(strategy_id, datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S"), underlying_list)

    @property
    def json(self):
        return dict(
            underlyingList=[underlying.json for underlying in self.underlyings],
            strategyID=self.strategy_id,
            rebalancingTs=self.format(self.ts)

        )


class Underlying(Data):
    def __init__(
            self,
            product_code: str,
            weight: float
    ):
        self.product_code = product_code
        self.weight = weight

    @classmethod
    def from_json(cls, **kwargs):
        product_code = kwargs.get("productCode")
        weight = kwargs.get("weight")
        return cls(product_code, weight)

    @property
    def json(self):
        return dict(
            productCode=self.product_code,
            weight=self.weight
        )


class EligibleComponent(Data, Serializable):
    __dict__ = {}

    def __init__(
            self,
            product_code: ProductCode,
            exposure_type: ExposureType
    ):
        if not isinstance(product_code, ProductCode):
            raise_error(ProductCode)

        if not isinstance(exposure_type, ExposureType):
            raise_error(ExposureType)

        self.product_code = product_code.value
        self.exposure_type = exposure_type.value

    @classmethod
    def from_json(cls, **kwargs):
        exposure_type = kwargs.get("exposureType")
        product_code = kwargs.get("productCode")
        if exposure_type is not None:
            exposure_type = ExposureType(exposure_type)
        if product_code is not None:
            product_code = ProductCode(product_code)
        return cls(product_code, exposure_type)

    @property
    def json(self):
        return dict(
            productCode=self.product_code,
            exposureType=self.exposure_type
        )
