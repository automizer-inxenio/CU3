_A='SET '
from homeassistant.components.light import LightEntity,ColorMode,LightEntityFeature,ATTR_BRIGHTNESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry,ConfigType,DiscoveryInfoType
from.import utils as utils
async def async_setup_entry(hass,config_entry,async_add_entities):A=hass.data['automizer'][config_entry.entry_id];async_add_entities(A['lights'])
class InelsLight(LightEntity):
	def __init__(A,inelsName,inelsId):C=inelsId;B=inelsName;A._name=B;A.inelsName=B;A.inelsId=C;A._state=False;A.unique_id=B+C;A._brightness=255;A.ic=None
	@property
	def name(self):'Devuelve el nombre de la luz.';return self._name
	@property
	def is_on(self):'Devuelve True si la luz está encendida.';return self._state
	def turn_on(A,**C):
		if ATTR_BRIGHTNESS in C:A._brightness=C[ATTR_BRIGHTNESS];B=_A+A.inelsId+' '+str(utils.scaleValue2550(int(A._brightness)));A.ic.sendLine(B);A._state=True
		else:B=_A+A.inelsId+' '+str(utils.scaleValue2550(int(A._brightness)));A.ic.sendLine(B);A._state=True
	def turn_off(A,**B):A.ic.sendLine(_A+A.inelsId+' 0');A._state=False
	def update(A):A.schedule_update_ha_state()
	@property
	def brightness(self):return self._brightness
	@property
	def supported_color_modes(self):return{ColorMode.BRIGHTNESS}
	@property
	def color_mode(self):return ColorMode.BRIGHTNESS