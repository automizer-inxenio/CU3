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

# Segundos sin datos antes de enviar un GETSTATUS como ping para verificar la conexión
INACTIVITY_TIMEOUT = 60
# Espera entre intentos de reconexión (segundos)
RECONNECT_DELAY = 5
# Parámetros TCP keepalive
_TCP_KEEPALIVE_IDLE = 10      # segundos sin actividad antes del primer probe
_TCP_KEEPALIVE_INTERVAL = 5   # segundos entre probes
_TCP_KEEPALIVE_COUNT = 3      # probes fallidos antes de declarar la conexión muerta


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

        self.entities = {}
        for e in entities:
            self.entities[e.inelsId.lower()] = inelsObj.InelsDeviceValue(
                e.inelsName, e.inelsId, e
            )

        self.lock = threading.Lock()

    def _create_socket(self):
        """Crea un socket TCP con keepalive habilitado."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, "TCP_KEEPIDLE"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, _TCP_KEEPALIVE_IDLE)
        if hasattr(socket, "TCP_KEEPINTVL"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, _TCP_KEEPALIVE_INTERVAL)
        if hasattr(socket, "TCP_KEEPCNT"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, _TCP_KEEPALIVE_COUNT)
        return sock

    def _request_initial_states(self):
        """Solicita el estado de todas las entidades. Se llama tras cada conexión."""
        self.sendLine("GETSTATUS")
        for device_value in self.entities.values():
            self.sendLine("GET " + device_value.inelsId)
            time.sleep(0.1)

    def connect(self):
        while self.running:
            sock = self._create_socket()
            try:
                sock.connect((self.host, self.port))
                with self.lock:
                    self.sock = sock
                _LOGGER.info(f"Conectado a {self.host}:{self.port}")
                self.clientConnectionStatus._attr_is_on = True
                self.clientConnectionStatus.update()
                self._request_initial_states()
                self.listen()
            except (ConnectionRefusedError, OSError) as e:
                _LOGGER.error(
                    f"Error de conexión a {self.host}:{self.port}: {e}. "
                    f"Reintentando en {RECONNECT_DELAY}s..."
                )
                self.clientConnectionStatus._attr_is_on = False
                self.clientConnectionStatus.update()
            finally:
                # El socket es propiedad exclusiva de este hilo; nadie más lo cierra
                with self.lock:
                    self.sock = None
                try:
                    sock.close()
                except OSError:
                    pass
            if self.running:
                time.sleep(RECONNECT_DELAY)

    def listen(self):
        buffer = ""
        self.sock.settimeout(INACTIVITY_TIMEOUT)
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    _LOGGER.warning(
                        f"El servidor {self.host}:{self.port} cerró la conexión. Reconectando..."
                    )
                    self.clientConnectionStatus._attr_is_on = False
                    self.clientConnectionStatus.update()
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.processLine(line.strip())
            except socket.timeout:
                # Sin datos durante INACTIVITY_TIMEOUT: enviamos un ping en lugar de reconectar
                _LOGGER.debug(
                    f"Sin datos en {INACTIVITY_TIMEOUT}s ({self.host}). "
                    "Enviando GETSTATUS como ping..."
                )
                try:
                    with self.lock:
                        if self.sock:
                            self.sock.sendall("GETSTATUS\r\n".encode())
                except OSError as e:
                    _LOGGER.error(
                        f"Ping fallido en {self.host}:{self.port}: {e}. Reconectando..."
                    )
                    self.clientConnectionStatus._attr_is_on = False
                    self.clientConnectionStatus.update()
                    break
            except (ConnectionResetError, OSError) as e:
                if not self.running:
                    # Cierre provocado por stop() — no es un error
                    break
                _LOGGER.error(
                    f"Conexión perdida con {self.host}:{self.port}: {e}. Reconectando..."
                )
                self.clientConnectionStatus._attr_is_on = False
                self.clientConnectionStatus.update()
                break

    def processLine(self, line):
        if not self.running or not line:
            return

        if line.startswith("GETSTATUS"):
            parts = line.split(" ")
            if len(parts) < 2:
                return
            self.cuStateSensor._attr_native_value = parts[1]
            self.cuStateSensor.update()
        elif line.startswith("EVENTSTATUS"):
            parts = line.split(" ")
            if len(parts) < 2:
                return
            self.cuStateSensor._attr_native_value = parts[1]
            self.cuStateSensor.update()
        elif line.startswith("EVENT"):
            parts = line.split(" ")
            if len(parts) < 4:
                return
            inelsId = parts[2].lower()
            cuValue = parts[3]

            foundValue = self.entities.get(inelsId)
            if foundValue:
                try:
                    if isinstance(foundValue.entity, s.InelsTemperatureSensor):
                        if foundValue.entity.refreshSeconds > 0:
                            nextRefreshPoint = foundValue.entity.lastUpdate + foundValue.entity.refreshSeconds
                            if time.time() < nextRefreshPoint:
                                return
                            foundValue.entity.lastUpdate = time.time()
                        foundValue.entity._attr_native_value = int(cuValue) / 100
                    elif isinstance(foundValue.entity, s.InelsHumiditySensor):
                        foundValue.entity._attr_native_value = int(cuValue) / 100
                    elif isinstance(foundValue.entity, s.InelsBinarySensor):
                        foundValue.entity._attr_is_on = cuValue != "0"
                    elif isinstance(foundValue.entity, sw.InelsSwitch):
                        foundValue.entity._state = cuValue != "0"
                    elif isinstance(foundValue.entity, n.InelsNumber):
                        decimals = foundValue.entity.decimals
                        foundValue.entity._attr_native_value = round(int(cuValue) / (10**decimals), decimals)
                    elif isinstance(foundValue.entity, s.InelsAnalogSensor):
                        nextRefreshPoint = (
                            foundValue.entity.lastUpdate + foundValue.entity.refreshSeconds
                        )
                        if time.time() < nextRefreshPoint:
                            return
                        foundValue.entity.lastUpdate = time.time()
                        decimals = foundValue.entity.decimals
                        foundValue.entity._attr_native_value = round(int(cuValue) / (10**decimals), decimals)
                    elif isinstance(foundValue.entity, l.InelsLight):
                        intValue = utils.scaleValue0255(int(cuValue))
                        foundValue.entity._state = intValue != 0
                        if intValue != 0:
                            foundValue.entity._brightness = intValue

                    foundValue.entity.update()
                except (ValueError, IndexError) as e:
                    _LOGGER.warning(
                        f"Valor inválido en EVENT para {inelsId}: {cuValue!r} — {e}"
                    )
                    return
        elif line.startswith("GET"):
            parts = line.split(" ")
            if len(parts) < 3:
                return
            inelsId = parts[1].lower()
            cuValue = parts[2]

            foundValue = self.entities.get(inelsId)
            if foundValue:
                try:
                    if isinstance(foundValue.entity, s.InelsTemperatureSensor):
                        foundValue.entity._attr_native_value = int(cuValue) / 100
                    elif isinstance(foundValue.entity, s.InelsHumiditySensor):
                        foundValue.entity._attr_native_value = int(cuValue) / 100
                    elif isinstance(foundValue.entity, s.InelsBinarySensor):
                        foundValue.entity._attr_is_on = cuValue != "0"
                    elif isinstance(foundValue.entity, sw.InelsSwitch):
                        foundValue.entity._state = cuValue != "0"
                    elif isinstance(foundValue.entity, n.InelsNumber):
                        decimals = foundValue.entity.decimals
                        foundValue.entity._attr_native_value = round(int(cuValue) / (10**decimals), decimals)
                    elif isinstance(foundValue.entity, s.InelsAnalogSensor):
                        decimals = foundValue.entity.decimals
                        foundValue.entity._attr_native_value = round(int(cuValue) / (10**decimals), decimals)
                    elif isinstance(foundValue.entity, l.InelsLight):
                        intValue = int(cuValue)
                        foundValue.entity._state = intValue != 0
                        if intValue != 0:
                            foundValue.entity._brightness = intValue

                    foundValue.entity.update()
                except (ValueError, IndexError) as e:
                    _LOGGER.warning(
                        f"Valor inválido en GET para {inelsId}: {cuValue!r} — {e}"
                    )
                    return

    def sendLine(self, line):
        with self.lock:
            if not self.sock:
                _LOGGER.warning(
                    f"Sin conexión activa con {self.host}:{self.port}. "
                    "Comando descartado: %s", line
                )
                return
            try:
                self.sock.sendall((line + "\r\n").encode())
            except (BrokenPipeError, OSError) as e:
                _LOGGER.error(
                    f"Error al enviar comando a {self.host}:{self.port}: {e}"
                )
                self.clientConnectionStatus._attr_is_on = False
                self.clientConnectionStatus.update()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.connect, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        with self.lock:
            if self.sock:
                try:
                    self.sock.close()
                except OSError:
                    pass
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join(timeout=10)
