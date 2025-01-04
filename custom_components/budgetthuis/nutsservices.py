import logging
import requests
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .structs.contract import Contract, Address
from .structs.hourly_tariff import HourlyTariff, AmountDetails

_LOGGER = logging.getLogger(__name__)


class Nutsservices:
    baseUrlAccounts: str = "https://app.api.nutsservices.nl"

    def __init__(self, access_token: str):
        self.client = requests.Session()
        self.client.mount(
            prefix='https://',
            adapter=HTTPAdapter(
                max_retries=Retry(
                    total=5,
                    backoff_factor=3
                ),
                pool_maxsize=25,
                pool_block=True
            )
        )
        self.client.headers = {
            "Authorization": "Bearer " + access_token
        }

    def all_contracts(self) -> list[Contract]:
        response = self.client.post(
            url=self.baseUrlAccounts + "/energy/v1/customer/productPicker",
            json={
                "relationIds": []
            }
        )
        response.raise_for_status()

        contracts: list[Contract] = []

        for contract in response.json()['contractsInfo']:
            contracts.append(
                Contract(
                    id=contract['contractId'],
                    relationId=contract['relationId'],
                    propositionType=contract['propositionType'],
                    contractStatus=contract['contractStatus'],
                    contractType=contract['contractType'],
                    supplyAddress=Address(
                        zipCode=contract['supplyAddress']['zipCode'],
                        houseNumber=contract['supplyAddress']['houseNumber'],
                        houseNumberExtension=contract['supplyAddress']['houseNumberExtension'] if contract[
                                                                                                      'supplyAddress'] != "" else None,
                        city=contract['supplyAddress']['city'],
                        street=contract['supplyAddress']['street'],
                    )
                )
            )

        return contracts

    def hourly_tariff(self, contract_id: int) -> list[HourlyTariff]:
        response = self.client.get(
            self.baseUrlAccounts + "/energy/v1/contract/" + str(contract_id) + "/dashboard/hourlytariff")
        response.raise_for_status()

        tariffs: list[HourlyTariff] = []

        for tariff in response.json()['electricityTariffs']:
            tariffs.append(
                HourlyTariff(
                    total=AmountDetails(
                        net=tariff['totalTariff']['amountNet'],
                        vat=tariff['totalTariff']['amountVat'],
                        gross=tariff['totalTariff']['amountGross']
                    ),
                    tax=AmountDetails(
                        net=tariff['energyTax']['amountNet'],
                        vat=tariff['energyTax']['amountVat'],
                        gross=tariff['energyTax']['amountGross']
                    ),
                    surcharge=AmountDetails(
                        net=tariff['surcharge']['amountNet'],
                        vat=tariff['surcharge']['amountVat'],
                        gross=tariff['surcharge']['amountGross']
                    ),
                    commodity=AmountDetails(
                        net=tariff['commodity']['amountNet'],
                        vat=tariff['commodity']['amountVat'],
                        gross=tariff['commodity']['amountGross']
                    ),
                    periodFrom=datetime.fromisoformat(tariff['periodFrom']),
                    periodTo=datetime.fromisoformat(tariff['periodTo'])
                )
            )

        return tariffs
