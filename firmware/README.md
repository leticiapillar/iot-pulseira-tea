# Firmware proposto: pulseira ESP32

Código de referência da pulseira física proposta. Neste trabalho a pulseira é **virtualizada** (veja `src/iot/virtual_wristband.py`), e este firmware documenta como seria a implementação real. Pode ser simulado no [Wokwi](https://wokwi.com).

## Componentes propostos

| Componente | Função | Interface |
|---|---|---|
| ESP32 DevKit | Microcontrolador com Wi-Fi | — |
| MAX30102 | Frequência cardíaca (PPG) | I2C |
| Módulo GSR (Grove) | Atividade eletrodérmica (suor) | ADC |
| MPU6050 | Acelerômetro e giroscópio (movimento) | I2C |
| Bateria LiPo 3,7 V + TP4056 | Alimentação e carga | — |

## Pinagem (a definir)

| Sensor | Pino ESP32 |
|---|---|
| MAX30102 SDA/SCL | GPIO 21 / GPIO 22 |
| MPU6050 SDA/SCL | GPIO 21 / GPIO 22 (mesmo barramento I2C) |
| GSR SIG | GPIO 34 (ADC) |

## Mensagem MQTT

Tópico: `escola/sala1/pulseira/<id_aluno>`

```json
{"ts": 1731100000, "hr": 92.4, "eda": 3.21, "acc_x": 0.02, "acc_y": -0.98, "acc_z": 0.11, "temp": 33.8}
```
