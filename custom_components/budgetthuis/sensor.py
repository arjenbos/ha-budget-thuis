"""Sensor for Budget Thuis packages."""
import logging
from dataclasses import dataclass
from datetime import timedelta
from homeassistant.components.sensor import SensorEntityDescription, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import event
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import utcnow
from typing import Any, Callable

from . import DOMAIN
from .coordinator import BudgetThuisCoordinator
from .structs.contract import Contract
from .structs.hourly_tariff import HourlyTariff

_LOGGER = logging.getLogger(__name__)


@dataclass
class BudgetThuisEntityDescription(SensorEntityDescription):
    """Describes Budget Thuis sensor entity."""

    service_name: str | None = None
    value_fn: Callable[[dict], StateType] = None
    attr_fn: Callable[[dict], dict[str, StateType | list]] = lambda _: {}


SENSOR_TYPES: tuple[BudgetThuisEntityDescription, ...] = (
    BudgetThuisEntityDescription(
        key="electricity_total",
        name="Current electricity total price",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data['current_tariff'].total.gross,
        attr_fn=lambda data: {
            "net": data['current_tariff'].total.net,
            "vat": data['current_tariff'].total.vat,
            "gross": data['current_tariff'].total.gross
        },
    ),
    BudgetThuisEntityDescription(
        key="electricity_tax",
        name="Current electricity tax price",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data['current_tariff'].tax.gross,
        attr_fn=lambda data: {
            "net": data['current_tariff'].tax.net,
            "vat": data['current_tariff'].tax.vat,
            "gross": data['current_tariff'].tax.gross
        },
    ),
    BudgetThuisEntityDescription(
        key="electricity_surcharge",
        name="Current electricity surcharge price",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data['current_tariff'].surcharge.gross,
        attr_fn=lambda data: {
            "net": data['current_tariff'].surcharge.net,
            "vat": data['current_tariff'].surcharge.vat,
            "gross": data['current_tariff'].surcharge.gross
        },
    ),
    BudgetThuisEntityDescription(
        key="electricity_commodity",
        name="Current electricity commodity price",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data['current_tariff'].commodity.gross,
        attr_fn=lambda data: {
            "net": data['current_tariff'].commodity.net,
            "vat": data['current_tariff'].commodity.vat,
            "gross": data['current_tariff'].commodity.gross
        },
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Budget Thuis sensor platform."""

    coordinator = BudgetThuisCoordinator(hass)

    await coordinator.async_config_entry_first_refresh()

    entities = []

    # Loop through contracts and create sensors for each contract
    for contract in coordinator.data:
        for description in SENSOR_TYPES:
            entities.append(
                BudgetThuisSensor(coordinator, description, entry, contract)
            )

    async_add_entities(entities, True)


class BudgetThuisSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Budget Thuis sensor."""

    _attr_attribution = "Data provided by Budget Thuis"
    _attr_icon = "mdi:currency-eur"

    def __init__(
            self,
            coordinator: BudgetThuisCoordinator,
            description: BudgetThuisEntityDescription,
            entry: ConfigEntry,
            contract: dict[str, Contract | list[HourlyTariff]],
    ) -> None:
        """Initialize the sensor."""
        self.entity_description: BudgetThuisEntityDescription = description
        self.contract = contract
        self._attr_unique_id = f"{entry.unique_id}.{contract['contract'].id}.{description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}", f"{contract['contract'].id}")},
            name=f"{contract['contract'].id} - {contract['contract'].supplyAddress.street} {contract['contract'].supplyAddress.houseNumber} {contract['contract'].supplyAddress.houseNumberExtension if contract['contract'].supplyAddress.houseNumberExtension else ''}",
            manufacturer="Budget Thuis",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.budgetthuis.nl",
        )

        self._update_job = HassJob(self._handle_scheduled_update)
        self._unsub_update = None

        super().__init__(coordinator)

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        try:
            # Pass contract-specific data to the value function
            self._attr_native_value = self.entity_description.value_fn(self.contract)
        except (TypeError, IndexError, ValueError):
            # No data available
            self._attr_native_value = None

        # Cancel the currently scheduled event if there is any
        if self._unsub_update:
            self._unsub_update()
            self._unsub_update = None

        # Schedule the next update at exactly the next whole hour sharp
        self._unsub_update = event.async_track_point_in_utc_time(
            self.hass,
            self._update_job,
            utcnow().replace(minute=0, second=0) + timedelta(hours=1),
        )

    async def _handle_scheduled_update(self, _):
        """Handle a scheduled update."""
        # Only handle the scheduled update for entities which have a reference to hass,
        # which disabled sensors don't have.
        if self.hass is None:
            return

        self.async_schedule_update_ha_state(True)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        # Pass contract-specific data to the attribute function
        return self.entity_description.attr_fn(self.contract)
