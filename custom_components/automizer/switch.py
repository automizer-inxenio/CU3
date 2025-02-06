from homeassistant.helpers.entity import ToggleEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry,ConfigType,DiscoveryInfoType
from.import integrationStorage as storage
async def async_setup_entry(hass,config_entry,async_add_entities):A=storage.switches;async_add_entities(A)
class InelsSwitch(ToggleEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._name=B;A.inelsId=C;A.inelsName=B;A._state=False;A.unique_id=B+C
	@property
	def name(self):return self._name
	@property
	def is_on(self):return self._state
	def turn_on(A,**B):A._state=True;storage.ic.sendLine('SET '+A.inelsId+' 1');A.schedule_update_ha_state()
	def turn_off(A,**B):A._state=False;storage.ic.sendLine('SET '+A.inelsId+' 0');A.schedule_update_ha_state()
	def update(A):A.schedule_update_ha_state()