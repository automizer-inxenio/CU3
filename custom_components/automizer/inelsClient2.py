_B=True
_A=False
from.import switch as sw,light as l,number as n,sensor as s,objects as inelsObj,integrationStorage as storage,utils as utils
import socket,threading,time
class InelsClient2:
	def __init__(A,cu,entities,cuStateSensor,clientConnectionStatus):
		A.centralUnit=cu;A.host=cu.host;A.port=cu.port;A.sock=None;A.running=_A;A.cuStateSensor=cuStateSensor;A.clientConnectionStatus=clientConnectionStatus;A.initialGet=_B;A.entities={}
		for B in entities:A.entities[B.inelsId.lower()]=inelsObj.InelsDeviceValue(B.inelsName,B.inelsId,B)
		A.lock=threading.Lock()
	def connect(A):
		while A.running:
			try:A.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);A.sock.connect((A.host,A.port));print(f"Conectado a {A.host}:{A.port}");A.clientConnectionStatus._attr_is_on=_B;A.clientConnectionStatus.update();A.listen()
			except(ConnectionRefusedError,OSError):print('Error de conexión. Reintentando en 5 segundos...');A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update()
			A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update();time.sleep(5)
	def listen(A):
		B=''
		try:
			while A.running:
				C=A.sock.recv(1024)
				if not C:break
				B+=C.decode()
				while'\n'in B:D,B=B.split('\n',1);A.processLine(D)
		except(ConnectionResetError,OSError):print('Conexión perdida. Intentando reconectar...');A.clientConnectionStatus._attr_is_on=_A;A.clientConnectionStatus.update()
		finally:A.sock.close()
	def processLine(E,line):
		I=' ';G='0';D=line
		if D.startswith('GETSTATUS'):C=D.split(I);J=C[1].strip();print(f"Estado de la CU recibido: {J}");E.cuStateSensor._attr_native_value=J;E.cuStateSensor.update()
		elif D.startswith('EVENT'):
			C=D.split(I);H=C[2].strip().lower();B=C[3].strip();A=E.entities.get(H)
			if A:
				if isinstance(A.entity,s.InelsTemperatureSensor):print('EVENTO TERMOMETRO!!!!!');A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsHumiditySensor):print('EVENTO SENSOR HUMEDAD!!!!!');A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsBinarySensor):
					print('EVENTO SENSOR BINARIO!!!!!')
					if B==G:A.entity._attr_is_on=_A
					else:A.entity._attr_is_on=_B
				elif isinstance(A.entity,sw.InelsSwitch):
					print('EVENTO SWITCH!!!!!')
					if B==G:A.entity._state=_A
					else:A.entity._state=_B
				elif isinstance(A.entity,n.InelsNumber):print('EVENTO INTEGER!!!!!');A.entity._attr_value=int(B)
				elif isinstance(A.entity,l.InelsLight):
					print('EVENTO LIGHT: '+A.inelsName+' - '+B);F=utils.scaleValue0255(int(B))
					if F==0:A.entity._state=_A
					else:A.entity._state=_B;A.entity._brightness=F
				A.entity.update()
		elif D.startswith('GET')and E.initialGet:
			C=D.split(I);H=C[1].strip().lower();B=C[2].strip();A=E.entities.get(H)
			if A:
				if isinstance(A.entity,s.InelsTemperatureSensor):print('RESPUESTA A PETICION TERMOMETRO!!!!!');A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsHumiditySensor):print('RESPUESTA A PETICION SENSOR HUMEDAD!!!!!');A.entity._attr_native_value=int(B)/100
				elif isinstance(A.entity,s.InelsBinarySensor):
					print('RESPUESTA A SENSOR BINARIO!!!!!')
					if B==G:A.entity._attr_is_on=_A
					else:A.entity._attr_is_on=_B
				elif isinstance(A.entity,sw.InelsSwitch):
					print('RESPUESTA A PETICION SWITCH!!!!!')
					if B==G:A._state=_A
					else:A.entity._state=_B
				elif isinstance(A.entity,n.InelsNumber):print('RESPUESTA A PETICION INTEGER!!!!!');A.entity._attr_value=int(B)
				elif isinstance(A.entity,l.InelsLight):
					print('RESPUESTA A PETICION LIGHT!!!!!');F=int(B)
					if F==0:A.entity._state=_A
					else:A.entity._state=_B;A.entity._brightness=F
				A.entity.update()
	def sendLine(A,line):
		with A.lock:
			if A.sock:A.sock.sendall((line+'\r\n').encode())
	def start(A):A.running=_B;A.thread=threading.Thread(target=A.connect);A.thread.start()
	def stop(A):
		A.running=_A
		if A.sock:A.sock.close();A.thread.join()