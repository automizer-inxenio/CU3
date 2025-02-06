from enum import Enum
class DeviceType(Enum):SWITCH=0;LIGHT=1;TEMPERATURE=2;BINARY_INPUT=3;BIT=4;INTEGER=5
class InelsCentralUnit:
	def __init__(A,name,host,port):A.name=name;A.host=host;A.port=port
class InelsDeviceValue:
	def __init__(A,inelsName,inelsId,entity):A.inelsName=inelsName;A.inelsId=inelsId;A.entity=entity;A.state='';A.brightness=''
class InelsDevice:
	def __init__(A,deviceName,deviceId,deviceType):A.deviceName=deviceName;A.deviceId=deviceId;A.deviceType=deviceType