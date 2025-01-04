from dataclasses import dataclass
from datetime import datetime


@dataclass
class AmountDetails:
    net: float
    vat: float
    gross: float


@dataclass
class HourlyTariff:
    total: AmountDetails
    tax: AmountDetails
    surcharge: AmountDetails
    commodity: AmountDetails
    periodFrom: datetime
    periodTo: datetime
