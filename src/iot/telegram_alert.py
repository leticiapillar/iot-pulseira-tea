"""Envia alertas ao professor via bot do Telegram.
Assina escola/sala1/alertas e envia só o pseudônimo e o nível (sem dados de saúde brutos).

Configuração (.env):
    TELEGRAM_BOT_TOKEN  token do bot, criado com o @BotFather
    TELEGRAM_CHAT_ID    id da conversa do professor (veja --descobrir-chat)
Sem token, o serviço roda em modo de teste: mostra no terminal a mensagem que enviaria.

Uso:
    python -m src.iot.telegram_alert                    # assina os alertas e envia
    python -m src.iot.telegram_alert --descobrir-chat   # mande "oi" ao bot antes; mostra o chat id
    python -m src.iot.telegram_alert --teste            # envia uma mensagem de teste

Cronograma: dia 13
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from src.iot.config import TOPICO_ALERTAS, cliente_mqtt

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
INTERVALO_MIN_S = 30   # no máximo 1 mensagem a cada 30 s por aluno (como no AutiSense)


def texto_alerta(alerta: dict) -> str:
    nome = alerta["aluno"].replace("aluno", "Aluno ")
    hora = time.strftime("%H:%M", time.localtime(alerta["t"]))
    if alerta["tipo"] == "inicio":
        return (f"⚠️ {nome}: sinais de agitação (nível {alerta['nivel']}) às {hora}.\n"
                "Sugestão: aproximar-se com calma e oferecer uma pausa sensorial.")
    return f"✅ {nome}: os sinais voltaram ao normal às {hora}."


def _api(metodo: str, **params) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/{metodo}"
    dados = urllib.parse.urlencode(params).encode() if params else None
    with urllib.request.urlopen(url, data=dados, timeout=10) as r:
        return json.loads(r.read())


def enviar(texto: str) -> None:
    if not (TOKEN and CHAT_ID):
        print(f"[modo de teste: sem TELEGRAM_BOT_TOKEN/CHAT_ID no .env]\n{texto}\n")
        return
    try:
        _api("sendMessage", chat_id=CHAT_ID, text=texto)
        print(f"enviado ao Telegram: {texto.splitlines()[0]}")
    except urllib.error.HTTPError as e:  # o Telegram explica o motivo no corpo da resposta
        try:
            motivo = json.loads(e.read()).get("description", "")
        except Exception:
            motivo = ""
        print(f"falha ao enviar ao Telegram (HTTP {e.code}: {motivo or e.reason}): {texto.splitlines()[0]}")
        if e.code in (400, 403):
            print("  confira o TELEGRAM_CHAT_ID (rode --descobrir-chat) e se você já deu Start no bot")
    except Exception as e:  # sem internet etc.: avisa e segue
        print(f"falha ao enviar ao Telegram ({e!r}): {texto.splitlines()[0]}")


def descobrir_chat() -> None:
    if not TOKEN:
        raise SystemExit("Preencha TELEGRAM_BOT_TOKEN no .env primeiro.")
    r = _api("getUpdates")
    chats = {u["message"]["chat"]["id"]: u["message"]["chat"].get("first_name", "")
             for u in r.get("result", []) if "message" in u}
    if not chats:
        print("Nenhuma conversa encontrada. Mande uma mensagem qualquer ao bot e rode de novo.")
    for cid, nome in chats.items():
        print(f"TELEGRAM_CHAT_ID={cid}   ({nome})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Alertas no Telegram")
    ap.add_argument("--descobrir-chat", action="store_true")
    ap.add_argument("--teste", action="store_true")
    args = ap.parse_args()
    if args.descobrir_chat:
        return descobrir_chat()
    if args.teste:
        return enviar("🔔 Teste da pulseira inteligente: o bot está funcionando.")

    ultimo_envio: dict[str, float] = {}
    cliente = cliente_mqtt("alertas-telegram")

    def ao_receber(_c, _userdata, m):
        try:
            alerta = json.loads(m.payload)
            agora = float(alerta["t"])  # horário do alerta (vale também na reprodução acelerada)
            chave = f"{alerta['aluno']}:{alerta['tipo']}"
            if agora - ultimo_envio.get(chave, -INTERVALO_MIN_S) < INTERVALO_MIN_S:
                return
            ultimo_envio[chave] = agora
            enviar(texto_alerta(alerta))
        except Exception as e:
            print(f"alerta inválido em {m.topic}: {e!r}")

    def ao_conectar(c, _userdata, _flags, _rc, _props=None):
        c.subscribe(TOPICO_ALERTAS, qos=1)  # assina de novo a cada reconexão

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber
    modo = "enviando ao Telegram" if TOKEN and CHAT_ID else "modo de teste (sem token)"
    print(f"Assinando {TOPICO_ALERTAS} ({modo}). Ctrl+C para parar.")
    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("encerrado")


if __name__ == "__main__":
    main()
