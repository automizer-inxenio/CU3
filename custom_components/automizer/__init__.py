'The automizer integration.'
from __future__ import annotations
_J='textSensors'
_I='analogSensors'
_H='humiditySensors'
_G='temperatureSensors'
_F='lights'
_E='binarySensors'
_D='switches'
_C='numbers'
_B='ic'
_A='allEntities'
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from.import objects as inelsObj
from.import inelsClient2 as ic
from.import switch as sw
from.import light as l
from.import number as n
from.import sensor as s
from.import utils as utils
from homeassistant.const import CONF_HOST,CONF_PORT
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import asyncio
from.const import DOMAIN,CONF_EXPORT,CONF_CU_NAME
import re,uuid,time,os,logging,yaml
_LOGGER=logging.getLogger(__name__)
_PLATFORMS=[Platform.LIGHT,Platform.SENSOR,Platform.SWITCH,Platform.NUMBER]
async def async_setup_entry(hass,entry):
	Z='decimals';Y='0x0105';S='_status';R='refresh_seconds';K='name';B=hass;A=entry
	if DOMAIN not in B.data:B.data[DOMAIN]={}
	if A.entry_id in B.data[DOMAIN]:_LOGGER.warning(f"La entrada {A.entry_id} ya está configurada.");return False
	B.data[DOMAIN][A.entry_id]={};B.data[DOMAIN][A.entry_id]={_C:[],_A:[],_D:[],_F:[],_G:[],_H:[],_I:[],_J:[],_E:[],_B:None};a=A.data[CONF_EXPORT];b=a.splitlines();c=re.compile('(?P<deviceName>[a-zA-Z0-9_-]+)\\s(?P<deviceType>[a-zA-Z0-9_-]+)\\s(?P<deviceId>[0-9A-F,x]+)');L=os.path.join(os.path.dirname(__file__),'configuration.yaml');_LOGGER.info(f"Leyendo configuración desde: {L}")
	try:F=await B.async_add_executor_job(read_yaml_file,L)
	except FileNotFoundError:_LOGGER.info(f"No se encontró el archivo {L}.");F={}
	except yaml.YAMLError as d:_LOGGER.error(f"Error al leer el archivo {L} YAML: {d}");F={}
	if F is None:_LOGGER.warning('El archivo de configuración está vacío o es inválido.');F={}
	_LOGGER.info(f"config_data completo: {F}");O=F.get('automizer',{});_LOGGER.info(f"Sección automizer: {O}");T=O.get(_C,[]);_LOGGER.info(f"Configuración de números cargada: {T}");H=O.get('analog',[]);_LOGGER.info(f"Configuración de sensores analógicos cargada: {H}")
	for I in b:
		if I.startswith('_'):continue
		P=c.match(I)
		if P:
			_LOGGER.info(f"READ EXPORT LINE: {I}");e=P.group('deviceName');D=P.group('deviceId');E=A.data[CONF_CU_NAME]+'_'+e
			if D.startswith('0x0101'):C=s.InelsBinarySensor(E,D);B.data[DOMAIN][A.entry_id][_E].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			if D.startswith('0x0102'):C=sw.InelsSwitch(E,D);B.data[DOMAIN][A.entry_id][_D].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			elif D.startswith('0x0104'):C=l.InelsLight(E,D);B.data[DOMAIN][A.entry_id][_F].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			elif D.startswith(Y)and'%'not in I:Q=E;_LOGGER.info(f"Buscando intervalo de actualizacion en el archivo de configuracion: {Q}");G=next((A.get(R,0)for A in H if A[K]==Q),0);_LOGGER.info(f"[TEMP] {Q}: refresh_seconds={G}");C=s.InelsTemperatureSensor(E,D,G);B.data[DOMAIN][A.entry_id][_G].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			elif D.startswith(Y)and'%'in I:U=E;_LOGGER.info(f"Buscando intervalo de actualizacion en el archivo de configuracion: {U}");G=next((A.get(R,0)for A in H if A[K]==U),0);C=s.InelsHumiditySensor(E,D,G);B.data[DOMAIN][A.entry_id][_H].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			elif D.startswith('0x0203'):C=sw.InelsSwitch(E,D);B.data[DOMAIN][A.entry_id][_D].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			elif D.startswith('0x0202'):V=E;M=next((A.get(Z,0)for A in T if A[K]==V),0);_LOGGER.info(f"Buscando decimales en el archivo de configuracion: {V}");_LOGGER.info(f"Creando entero con decimales: {M}");C=n.InelsNumber(E,D,M);B.data[DOMAIN][A.entry_id][_C].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
			elif D.startswith('0x0108'):N=E;_LOGGER.info(f"Buscando decimales en el archivo de configuracion: {N}");M=next((A.get(Z,0)for A in H if A[K]==N),0);_LOGGER.info(f"Buscando intervalo de actualizacion en el archivo de configuracion: {N}");G=next((A.get(R,0)for A in H if A[K]==N),0);C=s.InelsAnalogSensor(E,D,M,G);B.data[DOMAIN][A.entry_id][_I].append(C);B.data[DOMAIN][A.entry_id][_A].append(C)
		else:continue
	W=s.InelsTextSensor(A.data[CONF_CU_NAME]+S,A.data[CONF_CU_NAME]+S);B.data[DOMAIN][A.entry_id][_J].append(W);X=s.InelsBinarySensor(A.data[CONF_CU_NAME]+'_client_connected',A.data[CONF_CU_NAME]+S);B.data[DOMAIN][A.entry_id][_E].append(X);await B.config_entries.async_forward_entry_setups(A,[Platform.SWITCH,Platform.LIGHT,Platform.NUMBER,Platform.SENSOR]);f=inelsObj.InelsCentralUnit(A.data[CONF_CU_NAME],A.data[CONF_HOST],A.data[CONF_PORT]);J=B.data[DOMAIN][A.entry_id];J[_B]=ic.InelsClient2(f,J[_A],W,X)
	for g in J[_A]:g.ic=J[_B]
	J[_B].start();return True
async def async_get_options_flow(config_entry):from.options_flow import AutomizerOptionsFlowHandler as A;return A(config_entry)
async def async_unload_entry(hass,entry):
	'Descargar una entrada de configuración.';C=hass;B=entry;A=C.data[DOMAIN][B.entry_id]
	if A[_B]:A[_B].stop()
	A[_J].clear();A[_E].clear();A[_D].clear();A[_F].clear();A[_C].clear();A[_G].clear();A[_H].clear();A[_I].clear();A[_A].clear()
	if B.entry_id not in C.data.get(DOMAIN,{}):_LOGGER.warning(f"La entrada {B.entry_id} no estaba cargada.");return True
	D=await C.config_entries.async_unload_platforms(B,_PLATFORMS)
	if not D:_LOGGER.error('No se pudieron descargar las plataformas correctamente.');return False
	C.data[DOMAIN].pop(B.entry_id,None);return True
async def async_reload_entry(hass,entry):'Recargar una entrada de configuración.';A=entry;_LOGGER.info(f"Recargando la integración {A.title}");await async_unload_entry(hass,A);return await async_setup_entry(hass,A)
def read_yaml_file(file_path):
	'Función auxiliar para leer un archivo YAML.'
	with open(file_path,'r')as A:return yaml.safe_load(A)