# CU3 - Integración para Home Assistant

Esta es una integración personalizada para [Home Assistant](https://www.home-assistant.io/) que permite conectar centralitas **iNELS** con Home Assistant utilizando la interfaz ASCII de las centralitas antiguas.

## Descripción

La integración CU3 está diseñada para interactuar con centralitas iNELS a través de su protocolo ASCII, permitiendo a los usuarios controlar y monitorizar dispositivos conectados a estas centralitas directamente desde Home Assistant. Esto incluye dispositivos como luces, interruptores, sensores de temperatura, sensores de humedad y más.

## Características

- **Compatibilidad con centralitas antiguas**: Utiliza la interfaz ASCII para comunicarse con centralitas iNELS más antiguas.
- **Soporte para múltiples dispositivos**: Controla y monitoriza luces, interruptores, sensores y otros dispositivos conectados a la centralita.
- **Integración directa con Home Assistant**: Configuración sencilla y soporte para automatizaciones y scripts.
- **Actualizaciones automáticas**: Soporte para actualizaciones y despliegue continuo a través de GitHub.

## Requisitos

- Una centralita iNELS compatible con la interfaz ASCII.
- Una instalación funcional de [Home Assistant](https://www.home-assistant.io/).
- Conexión de red entre Home Assistant y la centralita iNELS.
- Un export del proyecto IDM3 en formato is3. Solo se integraran los dispositivos marcados para export en IDM3

## Instalación

1. **Descarga la integración**:
   - Utiliza HACS para descargar e instalar la integración.

2. **Ejecuta la instalacion de automizer**:
   - En Dispositivos y servicios -> Añadir integracion, instala la integracion automize.

3. **Obten un numero de licencia valido**:
   - Proporcionale a tu proveedor el identificador de instalacion que tendras visible al ejecutar la instalacion de automizer. El te proporcionara el numero de serie necesario para continuar con la instalacion. Deberas copiarlo en el campo adecuado del instalador de automizer.

4. **Rellena el resto de campos necesarios para la instalacion**:
   - Asegúrate de que la centralita iNELS esté configurada para aceptar conexiones a través de la interfaz ASCII.
   - Asegurate de que el separador que usara la centralita es el ESPACIO EN BLANCO
   - Copia y pega el contenido de tu export is3 en el campo designado.
