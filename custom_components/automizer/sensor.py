from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry,ConfigType,DiscoveryInfoType
from.import integrationStorage as storage
from homeassistant.const import UnitOfTemperature,PERCENTAGE
async def async_setup_entry(hass,config_entry,async_add_entities):A=async_add_entities;B=storage.binarySensors;C=storage.temperatureSensors;D=storage.textSensors;E=storage.humiditySensors;A(B);A(C);A(E);A(D)
class InelsBinarySensor(BinarySensorEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_is_on=False;A.inelsName=B;A.inelsId=C;A.unique_id=B+C
	@property
	def is_on(self):return self._attr_is_on
	def update(A):A.schedule_update_ha_state()
class InelsTemperatureSensor(SensorEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_unit_of_measurement=UnitOfTemperature.CELSIUS;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A._attr_icon='mdi:thermometer'
	@property
	def native_value(self):return self._attr_native_value
	def update(A):A.schedule_update_ha_state()
class InelsHumiditySensor(SensorEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_unit_of_measurement=PERCENTAGE;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A._attr_icon='mdi:water-percent'
	@property
	def native_value(self):return self._attr_native_value
	def update(A):A.schedule_update_ha_state()
class InelsTextSensor(SensorEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_value='STOP';A.inelsName=B;A.inelsId=C;A.unique_id=B+C
	@property
	def native_value(self):return self._attr_native_value
	def set_value(A):0
	def update(A):A.schedule_update_ha_state()