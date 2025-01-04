import logging
import requests
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)
from homeassistant.util import utcnow

from . import AsyncConfigEntryAuth
from .budget_thuis import BudgetThuis
from .const import DOMAIN
from .nutsservices import Nutsservices
from .structs.contract import Contract
from .structs.hourly_tariff import HourlyTariff

_LOGGER = logging.getLogger(__name__)


class BudgetThuisCoordinator(DataUpdateCoordinator):
    budget_thuis_api: BudgetThuis
    nutsservices_api: Nutsservices

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize Budget Thuis coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Budget Thuis",
            update_interval=timedelta(seconds=90),
        )

    async def _async_update_data(self):
        _LOGGER.debug('Get latest data.')
        try:
            auth: AsyncConfigEntryAuth = self.hass.data[DOMAIN][self.config_entry.entry_id]['auth']
            await auth.check_and_refresh_token()

            self.budget_thuis_api = BudgetThuis(auth.access_token)
            self.nutsservices_api = Nutsservices(auth.access_token)

            data: list[dict[str, Contract | list[HourlyTariff]]] = []

            contracts = await self.hass.async_add_executor_job(self.nutsservices_api.all_contracts)
            _LOGGER.debug("Found %d contracts", len(contracts))
            for contract in contracts:
                if contract.contractType != "Dynamic":
                    _LOGGER.debug("Skipping contract %d, not a dynamic contract.", contract.id)
                    continue

                tariffs = await self.hass.async_add_executor_job(self.nutsservices_api.hourly_tariff, contract.id)
                _LOGGER.debug("Found %d tariff entries", len(tariffs))

                current_tariff = None

                for tariff in tariffs:
                    if tariff.periodFrom <= utcnow() <= tariff.periodTo:
                        current_tariff = tariff
                        break

                data.append({
                    'contract': contract,
                    'current_tariff': current_tariff
                })

            return data
        except requests.exceptions.RequestException as exception:
            raise UpdateFailed("Unable to update Budget Thuis data") from exception
