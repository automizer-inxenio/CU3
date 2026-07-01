"""The automizer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import objects as inelsObj
from . import inelsClient2 as ic
from . import switch as sw
from . import light as l
from . import number as n
from . import sensor as s

# from . import integrationStorage as storage
from . import utils as utils

from homeassistant.const import CONF_HOST, CONF_PORT

from homeassistant.helpers.entity_platform import AddEntitiesCallback

import asyncio

from .const import DOMAIN, CONF_EXPORT, CONF_CU_NAME, CONF_YAML_CONFIG
import re
import uuid
import time
import logging
import yaml

_LOGGER = logging.getLogger(__name__)

# Prefijos de nombres internos de iNELS que no se deben exponer como entidades.
# Respaldo para exportaciones antiguas (3 columnas) donde las líneas internas
# no tienen prefijo "_ ". En el formato real (.is3) ya las filtra el startswith("_").
_INTERNAL_DEVICE_PREFIXES = (
    "Controller_",
    "Heat-Regulator_",
    "Cool-Regulator_",
)

# Lista de plataformas soportadas
_PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.warning(f"La entrada {entry.entry_id} ya está configurada.")
        return False

    hass.data[DOMAIN][entry.entry_id] = {}

    hass.data[DOMAIN][entry.entry_id] = {
        "numbers": [],
        "allEntities": [],
        "switches": [],
        "lights": [],
        "temperatureSensors": [],
        "humiditySensors": [],
        "analogSensors": [],
        "textSensors": [],
        "binarySensors": [],
        "ic": None,
    }
    export = entry.options.get(CONF_EXPORT) or entry.data[CONF_EXPORT]
    cu_host = entry.options.get(CONF_HOST) or entry.data[CONF_HOST]
    cu_port = entry.options.get(CONF_PORT) or entry.data[CONF_PORT]
    cu_name = entry.options.get(CONF_CU_NAME) or entry.data[CONF_CU_NAME]
    exportLines = export.splitlines()
    rDevice = re.compile(
        # Formato 3 columnas: nombre  ID            valor
        # Formato 4 columnas: nombre  módulo        ID            valor
        # El módulo (2ª columna en formato 4-col) empieza siempre por letra,
        # nunca por "0x", así que el grupo opcional no consume el ID.
        r"^(?P<deviceName>[a-zA-Z0-9_-]+)"
        r"\s+(?:[A-Za-z]\S*\s+)?"
        r"(?P<deviceId>0x[0-9A-Fa-f]+)"
    )

    yaml_config_str = entry.options.get(CONF_YAML_CONFIG) or entry.data.get(CONF_YAML_CONFIG, "")
    if yaml_config_str.strip():
        try:
            config_data = yaml.safe_load(yaml_config_str)
            _LOGGER.info("Usando configuración YAML desde opciones de la integración.")
        except yaml.YAMLError as e:
            _LOGGER.error(f"Error al parsear el YAML de configuración desde opciones: {e}")
            config_data = {}
    else:
        config_data = {}

    if config_data is None:
        _LOGGER.warning("El archivo de configuración está vacío o es inválido.")
        config_data = {}

    _LOGGER.info(f"config_data completo: {config_data}")

    automizer_section = config_data.get("automizer", {})
    _LOGGER.info(f"Sección automizer: {automizer_section}")

    # Procesar la configuración de números
    numbers_config = automizer_section.get("numbers", [])
    _LOGGER.info(f"Configuración de números cargada: {numbers_config}")
    analogSensors_config = automizer_section.get("analog", [])
    _LOGGER.info(
        f"Configuración de sensores analógicos cargada: {analogSensors_config}"
    )

    for exportLine in exportLines:
        if exportLine.startswith("_"):
            continue

        match = rDevice.match(exportLine)
        if match:
            _LOGGER.info(f"READ EXPORT LINE: {exportLine}")
            # print("READ EXPORT LINE: " + exportLine)
            deviceName = match.group("deviceName")
            deviceId = match.group("deviceId")

            # Filtro de respaldo: ignorar dispositivos internos de iNELS
            # (en el formato .is3 real ya van con "_ " y son filtrados arriba)
            if any(deviceName.startswith(p) for p in _INTERNAL_DEVICE_PREFIXES):
                continue

            fullDeviceName = cu_name + "_" + deviceName

            # BINARY_INPUT -> sensor(bool)
            if deviceId.startswith("0x0101"):
                newDevice = s.InelsBinarySensor(fullDeviceName, deviceId)
                hass.data[DOMAIN][entry.entry_id]["binarySensors"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # SWITCH -> switch
            if deviceId.startswith("0x0102"):
                newDevice = sw.InelsSwitch(fullDeviceName, deviceId)
                hass.data[DOMAIN][entry.entry_id]["switches"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # LIGHT -> light
            elif deviceId.startswith("0x0104"):
                newDevice = l.InelsLight(fullDeviceName, deviceId)
                hass.data[DOMAIN][entry.entry_id]["lights"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # TEMPERATURE -> sensor(float)
            elif deviceId.startswith("0x0105") and "%" not in exportLine:
                inelsTemperatureSensorToFind = fullDeviceName

                _LOGGER.info(
                    f"Buscando intervalo de actualizacion en el archivo de configuracion: {inelsTemperatureSensorToFind}"
                )
                refresh_seconds = next(
                    (
                        item.get("refresh_seconds", 0)
                        for item in analogSensors_config
                        if item["name"] == inelsTemperatureSensorToFind
                    ),
                    0,  # Valor predeterminado si no se encuentra el item
                )
                _LOGGER.info(
                    f"[TEMP] {inelsTemperatureSensorToFind}: refresh_seconds={refresh_seconds}"
                )

                newDevice = s.InelsTemperatureSensor(
                    fullDeviceName, deviceId, refresh_seconds
                )
                hass.data[DOMAIN][entry.entry_id]["temperatureSensors"].append(
                    newDevice
                )
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # HUMIDITY -> sensor(float)
            elif deviceId.startswith("0x0105") and "%" in exportLine:
                inelsHumiditySensorToFind = fullDeviceName
                _LOGGER.info(
                    f"Buscando intervalo de actualizacion en el archivo de configuracion: {inelsHumiditySensorToFind}"
                )
                refresh_seconds = next(
                    (
                        item.get("refresh_seconds", 0)
                        for item in analogSensors_config
                        if item["name"] == inelsHumiditySensorToFind
                    ),
                    0,  # Valor predeterminado si no se encuentra el item
                )

                newDevice = s.InelsHumiditySensor(
                    fullDeviceName, deviceId, refresh_seconds
                )
                hass.data[DOMAIN][entry.entry_id]["humiditySensors"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # BIT -> switch
            elif deviceId.startswith("0x0203"):
                newDevice = sw.InelsSwitch(fullDeviceName, deviceId)
                hass.data[DOMAIN][entry.entry_id]["switches"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # INTEGER -> number
            elif deviceId.startswith("0x0202"):
                inelsNumberToFind = fullDeviceName
                decimals = next(
                    (
                        item.get("decimals", 0)
                        for item in numbers_config
                        if item["name"] == inelsNumberToFind
                    ),
                    0,  # Valor predeterminado si no se encuentra el item
                )

                _LOGGER.info(
                    f"Buscando decimales en el archivo de configuracion: {inelsNumberToFind}"
                )
                _LOGGER.info(f"Creando entero con decimales: {decimals}")
                newDevice = n.InelsNumber(fullDeviceName, deviceId, decimals)
                hass.data[DOMAIN][entry.entry_id]["numbers"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
            # AIN -> sensor(float)
            elif deviceId.startswith("0x0108"):
                inelsAnalogSensorToFind = fullDeviceName

                _LOGGER.info(
                    f"Buscando decimales en el archivo de configuracion: {inelsAnalogSensorToFind}"
                )
                decimals = next(
                    (
                        item.get("decimals", 0)
                        for item in analogSensors_config
                        if item["name"] == inelsAnalogSensorToFind
                    ),
                    0,  # Valor predeterminado si no se encuentra el item
                )

                _LOGGER.info(
                    f"Buscando intervalo de actualizacion en el archivo de configuracion: {inelsAnalogSensorToFind}"
                )
                refresh_seconds = next(
                    (
                        item.get("refresh_seconds", 0)
                        for item in analogSensors_config
                        if item["name"] == inelsAnalogSensorToFind
                    ),
                    0,  # Valor predeterminado si no se encuentra el item
                )

                newDevice = s.InelsAnalogSensor(
                    fullDeviceName, deviceId, decimals, refresh_seconds
                )
                hass.data[DOMAIN][entry.entry_id]["analogSensors"].append(newDevice)
                hass.data[DOMAIN][entry.entry_id]["allEntities"].append(newDevice)
        else:
            continue

    # AÑADIOS UN SENSOR DE TIPO TEXTO PARA EL ESTADO DE LA CENTRALITA
    cuStateSensor = s.InelsTextSensor(
        cu_name + "_status", cu_name + "_status"
    )
    hass.data[DOMAIN][entry.entry_id]["textSensors"].append(cuStateSensor)

    # AÑADIMOS UN SENSOR DE TIPO BINARIO PARA EL ESTADO DE LA CONEXION DE TELNET
    clientConnectionStatus = s.InelsBinarySensor(
        cu_name + "_client_connected",
        cu_name + "_status",
    )
    hass.data[DOMAIN][entry.entry_id]["binarySensors"].append(clientConnectionStatus)

    await hass.config_entries.async_forward_entry_setups(
        # entry, [Platform.SWITCH, Platform.NUMBER]
        entry,
        [
            Platform.SWITCH,
            Platform.LIGHT,
            Platform.NUMBER,
            Platform.SENSOR,
        ],
    )

    # LANZAOS EL CLIENTE DE TELNET
    cu = inelsObj.InelsCentralUnit(
        cu_name,
        cu_host,
        cu_port,
    )

    storage = hass.data[DOMAIN][entry.entry_id]
    storage["ic"] = ic.InelsClient2(
        cu, storage["allEntities"], cuStateSensor, clientConnectionStatus
    )

    # Asignamos el cliente de Telnet a cada entidad
    # Esto es necesario para que las entidades puedan enviar comandos al cliente
    # de Telnet y recibir actualizaciones de estado. Algunos dispositivos usaran el cliente para enviar comandos y otros, como los sensores, no.
    for entity in storage["allEntities"]:
        entity.ic = storage["ic"]

    storage["ic"].start()

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descargar una entrada de configuración."""
    # Detener el cliente de Telnet si está en ejecución
    storage = hass.data[DOMAIN][entry.entry_id]
    if storage["ic"]:
        storage["ic"].stop()

    # Limpiar las entidades almacenadas
    storage["textSensors"].clear()
    storage["binarySensors"].clear()
    storage["switches"].clear()
    storage["lights"].clear()
    storage["numbers"].clear()
    storage["temperatureSensors"].clear()
    storage["humiditySensors"].clear()
    storage["analogSensors"].clear()
    storage["allEntities"].clear()

    # Verificar si las plataformas están registradas antes de intentar descargarlas
    if entry.entry_id not in hass.data.get(DOMAIN, {}):
        _LOGGER.warning(f"La entrada {entry.entry_id} no estaba cargada.")
        return True

    # Descargar las plataformas
    unloaded = await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    if not unloaded:
        _LOGGER.error("No se pudieron descargar las plataformas correctamente.")
        return False

    # Eliminar las entidades asociadas a esta entrada
    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Recargar una entrada de configuración."""
    _LOGGER.info(f"Recargando la integración {entry.title}")

    # Descargar la configuración existente
    await async_unload_entry(hass, entry)

    # Volver a cargar la configuración
    return await async_setup_entry(hass, entry)



