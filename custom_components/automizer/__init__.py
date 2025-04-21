'The automizer integration.'
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from.import objects as inelsObj
from.import inelsClient2 as ic
from.import switch as sw
from.import light as l
from.import number as n
from.import sensor as s
from.import integrationStorage as storage
from.import utils as utils
from homeassistant.const import CONF_HOST,CONF_PORT
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import asyncio
from.const import DOMAIN,CONF_EXPORT,CONF_CU_NAME
import re,uuid,time,os,logging,yaml
_LOGGER=logging.getLogger(__name__)
_PLATFORMS=[Platform.LIGHT,Platform.SENSOR,Platform.SWITCH,Platform.NUMBER]
async def async_setup_entry(hass,entry):
	N='0x0105';J='_status';C=entry;O=C.data[CONF_EXPORT];P=O.splitlines();Q=re.compile('(?P<deviceName>[a-zA-Z0-9_-]+)\\s(?P<deviceType>[a-zA-Z0-9_-]+)\\s(?P<deviceId>[0-9A-F,x]+)');F=os.path.join(os.path.dirname(__file__),'configuration.yaml')
	try:G=await hass.async_add_executor_job(read_yaml_file,F)
	except FileNotFoundError:_LOGGER.info(f"No se encontró el archivo {F}.");G={}
	except yaml.YAMLError as H:_LOGGER.error(f"Error al leer el archivo {F} YAML: {H}");G={}
	K=G.get('automizer',{}).get('numbers',[]);_LOGGER.info(f"Configuración de números cargada: {K}")
	for E in P:
		if E.startswith('_'):continue
		I=Q.match(E)
		if I:
			_LOGGER.info(f"READ EXPORT LINE: {E}");R=I.group('deviceName');B=I.group('deviceId');D=C.data[CONF_CU_NAME]+'_'+R
			if B.startswith('0x0101'):A=s.InelsBinarySensor(D,B);storage.binarySensors.append(A);storage.allEntities.append(A)
			if B.startswith('0x0102'):A=sw.InelsSwitch(D,B);storage.switches.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0104'):A=l.InelsLight(D,B);storage.lights.append(A);storage.allEntities.append(A)
			elif B.startswith(N)and'%'not in E:A=s.InelsTemperatureSensor(D,B);storage.temperatureSensors.append(A);storage.allEntities.append(A)
			elif B.startswith(N)and'%'in E:A=s.InelsHumiditySensor(D,B);storage.humiditySensors.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0203'):A=sw.InelsSwitch(D,B);storage.switches.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0202'):S=D;T=next((A.get('decimals',0)for A in K if A['name']==S),0);A=n.InelsNumber(D,B,T);storage.numbers.append(A);storage.allEntities.append(A)
		else:continue
	L=s.InelsTextSensor(C.data[CONF_CU_NAME]+J,C.data[CONF_CU_NAME]+J);storage.textSensors.append(L);M=s.InelsBinarySensor(C.data[CONF_CU_NAME]+'_client_connected',C.data[CONF_CU_NAME]+J);storage.binarySensors.append(M);await hass.config_entries.async_forward_entry_setups(C,[Platform.SWITCH,Platform.LIGHT,Platform.NUMBER,Platform.SENSOR]);U=inelsObj.InelsCentralUnit(C.data[CONF_CU_NAME],C.data[CONF_HOST],C.data[CONF_PORT]);storage.ic=ic.InelsClient2(U,storage.allEntities,L,M);storage.ic.start();await asyncio.sleep(3);storage.ic.sendLine('GETSTATUS')
	for H in storage.allEntities:storage.ic.sendLine('GET '+H.inelsId);await asyncio.sleep(.2)
	return True
async def async_unload_entry(hass,entry):'Unload a config entry.';return await hass.config_entries.async_unload_platforms(entry,_PLATFORMS)
def read_yaml_file(file_path):
	'Función auxiliar para leer un archivo YAML.'
	with open(file_path,'r')as A:return yaml.safe_load(A)