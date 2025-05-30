_B=True
_A=False
from.import switch as sw,light as l,number as n,sensor as s,objects as inelsObj,utils as utils
import socket,threading,time,logging
_LOGGER=logging.getLogger(__name__)
INACTIVITY_TIMEOUT=10
class InelsClient2:
	def __init__(A,cu,entities,cuStateSensor,clientConnectionStatus):
		A.centralUnit=cu;A.host=cu.host;A.port=cu.port;A.sock=None;A.running=_A;A.cuStateSensor=cuStateSensor;A.clientConnectionStatus=clientConnectionStatus;A.initialGet=_B;A.entities={}
		for B in entities:A.entities[B.inelsId.lower()]=inelsObj.InelsDeviceValue(B.inelsName,B.inelsId,B)
		A.lock=threading.Lock()
	def connect(A):
		while A.running:
			try:A.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);A.sock.connect((A.host,A.port));_LOGGER.info(f"Conectado a {A.host}:{A.port}");A.clientConnectionStatus._attr_is_on=_B;A.clientConnectionStatus.update();A.listen()
			except(ConnectionRefusedError,OSError)as B:_LOGGER.error(f"Error de conexión: {B}. Reintentando en 5 segundos...");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update();time.sleep(5)
			finally:
				if A.sock:A.sock.close()
	def listen(A):
		B=''
		try:
			A.sock.settimeout(INACTIVITY_TIMEOUT)
			while A.running:
				try:
					C=A.sock.recv(1024)
					if not C:break
					B+=C.decode()
					while'\n'in B:D,B=B.split('\n',1);A.processLine(D)
				except socket.timeout:_LOGGER.warning(f"No se recibió información en {INACTIVITY_TIMEOUT} segundos. Cerrando conexión...");break
		except(ConnectionResetError,OSError)as E:_LOGGER.error(f"Conexión perdida: {E}. Intentando reconectar...");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update()
		finally:
			if A.sock:A.sock.close()
	def processLine(E,line):
		J='0';I=' ';F=line
		if not E.running:return
		if F.startswith('GETSTATUS'):D=F.split(I);K=D[1].strip();E.cuStateSensor._attr_native_value=K;E.cuStateSensor.update()
		elif F.startswith('EVENTSTATUS'):D=F.split(I);K=D[1].strip();E.cuStateSensor._attr_native_value=K;E.cuStateSensor.update()
		elif F.startswith('EVENT'):
			D=F.split(I);L=D[2].strip().lower();B=D[3].strip();A=E.entities.get(L)
			if A:
				if isinstance(A.entity,s.InelsTemperatureSensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsHumiditySensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsBinarySensor):
					if B==J:A.entity._attr_is_on=_A
					else:A.entity._attr_is_on=_B
				elif isinstance(A.entity,sw.InelsSwitch):
					if B==J:A.entity._state=_A
					else:A.entity._state=_B
				elif isinstance(A.entity,n.InelsNumber):C=A.entity.decimals;G=round(int(B)/10**C,C);A.entity._attr_value=G
				elif isinstance(A.entity,s.InelsAnalogSensor):
					M=A.entity.lastUpdate+A.entity.refreshSeconds
					if time.time()<M:return
					A.entity.lastUpdate=time.time();C=A.entity.decimals;G=round(int(B)/10**C,C);A.entity._attr_native_value=G
				elif isinstance(A.entity,l.InelsLight):
					H=utils.scaleValue0255(int(B))
					if H==0:A.entity._state=_A
					else:A.entity._state=_B;A.entity._brightness=H
				A.entity.update()
		elif F.startswith('GET')and E.initialGet:
			D=F.split(I);L=D[1].strip().lower();B=D[2].strip()
			if not B.isdigit():return
			A=E.entities.get(L)
			if A:
				if isinstance(A.entity,s.InelsTemperatureSensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsHumiditySensor):A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsBinarySensor):
					if B==J:A.entity._attr_is_on=_A
					else:A.entity._attr_is_on=_B
				elif isinstance(A.entity,sw.InelsSwitch):
					if B==J:A._state=_A
					else:A.entity._state=_B
				elif isinstance(A.entity,n.InelsNumber):C=A.entity.decimals;G=round(int(B)/10**C,C);A.entity._attr_value=G
				elif isinstance(A.entity,s.InelsAnalogSensor):C=A.entity.decimals;G=round(int(B)/10**C,C);A.entity._attr_value=G
				elif isinstance(A.entity,l.InelsLight):
					H=int(B)
					if H==0:A.entity._state=_A
					else:A.entity._state=_B;A.entity._brightness=H
				A.entity.update()
	def sendLine(A,line):
		with A.lock:
			if not A.sock or A.sock.fileno()==-1:
				_LOGGER.warning('Conexión no operativa. Intentando reconectar...')
				try:A.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);A.sock.connect((A.host,A.port));_LOGGER.info(f"Reconectado a {A.host}:{A.port}");A.clientConnectionStatus._attr_is_on=_B;A.clientConnectionStatus.update()
				except(ConnectionRefusedError,OSError)as B:_LOGGER.error(f"No se pudo reconectar: {B}");A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update();return
			try:A.sock.sendall((line+'\r\n').encode())
			except(BrokenPipeError,OSError)as B:_LOGGER.error('Error al enviar la línea: %s',B);A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update()
	def start(A):A.running=_B;A.thread=threading.Thread(target=A.connect);A.thread.start()
	def stop(A):
		A.running=_A
		if A.sock:A.sock.close();A.thread.join()