"""Description for ConsumerProducts Entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass, NumberMode
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import UnitOfVolume

from .descriptions_definitions import (
    HCBinarySensorEntityDescription,
    HCNumberEntityDescription,
    HCSelectEntityDescription,
    HCSensorEntityDescription,
    HCSwitchEntityDescription,
)

if TYPE_CHECKING:
    from .descriptions_definitions import _EntityDescriptionsDefinitionsType

CONSUMER_PRODUCTS_ENTITY_DESCRIPTIONS: _EntityDescriptionsDefinitionsType = {
    "binary_sensor": [
        HCBinarySensorEntityDescription(
            key="binary_sensor_bean_container_empty",
            entity="ConsumerProducts.CoffeeMaker.Event.BeanContainerEmpty",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value_on={"Present"},
            value_off={"Off", "Confirmed"},
        ),
    ],
    "event_sensor": [
        HCSensorEntityDescription(
            key="sensor_water_tank",
            entities=[
                "ConsumerProducts.CoffeeMaker.Event.WaterTankEmpty",
                "ConsumerProducts.CoffeeMaker.Event.WaterTankNearlyEmpty",
                "ConsumerProducts.CoffeeMaker.Event.WaterTankNotInserted",
            ],
            device_class=SensorDeviceClass.ENUM,
            options=["empty", "nearly_empty", "not_inserted", "full"],
        ),
        HCSensorEntityDescription(
            key="sensor_drip_tray",
            entities=[
                "ConsumerProducts.CoffeeMaker.Event.DripTrayFull",
                "ConsumerProducts.CoffeeMaker.Event.DripTrayNotInserted",
            ],
            device_class=SensorDeviceClass.ENUM,
            options=["full", "not_inserted", "ok"],
        ),
    ],
    "select": [
        HCSelectEntityDescription(
            key="select_coffee_temperature",
            entity="ConsumerProducts.CoffeeMaker.Option.CoffeeTemperature",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_bean_amount",
            entity="ConsumerProducts.CoffeeMaker.Option.BeanAmount",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_beverage_size",
            entity="ConsumerProducts.CoffeeMaker.Option.BeverageSize",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_coffee_milk_ratio",
            entity="ConsumerProducts.CoffeeMaker.Option.CoffeeMilkRatio",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_hot_water_temperature",
            entity="ConsumerProducts.CoffeeMaker.Option.HotWaterTemperature",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_flow_rate",
            entity="ConsumerProducts.CoffeeMaker.Option.FlowRate",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_coarsness",
            entity="ConsumerProducts.CoffeeMaker.Option.Coarsness",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_coffee_strength",
            entity="ConsumerProducts.CoffeeMaker.Option.CoffeeStrength",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_aroma_select",
            entity="ConsumerProducts.CoffeeMaker.Option.AromaSelect",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_bean_container",
            entity="ConsumerProducts.CoffeeMaker.Option.BeanContainerSelection",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_shot_count",
            entity="ConsumerProducts.CoffeeMaker.Option.Shot.Count",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSelectEntityDescription(
            key="select_cups",
            entity="ConsumerProducts.CoffeeMaker.Option.Cups",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
    ],
    "switch": [
        HCSwitchEntityDescription(
            key="switch_multiple_beverages",
            entity="ConsumerProducts.CoffeeMaker.Option.MultipleBeverages",
            device_class=SwitchDeviceClass.SWITCH,
        ),
    ],
    "number": [
        HCNumberEntityDescription(
            key="number_fill_quantity",
            entity="ConsumerProducts.CoffeeMaker.Option.FillQuantity",
            device_class=NumberDeviceClass.VOLUME,
            native_unit_of_measurement=UnitOfVolume.MILLILITERS,
            mode=NumberMode.BOX,
        )
    ],
}
