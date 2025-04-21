from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from.import integrationStorage as storage
async def async_setup_entry(hass,config_entry,async_add_entities):A=storage.numbers;async_add_entities(A)
class InelsNumber(NumberEntity):
	'Representación de un número con decimales configurables.'
	def __init__(A,inelsName,inelsId,decimals=2):D=decimals;C=inelsId;B=inelsName;A._attr_name=B;A._attr_step=1/10**D;A.native_min_value=-10000;A.native_max_value=10000;A._attr_value=2e1;A.inelsName=B;A.inelsId=C;A.unique_id=B+C;A.decimals=D
	@property
	def value(self):'Devuelve el valor actual del número.';return round(self._attr_value,self.decimals)
	def set_value(A,value):'Establece el valor del número.';A._attr_value=round(value,A.decimals);storage.ic.sendLine('SET '+A.inelsId+' '+str(A._attr_value));A.schedule_update_ha_state()
	def update(A):'Actualiza el estado de la entidad.';A.schedule_update_ha_state()
	@property
	def extra_state_attributes(self):'Añadir atributos personalizados al estado.';return{'decimals':self.decimals}