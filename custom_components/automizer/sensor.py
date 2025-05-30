_A=None
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry,ConfigType,DiscoveryInfoType
from homeassistant.const import UnitOfTemperature,UnitOfElectricPotential,PERCENTAGE
async def async_setup_entry(hass,config_entry,async_add_entities):A=async_add_entities;B=hass.data['automizer'][config_entry.entry_id];A(B['binarySensors']);A(B['temperatureSensors']);A(B['humiditySensors']);A(B['textSensors']);A(B['analogSensors'])
class InelsBinarySensor(BinarySensorEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_is_on=False;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A.ic=_A
	@property
	def is_on(self):return self._attr_is_on
	def update(A):A.schedule_update_ha_state()
class InelsTemperatureSensor(SensorEntity):
	def __init__(A,inelsName,inelsId,refreshSeconds=1):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_unit_of_measurement=UnitOfTemperature.CELSIUS;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A._attr_icon='mdi:thermometer';A.ic=_A;A.refreshSeconds=refreshSeconds
	@property
	def native_value(self):return self._attr_native_value
	def update(A):A.schedule_update_ha_state()
class InelsAnalogSensor(SensorEntity):
	def __init__(A,inelsName,inelsId,decimals=3,refreshSeconds=1):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A._attr_icon='mdi:gauge';A.decimals=decimals;A.refreshSeconds=refreshSeconds;A.lastUpdate=0;A.ic=_A
	@property
	def native_value(self):return self._attr_native_value
	def update(A):A.schedule_update_ha_state()
class InelsHumiditySensor(SensorEntity):
	def __init__(A,inelsName,inelsId,refreshSeconds=1):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_unit_of_measurement=PERCENTAGE;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A._attr_icon='mdi:water-percent';A.ic=_A;A.refreshSeconds=refreshSeconds
	@property
	def native_value(self):return self._attr_native_value
	def update(A):A.schedule_update_ha_state()
class InelsTextSensor(SensorEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_native_value='STOP';A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A.ic=_A
	@property
	def native_value(self):return self._attr_native_value
	def set_value(A):0
	def update(A):A.schedule_update_ha_state()