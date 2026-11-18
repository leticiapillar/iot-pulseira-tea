"""Configuração comum da demo IoT (lida do .env) e nomes dos tópicos MQTT.

Contrato dos tópicos e mensagens: Seção 2.3 do relatório
(docs/relatorio/02_arquitetura_metodologia.md).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
SALA = os.getenv("MQTT_SALA", "escola/sala1").split("#")[0].strip().rstrip("/")

# modelo da demo: treinado SEM os participantes reproduzidos como alunos
MODELO = Path(os.getenv("MODELO", ROOT / "models" / "modelo_demo_sem_S8_S10_S15.joblib"))

# alunos da demo: pseudônimo -> participante do WESAD (fora do treino do modelo da demo)
ALUNOS_DEMO = {"aluno01": "S10", "aluno02": "S15", "aluno03": "S8"}


def topico_sinais(aluno: str = "+") -> str:
    return f"{SALA}/aluno/{aluno}/sinais"


def topico_agitacao(aluno: str = "+") -> str:
    return f"{SALA}/aluno/{aluno}/agitacao"


TOPICO_ALERTAS = f"{SALA}/alertas"


def cliente_mqtt(nome: str):
    """Cliente paho-mqtt (API v2) já conectado ao broker."""
    import paho.mqtt.client as mqtt

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=nome)
    try:
        c.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    except OSError as e:
        raise SystemExit(f"Não consegui conectar ao broker MQTT em {MQTT_HOST}:{MQTT_PORT} ({e}).\n"
                         "Suba o broker com: docker compose up -d mosquitto") from e
    return c
