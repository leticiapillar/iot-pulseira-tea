# Firmware proposto: pulseira ESP32

Código de referência da pulseira física proposta. Neste trabalho a pulseira é **virtualizada** (veja `src/iot/virtual_wristband.py`), e este firmware documenta como seria a implementação real. Pode ser simulado no [Wokwi](https://wokwi.com).

## Componentes propostos

| Componente | Função | Interface |
|---|---|---|
| ESP32 DevKit | Microcontrolador com Wi-Fi | — |
| MAX30102 | Frequência cardíaca (PPG) | I2C |
| Módulo GSR (Grove) | Atividade eletrodérmica (suor) | ADC |
| MAX30205 | Temperatura da pele | I2C |
| MPU6050 | Acelerômetro e giroscópio (movimento) | I2C |
| Bateria LiPo 3,7 V + TP4056 | Alimentação e carga | — |

## Pinagem (a definir)

| Sensor | Pino ESP32 |
|---|---|
| MAX30102 SDA/SCL | GPIO 21 / GPIO 22 |
| MAX30205 SDA/SCL | GPIO 21 / GPIO 22 (mesmo barramento I2C) |
| MPU6050 SDA/SCL | GPIO 21 / GPIO 22 (mesmo barramento I2C) |
| GSR SIG | GPIO 34 (ADC) |

## Mensagem MQTT

A pulseira publica **um pacote por segundo** com as amostras brutas, nas mesmas taxas da Empatica E4 (pulso 64 Hz, EDA e temperatura 4 Hz, acelerômetro 32 Hz). O processamento fica no servidor. O contrato completo (tópicos, QoS e mensagens de agitação e alerta) está na Seção 2.3 do relatório (`docs/relatorio/02_arquitetura_metodologia.md`).

Tópico: `escola/sala1/aluno/<id>/sinais` (QoS 0)

```json
{"aluno": "aluno03", "seq": 1234, "t": 1731100000.0,
 "bvp": [64 valores], "eda": [4 valores, µS], "temp": [4 valores, °C],
 "acc": [[x, y, z], ... 32 amostras, em g]}
```

O valor do ADC do módulo GSR precisa ser convertido para µS com a curva do módulo antes do envio.
