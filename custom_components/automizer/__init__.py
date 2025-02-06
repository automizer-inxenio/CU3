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
import re,uuid,time,os
_PLATFORMS=[Platform.LIGHT],[Platform.SENSOR],[Platform.SWITCH]
async def async_setup_entry(hass,entry):
	J='0x0105';G='_status';C=entry;K=C.data[CONF_EXPORT];L=K.splitlines();M=re.compile('(?P<deviceName>[a-zA-Z0-9_-]+)\\s(?P<deviceType>[a-zA-Z0-9_-]+)\\s(?P<deviceId>[0-9A-F,x]+)')
	for E in L:
		if E.startswith('_'):continue
		F=M.match(E)
		if F:
			print('READ EXPORT LINE: '+E);N=F.group('deviceName');B=F.group('deviceId');D=C.data[CONF_CU_NAME]+'_'+N
			if B.startswith('0x0101'):A=s.InelsBinarySensor(D,B);storage.binarySensors.append(A);storage.allEntities.append(A)
			if B.startswith('0x0102'):A=sw.InelsSwitch(D,B);storage.switches.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0104'):A=l.InelsLight(D,B);storage.lights.append(A);storage.allEntities.append(A)
			elif B.startswith(J)and'%'not in E:A=s.InelsTemperatureSensor(D,B);storage.temperatureSensors.append(A);storage.allEntities.append(A)
			elif B.startswith(J)and'%'in E:A=s.InelsHumiditySensor(D,B);storage.humiditySensors.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0203'):A=sw.InelsSwitch(D,B);storage.switches.append(A);storage.allEntities.append(A)
			elif B.startswith('0x0202'):A=n.InelsNumber(D,B);storage.numbers.append(A);storage.allEntities.append(A)
		else:continue
	H=s.InelsTextSensor(C.data[CONF_CU_NAME]+G,C.data[CONF_CU_NAME]+G);storage.textSensors.append(H);I=s.InelsBinarySensor(C.data[CONF_CU_NAME]+'_client_connected',C.data[CONF_CU_NAME]+G);storage.binarySensors.append(I);await hass.config_entries.async_forward_entry_setups(C,[Platform.SWITCH,Platform.LIGHT,Platform.NUMBER,Platform.SENSOR]);O=inelsObj.InelsCentralUnit(C.data[CONF_CU_NAME],C.data[CONF_HOST],C.data[CONF_PORT]);storage.ic=ic.InelsClient2(O,storage.allEntities,H,I);storage.ic.start();await asyncio.sleep(3);storage.ic.sendLine('GETSTATUS')
	for P in storage.allEntities:storage.ic.sendLine('GET '+P.inelsId);await asyncio.sleep(.2)
	return True
async def async_unload_entry(hass,entry):'Unload a config entry.';return await hass.config_entries.async_unload_platforms(entry,_PLATFORMS)