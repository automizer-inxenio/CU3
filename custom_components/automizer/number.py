from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry,ConfigType,DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from.import integrationStorage as storage
async def async_setup_entry(hass,config_entry,async_add_entities):A=storage.numbers;async_add_entities(A)
class InelsNumber(NumberEntity):
	'Representación de un número de ejemplo.'
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._attr_name=B;A._attr_step=1;A.native_min_value=-10000;A.native_max_value=10000;A._attr_value=20;A.inelsName=B;A.inelsId=C;A.unique_id=B+C
	@property
	def value(self):'Devuelve el valor actual del número.';return self._attr_value
	def set_value(A,value):'Establece el valor del número.';B=value;A._attr_value=B;storage.ic.sendLine('SET '+A.inelsId+' '+str(B));A.schedule_update_ha_state()
	def update(A):A.schedule_update_ha_state()