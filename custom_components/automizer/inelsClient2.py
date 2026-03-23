_B='GETSTATUS'
_A=False
from.import switch as sw,light as l,number as n,sensor as s,objects as inelsObj,utils as utils
import socket,threading,time,logging
_LOGGER=logging.getLogger(__name__)
INACTIVITY_TIMEOUT=60
RECONNECT_DELAY=5
_TCP_KEEPALIVE_IDLE=10
_TCP_KEEPALIVE_INTERVAL=5
_TCP_KEEPALIVE_COUNT=3
class InelsClient2:
	def __init__(A,cu,entities,cuStateSensor,clientConnectionStatus):
		A.centralUnit=cu;A.host=cu.host;A.port=cu.port;A.sock=None;A.running=_A;A.cuStateSensor=cuStateSensor;A.clientConnectionStatus=clientConnectionStatus;A.entities={}
		for B in entities:A.entities[B.inelsId.lower()]=inelsObj.InelsDeviceValue(B.inelsName,B.inelsId,B)
		A.lock=threading.Lock()
	def _create_socket(B):
		'Crea un socket TCP con keepalive habilitado.';A=socket.socket(socket.AF_INET,socket.SOCK_STREAM);A.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)
		if hasattr(socket,'TCP_KEEPIDLE'):A.setsockopt(socket.IPPROTO_TCP,socket.TCP_KEEPIDLE,_TCP_KEEPALIVE_IDLE)
		if hasattr(socket,'TCP_KEEPINTVL'):A.setsockopt(socket.IPPROTO_TCP,socket.TCP_KEEPINTVL,_TCP_KEEPALIVE_INTERVAL)
		if hasattr(socket,'TCP_KEEPCNT'):A.setsockopt(socket.IPPROTO_TCP,socket.TCP_KEEPCNT,_TCP_KEEPALIVE_COUNT)
		return A
	def _request_initial_states(A):
		'Solicita el estado de todas las entidades. Se llama tras cada conexión.';A.sendLine(_B)
		for B in A.entities.values():A.sendLine('GET '+B.inelsId);time.sleep(.1)
	def connect(A):
		while A.running:
			B=A._create_socket()
			try:
				B.connect((A.host,A.port))
				with A.lock:A.sock=B
				_LOGGER.info(f"Conectado a {A.host}:{A.port}");A.clientConnectionStatus._attr_is_on=True;A.clientConnectionStatus.update();A._request_initial_states();A.listen()
			except(ConnectionRefusedError,OSError)as C:_LOGGER.error(f"Error de conexión a {A.host}:{A.port}: {C}. Reintentando en {RECONNECT_DELAY}s...");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update()
			finally:
				with A.lock:A.sock=None
				try:B.close()
				except OSError:pass
			if A.running:time.sleep(RECONNECT_DELAY)
	def listen(A):
		B='';A.sock.settimeout(INACTIVITY_TIMEOUT)
		while A.running:
			try:
				D=A.sock.recv(1024)
				if not D:_LOGGER.warning(f"El servidor {A.host}:{A.port} cerró la conexión. Reconectando...");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update();break
				B+=D.decode('utf-8',errors='replace')
				while'\n'in B:E,B=B.split('\n',1);A.processLine(E.strip())
			except socket.timeout:
				_LOGGER.debug(f"Sin datos en {INACTIVITY_TIMEOUT}s ({A.host}). Enviando GETSTATUS como ping...")
				try:
					with A.lock:
						if A.sock:A.sock.sendall('GETSTATUS\r\n'.encode())
				except OSError as C:_LOGGER.error(f"Ping fallido en {A.host}:{A.port}: {C}. Reconectando...");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update();break
			except(ConnectionResetError,OSError)as C:
				if not A.running:break
				_LOGGER.error(f"Conexión perdida con {A.host}:{A.port}: {C}. Reconectando...");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update();break
	def processLine(F,line):
		I='0';H=' ';E=line
		if not F.running or not E:return
		if E.startswith(_B):
			C=E.split(H)
			if len(C)<2:return
			F.cuStateSensor._attr_native_value=C[1];F.cuStateSensor.update()
		elif E.startswith('EVENTSTATUS'):
			C=E.split(H)
			if len(C)<2:return
			F.cuStateSensor._attr_native_value=C[1];F.cuStateSensor.update()
		elif E.startswith('EVENT'):
			C=E.split(H)
			if len(C)<4:return
			J=C[2].lower();B=C[3];A=F.entities.get(J)
			if A:
				if isinstance(A.entity,s.InelsTemperatureSensor):
					if A.entity.refreshSeconds>0:
						K=A.entity.lastUpdate+A.entity.refreshSeconds
						if time.time()<K:return
						A.entity.lastUpdate=time.time()
					A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsHumiditySensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsBinarySensor):A.entity._attr_is_on=B!=I
				elif isinstance(A.entity,sw.InelsSwitch):A.entity._state=B!=I
				elif isinstance(A.entity,n.InelsNumber):D=A.entity.decimals;A.entity._attr_value=round(int(B)/10**D,D)
				elif isinstance(A.entity,s.InelsAnalogSensor):
					K=A.entity.lastUpdate+A.entity.refreshSeconds
					if time.time()<K:return
					A.entity.lastUpdate=time.time();D=A.entity.decimals;A.entity._attr_native_value=round(int(B)/10**D,D)
				elif isinstance(A.entity,l.InelsLight):
					G=utils.scaleValue0255(int(B));A.entity._state=G!=0
					if G!=0:A.entity._brightness=G
				A.entity.update()
		elif E.startswith('GET'):
			C=E.split(H)
			if len(C)<3:return
			J=C[1].lower();B=C[2]
			if not B.isdigit():return
			A=F.entities.get(J)
			if A:
				if isinstance(A.entity,s.InelsTemperatureSensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsHumiditySensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsBinarySensor):A.entity._attr_is_on=B!=I
				elif isinstance(A.entity,sw.InelsSwitch):A.entity._state=B!=I
				elif isinstance(A.entity,n.InelsNumber):D=A.entity.decimals;A.entity._attr_value=round(int(B)/10**D,D)
				elif isinstance(A.entity,s.InelsAnalogSensor):D=A.entity.decimals;A.entity._attr_value=round(int(B)/10**D,D)
				elif isinstance(A.entity,l.InelsLight):
					G=int(B);A.entity._state=G!=0
					if G!=0:A.entity._brightness=G
				A.entity.update()
	def sendLine(A,line):
		with A.lock:
			if not A.sock:_LOGGER.warning(f"Sin conexión activa con {A.host}:{A.port}. Comando descartado: %s",line);return
			try:A.sock.sendall((line+'\r\n').encode())
			except(BrokenPipeError,OSError)as B:_LOGGER.error(f"Error al enviar comando a {A.host}:{A.port}: {B}");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update()
	def start(A):A.running=True;A.thread=threading.Thread(target=A.connect,daemon=True);A.thread.start()
	def stop(A):
		A.running=_A
		with A.lock:
			if A.sock:
				try:A.sock.close()
				except OSError:pass
		if hasattr(A,'thread')and A.thread.is_alive():A.thread.join(timeout=10)