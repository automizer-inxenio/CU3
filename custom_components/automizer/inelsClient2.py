from . import switch as sw
from . import light as l
from . import number as n
from . import sensor as s
from . import objects as inelsObj
from . import utils as utils

import socket
import threading
import time
import logging

_LOGGER = logging.getLogger(__name__)

# Tiempo de espera configurable (en segundos) para detectar inactividad en el socket
INACTIVITY_TIMEOUT = 10


class InelsClient2:
    def __init__(
        self,
        cu: inelsObj.InelsCentralUnit,
        entities,
        cuStateSensor,
        clientConnectionStatus,
    ):
        self.centralUnit = cu
        self.host = cu.host
        self.port = cu.port
        self.sock = None
        self.running = False
        self.cuStateSensor = cuStateSensor
        self.clientConnectionStatus = clientConnectionStatus
        self.initialGet = True

        self.entities = {}
        for e in entities:
            self.entities[e.inelsId.lower()] = inelsObj.InelsDeviceValue(
                e.inelsName, e.inelsId, e
            )

        self.lock = threading.Lock()

    def connect(self):
        while self.running:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                _LOGGER.info(f"Conectado a {self.host}:{self.port}")
                self.clientConnectionStatus._attr_is_on = True
                self.clientConnectionStatus.update()
                self.listen()  # Escucha datos hasta que ocurra un problema
            except (ConnectionRefusedError, OSError) as e:
                _LOGGER.error(f"Error de conexión: {e}. Reintentando en 5 segundos...")
                self.clientConnectionStatus._attr_is_on = False
                self.clientConnectionStatus.update()
                time.sleep(5)
            finally:
                if self.sock:
                    self.sock.close()

    def listen(self):
        buffer = ""
        try:
            self.sock.settimeout(INACTIVITY_TIMEOUT)  # Usa la variable configurable
            while self.running:
                try:
                    data = self.sock.recv(1024)
                    if not data:
                        break
                    buffer += data.decode()
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        self.processLine(line)
                except socket.timeout:
                    _LOGGER.warning(
                        f"No se recibió información en {INACTIVITY_TIMEOUT} segundos. Cerrando conexión..."
                    )
                    break  # Sal del bucle para cerrar y reintentar la conexión
        except (ConnectionResetError, OSError) as e:
            _LOGGER.error(f"Conexión perdida: {e}. Intentando reconectar...")
            self.clientConnectionStatus._attr_is_on = False
            self.clientConnectionStatus.update()
        finally:
            if self.sock:
                self.sock.close()

    def processLine(self, line):
        if not self.running:
            return

        if line.startswith("GETSTATUS"):
            splittedLine = line.split(" ")
            status = splittedLine[1].strip()
            # print(f"Estado de la CU recibido: {status}")
            self.cuStateSensor._attr_native_value = status
            self.cuStateSensor.update()
        elif line.startswith("EVENTSTATUS"):
            splittedLine = line.split(" ")
            status = splittedLine[1].strip()
            # print(f"Estado de la CU recibido: {status}")
            self.cuStateSensor._attr_native_value = status
            self.cuStateSensor.update()
        elif line.startswith("EVENT"):
            splittedLine = line.split(" ")
            inelsId = splittedLine[2].strip().lower()
            cuValue = splittedLine[3].strip()

            foundValue = self.entities.get(inelsId)
            if foundValue:
                if isinstance(foundValue.entity, s.InelsTemperatureSensor):
                    foundValue.entity._attr_native_value = int(cuValue) / 100
                elif isinstance(foundValue.entity, s.InelsHumiditySensor):
                    foundValue.entity._attr_native_value = int(cuValue) / 100
                elif isinstance(foundValue.entity, s.InelsBinarySensor):
                    if cuValue == "0":
                        foundValue.entity._attr_is_on = False
                    else:
                        foundValue.entity._attr_is_on = True
                elif isinstance(foundValue.entity, sw.InelsSwitch):
                    if cuValue == "0":
                        foundValue.entity._state = False
                    else:
                        foundValue.entity._state = True
                elif isinstance(foundValue.entity, n.InelsNumber):
                    decimals = foundValue.entity.decimals
                    rounded_value = round(int(cuValue) / (10**decimals), decimals)
                    foundValue.entity._attr_value = rounded_value
                elif isinstance(foundValue.entity, s.InelsAnalogSensor):
                    nextRefreshPoint = (
                        foundValue.entity.lastUpdate + foundValue.entity.refreshSeconds
                    )
                    if time.time() < nextRefreshPoint:
                        return

                    foundValue.entity.lastUpdate = time.time()
                    decimals = foundValue.entity.decimals
                    rounded_value = round(int(cuValue) / (10**decimals), decimals)
                    foundValue.entity._attr_native_value = rounded_value
                elif isinstance(foundValue.entity, l.InelsLight):
                    intValue = utils.scaleValue0255(int(cuValue))
                    if intValue == 0:
                        foundValue.entity._state = False
                    else:
                        foundValue.entity._state = True
                        foundValue.entity._brightness = intValue

                foundValue.entity.update()
        elif line.startswith("GET") and self.initialGet:
            splittedLine = line.split(" ")
            inelsId = splittedLine[1].strip().lower()

            cuValue = splittedLine[2].strip()
            if not cuValue.isdigit():
                return

            foundValue = self.entities.get(inelsId)
            if foundValue:
                if isinstance(foundValue.entity, s.InelsTemperatureSensor):
                    # print("RESPUESTA A PETICION TERMOMETRO!!!!!")
                    foundValue.entity._attr_native_value = int(cuValue) / 100
                elif isinstance(foundValue.entity, s.InelsHumiditySensor):
                    # print("RESPUESTA A PETICION SENSOR HUMEDAD!!!!!")
                    foundValue.entity._attr_native_value = int(cuValue) / 100
                elif isinstance(foundValue.entity, s.InelsBinarySensor):
                    # print("RESPUESTA A SENSOR BINARIO!!!!!")
                    if cuValue == "0":
                        foundValue.entity._attr_is_on = False
                    else:
                        foundValue.entity._attr_is_on = True
                elif isinstance(foundValue.entity, sw.InelsSwitch):
                    # print("RESPUESTA A PETICION SWITCH!!!!!")
                    if cuValue == "0":
                        foundValue._state = False
                    else:
                        foundValue.entity._state = True
                elif isinstance(foundValue.entity, n.InelsNumber):
                    # print("RESPUESTA A PETICION INTEGER!!!!!")
                    decimals = foundValue.entity.decimals
                    rounded_value = round(int(cuValue) / (10**decimals), decimals)
                    foundValue.entity._attr_value = rounded_value
                    # foundValue.entity._attr_value = int(cuValue)
                elif isinstance(foundValue.entity, s.InelsAnalogSensor):
                    decimals = foundValue.entity.decimals
                    rounded_value = round(int(cuValue) / (10**decimals), decimals)
                    foundValue.entity._attr_value = rounded_value
                elif isinstance(foundValue.entity, l.InelsLight):
                    # print("RESPUESTA A PETICION LIGHT!!!!!")
                    intValue = int(cuValue)
                    if intValue == 0:
                        foundValue.entity._state = False
                    else:
                        foundValue.entity._state = True
                        foundValue.entity._brightness = intValue

                foundValue.entity.update()

    def sendLine(self, line):
        with self.lock:
            if (
                not self.sock or self.sock.fileno() == -1
            ):  # Verifica si la conexión está cerrada
                _LOGGER.warning("Conexión no operativa. Intentando reconectar...")
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect((self.host, self.port))
                    _LOGGER.info(f"Reconectado a {self.host}:{self.port}")
                    self.clientConnectionStatus._attr_is_on = True
                    self.clientConnectionStatus.update()
                except (ConnectionRefusedError, OSError) as e:
                    _LOGGER.error(f"No se pudo reconectar: {e}")
                    self.clientConnectionStatus._attr_is_on = False
                    self.clientConnectionStatus.update()
                    return  # No se puede enviar la línea si no se reconecta

            try:
                self.sock.sendall((line + "\r\n").encode())
                # _LOGGER.info(f"Línea enviada: {line}")
            except (BrokenPipeError, OSError) as e:
                _LOGGER.error("Error al enviar la línea: %s", e)
                self.clientConnectionStatus._attr_is_on = False
                self.clientConnectionStatus.update()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.connect)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
            self.thread.join()
