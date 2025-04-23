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
	O='0x0105';K='_status';E=hass;C=entry
	if DOMAIN not in E.data:E.data[DOMAIN]={}
	if C.entry_id in E.data[DOMAIN]:_LOGGER.warning(f"La entrada {C.entry_id} ya está configurada.");return False
	E.data[DOMAIN][C.entry_id]={};P=C.data[CONF_EXPORT];Q=P.splitlines();R=re.compile('(?P<deviceName>[a-zA-Z0-9_-]+)\\s(?P<deviceType>[a-zA-Z0-9_-]+)\\s(?P<deviceId>[0-9A-F,x]+)');G=os.path.join(os.path.dirname(__file__),'configuration.yaml')
	try:H=await E.async_add_executor_job(read_yaml_file,G)
	except FileNotFoundError:_LOGGER.info(f"No se encontró el archivo {G}.");H={}
	except yaml.YAMLError as I:_LOGGER.error(f"Error al leer el archivo {G} YAML: {I}");H={}
	L=H.get('automizer',{}).get('numbers',[]);_LOGGER.info(f"Configuración de números cargada: {L}")
	for F in Q:
		if F.startswith('_'):continue
		J=R.match(F)
		if J:
			_LOGGER.info(f"READ EXPORT LINE: {F}");S=J.group('deviceName');B=J.group('deviceId');D=C.data[CONF_CU_NAME]+'_'+S
			if B.startswith('0x0101'):A=s.InelsBinarySensor(D,B);storage.binarySensors.append(A);storage.allEntities.append(A)
			if B.startswith('0x0102'):A=sw.InelsSwitch(D,B);storage.switches.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0104'):A=l.InelsLight(D,B);storage.lights.append(A);storage.allEntities.append(A)
			elif B.startswith(O)and'%'not in F:A=s.InelsTemperatureSensor(D,B);storage.temperatureSensors.append(A);storage.allEntities.append(A)
			elif B.startswith(O)and'%'in F:A=s.InelsHumiditySensor(D,B);storage.humiditySensors.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0203'):A=sw.InelsSwitch(D,B);storage.switches.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0202'):T=D;U=next((A.get('decimals',0)for A in L if A['name']==T),0);A=n.InelsNumber(D,B,U);storage.numbers.append(A);storage.allEntities.append(A)
		else:continue
	M=s.InelsTextSensor(C.data[CONF_CU_NAME]+K,C.data[CONF_CU_NAME]+K);storage.textSensors.append(M);N=s.InelsBinarySensor(C.data[CONF_CU_NAME]+'_client_connected',C.data[CONF_CU_NAME]+K);storage.binarySensors.append(N);await E.config_entries.async_forward_entry_setups(C,[Platform.SWITCH,Platform.LIGHT,Platform.NUMBER,Platform.SENSOR]);V=inelsObj.InelsCentralUnit(C.data[CONF_CU_NAME],C.data[CONF_HOST],C.data[CONF_PORT]);storage.ic=ic.InelsClient2(V,storage.allEntities,M,N);storage.ic.start();await asyncio.sleep(3);storage.ic.sendLine('GETSTATUS')
	for I in storage.allEntities:storage.ic.sendLine('GET '+I.inelsId);await asyncio.sleep(.2)
	return True
async def async_unload_entry(hass,entry):
	'Descargar una entrada de configuración.';B=hass;A=entry
	if storage.ic:storage.ic.stop()
	storage.textSensors.clear();storage.binarySensors.clear();storage.switches.clear();storage.lights.clear();storage.numbers.clear();storage.temperatureSensors.clear();storage.humiditySensors.clear();storage.allEntities.clear()
	if A.entry_id not in B.data.get(DOMAIN,{}):_LOGGER.warning(f"La entrada {A.entry_id} no estaba cargada.");return True
	C=await B.config_entries.async_unload_platforms(A,_PLATFORMS)
	if not C:_LOGGER.error('No se pudieron descargar las plataformas correctamente.');return False
	B.data[DOMAIN].pop(A.entry_id,None);return True
async def async_reload_entry(hass,entry):'Recargar una entrada de configuración.';A=entry;_LOGGER.info(f"Recargando la integración {A.title}");await async_unload_entry(hass,A);return await async_setup_entry(hass,A)
def read_yaml_file(file_path):
	'Función auxiliar para leer un archivo YAML.'
	with open(file_path,'r')as A:return yaml.safe_load(A)