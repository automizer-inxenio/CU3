from homeassistant.core import HomeAssistant
import hashlib
import base64


def scaleValue0255(sensorRawValue):
    if sensorRawValue < 0:
        sensorRawValue = 0
    elif sensorRawValue > 100:
        sensorRawValue = 100

    # Convertir el valor al nuevo rango
    scaledValue = int((sensorRawValue / 100) * 255)
    return scaledValue


def scaleValue2550(sensorRawValue):
    if sensorRawValue < 0:
        sensorRawValue = 0
    elif sensorRawValue > 255:
        sensorRawValue = 255

    # Convertir el valor al nuevo rango
    scaledValue = int((sensorRawValue / 255) * 100)
    return scaledValue


def testSerial(hass: HomeAssistant, serial: str):
    testString = hass.data["core.uuid"] + "INX-AUTOMIZER"
    sha256_hash = hashlib.sha256(testString.encode()).digest()
    base64_encoded_hash = base64.b64encode(sha256_hash).decode()
    if base64_encoded_hash == serial:
        return True
    else:
        return False
