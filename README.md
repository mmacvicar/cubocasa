# Cubo Casa for Home Assistant component

Component to control [Cubo Casa](https://www.cubocasa.com.br/) boxes from home assistant. Requires grabbing a token from an autorized using an SSL proxy.

## Install HA component
1. Download the repository
2. Copy 'custom_components/cubocasa' folder inside Home Assistant config folder
3. configure your configuration.yaml:

```yaml
lock:
  - platform: cubocasa
    access_token: !secret cubocasa_token
```

# Cubo API Documentation

The Cubo API allows you to interact with IoT devices by performing various operations such as getting device status, listing devices, and opening or closing devices.

## Base URL

The base endpoint for the API is `https://iot.cubo.casa/api`.

## Authentication

API authentication is done by including a Bearer token in the header: `Bearer: xxxxxxxxxxxxxxxxxxxx`.

## Endpoints

### Get device status

GET /device/:device_id/status/


**Response:**

```json
{
  "status": true,
  "deviceStatus": "close",
  "updating": 0,
  "progress": 0,
  "firmware": "1.0.2",
  "online": 1
}
```

### List devices

GET /device/

**Response:**

```json
{
  "status": true,
  "devices": [
    {
      "id": 385,
      "name": "Cubo My House",
      "chip_id": "16405E-0009E758",
      "key": "a045387bf3fa14754882044b136abf1a9a5a3475c53120fdcd755a2b673fffff",
      "created_at": "2022-12-13 16:16:00",
      "status": "close",
      "door_status": "",
      "local_ip": "192.168.0.2",
      "online": 1,
      "wifi_strength": 0,
      "last_online": "2023-04-15 23:31:19",
      "firmware": "1.0.2",
      "channel": 2,
      "updating": 0,
      "progress": 0,
      "hash_url": ""
    }
  ]
}
```

### Open or Close device

POST /device/:device_id/
Content-Type: application/json

**Request Body**

```json
{
  "status": "open" | "close"
}
```