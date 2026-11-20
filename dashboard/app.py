"""Painel do professor (Streamlit).

Mostra, para cada aluno: o nível de agitação atual, a probabilidade de estresse
ao longo da sessão, o histórico de alertas, os horários de maior agitação e os
sinais recentes da pulseira.

Fontes de dados:
- MQTT (ao vivo): escola/sala1/aluno/+/agitacao (retida), escola/sala1/alertas e,
  só na aba "Sinais ao vivo", escola/sala1/aluno/+/sinais. Os sinais brutos ficam
  apenas em memória (últimos 60 s) e nunca são gravados.
- data/demo/*.csv: histórico gravado pelo serviço de inferência (só probabilidades
  e alertas).

Executar: streamlit run dashboard/app.py
Cronograma: dia 14
"""
from __future__ import annotations

import json
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.iot.config import (ALUNOS_DEMO, MQTT_HOST, MQTT_PORT, TOPICO_ALERTAS,  # noqa: E402
                            topico_agitacao, topico_sinais)

HIST_DIR = ROOT / "data" / "demo"
ATUALIZAR_S = 2          # o painel se redesenha a cada 2 s
SEM_SINAL_S = 75         # sem mensagem de agitação há mais que isso: "sem atualização recente"
LACUNA_GRAFICO_S = 90    # intervalos maiores que isso quebram a linha do gráfico
FUSO = datetime.now().astimezone().tzinfo

# status (paleta fixa: cor + ícone + texto, nunca só a cor)
NIVEIS = {
    "baixo":    ("🟢", "Baixo",    "#0ca30c", "#ffffff"),
    "moderado": ("🟡", "Moderado", "#fab219", "#0b0b0b"),
    "alto":     ("🔴", "Alto",     "#d03b3b", "#ffffff"),
}
ESTADOS = {
    "calibrando":  ("⏳", "Calibrando", "#6b6a63", "#ffffff"),
    "sinal_ruim":  ("⚠️", "Sinal ruim", "#6b6a63", "#ffffff"),
    "sem_dados":   ("⚪", "Aguardando pulseira", "#a3a29a", "#0b0b0b"),
    "desatualizado": ("⚪", "Sem atualização recente", "#a3a29a", "#0b0b0b"),
}
AZUL = "#2a78d6"
CONDICOES = {"baseline": "repouso", "estresse": "estresse (TSST)", "diversao": "diversão",
             "meditacao": "meditação", "transicao": "transição"}
CRITICO, BOM = "#d03b3b", "#0ca30c"


# ---------------------------------------------------------------- MQTT (ao vivo)

class Estado:
    """O que chega pelo MQTT, guardado em memória e compartilhado entre as sessões do navegador."""

    def __init__(self):
        self.lock = threading.Lock()
        self.conectado = False
        self.agitacao: dict[str, tuple[dict, float]] = {}       # aluno -> (mensagem, hora de chegada)
        self.alertas: deque[dict] = deque(maxlen=200)
        self.sinais: dict[str, deque[dict]] = {}                # aluno -> últimos 60 pacotes
        self.ultimo_sinal: dict[str, float] = {}                # aluno -> hora de chegada do último pacote


@st.cache_resource
def conectar() -> Estado:
    import paho.mqtt.client as mqtt

    estado = Estado()
    # client_id único: dois painéis abertos com o mesmo id se derrubariam no broker
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"painel-{uuid.uuid4().hex[:8]}")

    def ao_conectar(cli, _u, _f, rc, _p=None):
        estado.conectado = not rc.is_failure
        cli.subscribe([(topico_agitacao("+"), 0), (TOPICO_ALERTAS, 1), (topico_sinais("+"), 0)])

    def ao_desconectar(*_a):
        estado.conectado = False

    def ao_receber(_cli, _u, m):
        try:
            msg = json.loads(m.payload)
        except ValueError:
            return
        with estado.lock:
            if m.topic == TOPICO_ALERTAS:
                estado.alertas.append(msg)
            elif m.topic.endswith("/agitacao"):
                estado.agitacao[msg["aluno"]] = (msg, time.time())
            elif m.topic.endswith("/sinais"):
                estado.sinais.setdefault(msg["aluno"], deque(maxlen=60)).append(msg)
                estado.ultimo_sinal[msg["aluno"]] = time.time()

    c.on_connect, c.on_disconnect, c.on_message = ao_conectar, ao_desconectar, ao_receber
    c.connect_async(MQTT_HOST, MQTT_PORT, keepalive=60)   # não trava o painel se o broker estiver fora
    c.loop_start()                                         # reconecta sozinho
    return estado


# ---------------------------------------------------------------- histórico (CSV)

def _hora_local(t: pd.Series) -> pd.Series:
    return pd.to_datetime(t, unit="s", utc=True).dt.tz_convert(FUSO).dt.tz_localize(None)


@st.cache_data(ttl=ATUALIZAR_S)
def ler_historico(tipo: str, mtime: float) -> pd.DataFrame:
    arq = HIST_DIR / f"{tipo}.csv"
    if not arq.exists():
        return pd.DataFrame()
    df = pd.read_csv(arq)
    if df.empty or "sessao" not in df:
        return pd.DataFrame()
    df["hora"] = _hora_local(df["t"])
    return df


def historico(tipo: str) -> pd.DataFrame:
    arq = HIST_DIR / f"{tipo}.csv"
    return ler_historico(tipo, arq.stat().st_mtime if arq.exists() else 0.0)


def sessao_atual(df: pd.DataFrame) -> pd.DataFrame:
    """Para cada aluno, só as linhas da sessão mais recente."""
    if df.empty:
        return df
    ultima = df.groupby("aluno")["sessao"].transform("max")
    return df[df["sessao"] == ultima]


def alertas_da_sessao(alertas: pd.DataFrame, aluno: str, sessao) -> pd.DataFrame:
    if alertas.empty or sessao is None:
        return alertas.iloc[0:0]
    return alertas[(alertas["aluno"] == aluno) & np.isclose(alertas["sessao"], float(sessao), rtol=0, atol=0.01)].sort_values("t")


def em_episodio(alertas: pd.DataFrame, aluno: str, sessao) -> pd.Series | None:
    """Alerta de início do episódio em andamento (se houver) na sessão atual do aluno."""
    a = alertas_da_sessao(alertas, aluno, sessao)
    if a.empty or a.iloc[-1]["tipo"] != "inicio":
        return None
    return a.iloc[-1]


# ---------------------------------------------------------------- componentes

def selo(icone: str, texto: str, fundo: str, tinta: str) -> str:
    return (f'<span style="display:inline-block;padding:4px 12px;border-radius:999px;'
            f'background:{fundo};color:{tinta};font-weight:600;font-size:1.05rem">'
            f'{icone} {texto}</span>')


def nome(aluno: str) -> str:
    return aluno.replace("aluno", "Aluno ")


def cartao(aluno: str, estado: Estado, alertas: pd.DataFrame, mostrar_rotulo: bool) -> None:
    with estado.lock:
        msg, chegada = estado.agitacao.get(aluno, (None, 0.0))
    with st.container(border=True):
        st.markdown(f"**{nome(aluno)}**")
        if msg is None:
            st.markdown(selo(*ESTADOS["sem_dados"]), unsafe_allow_html=True)
            st.caption("Nenhuma mensagem desta pulseira ainda.")
            return
        recente = time.time() - chegada <= SEM_SINAL_S
        if not recente:
            st.markdown(selo(*ESTADOS["desatualizado"]), unsafe_allow_html=True)
        elif msg.get("nivel") in NIVEIS:
            st.markdown(selo(*NIVEIS[msg["nivel"]]), unsafe_allow_html=True)
        else:
            st.markdown(selo(*ESTADOS.get(msg.get("estado"), ESTADOS["sem_dados"])), unsafe_allow_html=True)

        hora = datetime.fromtimestamp(msg["t"]).strftime("%H:%M:%S")
        if not recente:
            ultimo = "" if msg.get("prob") is None else f": P(estresse) {msg['prob']:.0%}"
            st.caption(f"Última estimativa às {hora}{ultimo}. A pulseira parou de enviar dados "
                       "(desligada, fora do pulso ou sem Wi-Fi).")
            return
        if msg.get("prob") is not None:
            st.metric("Probabilidade de estresse", f"{msg['prob']:.0%}".replace(".", ","))
        elif msg.get("estado") == "calibrando":
            st.caption("Primeiros 5 min em repouso: aprendendo o nível de base do aluno.")
        elif msg.get("estado") == "sinal_ruim":
            st.caption("Janela com muito movimento ou pulseira frouxa: sem estimativa.")

        ep = em_episodio(alertas, aluno, msg.get("sessao"))
        if ep is not None:
            st.markdown(f"**Em episódio desde {ep['hora']:%H:%M}**")

        resumo = []
        if msg.get("fc") is not None:
            resumo.append(f"FC {msg['fc']:.0f} bpm")
        if msg.get("eda") is not None:
            resumo.append(f"EDA {msg['eda']:.2f} µS".replace(".", ","))
        if msg.get("temp") is not None:
            resumo.append(f"pele {msg['temp']:.1f} °C".replace(".", ","))
        st.caption(" · ".join(resumo + [f"atualizado às {hora}"]))
        if mostrar_rotulo and msg.get("rotulo"):
            st.caption(f"Condição no WESAD (só na demo): **{CONDICOES.get(msg['rotulo'], msg['rotulo'])}**")


def grafico_sessao(df: pd.DataFrame, alertas: pd.DataFrame, aluno: str, mostrar_rotulo: bool):
    d = df[(df["aluno"] == aluno)].sort_values("t").copy()
    if d.empty:
        return None
    # trechos sem sinal (ou o salto do modo --curta) quebram a linha
    d["trecho"] = (d["t"].diff() > LACUNA_GRAFICO_S).cumsum()
    d["prob_txt"] = d["prob"].map(lambda p: "—" if pd.isna(p) else f"{p:.0%}")
    if "rotulo" in d:
        d["condicao"] = d["rotulo"].map(CONDICOES).fillna(d["rotulo"])
    x = alt.X("hora:T", title=None, axis=alt.Axis(format="%H:%M", grid=False, tickMinStep=60_000))
    y = alt.Y("prob:Q", title="P(estresse)", scale=alt.Scale(domain=[0, 1]),
              axis=alt.Axis(format="%", values=[0, 0.5, 0.8, 1], gridColor="#e1e0d9"))
    camadas = []

    if mostrar_rotulo and "rotulo" in d:
        # faixas do protocolo do WESAD em que a condição é "estresse" (a "verdade" da demo)
        est = d[d["rotulo"] == "estresse"]
        if not est.empty:
            grupos = (est["t"].diff() > 45).cumsum()
            faixas = est.groupby(grupos).agg(ini=("hora", "min"), fim=("hora", "max")).reset_index()
            faixas["fim"] += pd.Timedelta(seconds=30)
            faixas["legenda"] = "estresse no protocolo do WESAD"
            camadas.append(alt.Chart(faixas).mark_rect(color="#eb6834", opacity=0.12).encode(
                x="ini:T", x2="fim:T", tooltip=alt.Tooltip("legenda:N", title="Faixa")))
            camadas.append(alt.Chart(faixas.head(1).assign(legenda="estresse (WESAD)")).mark_text(
                align="left", baseline="bottom", dx=4, dy=-4, color="#b4532a", fontSize=11)
                .encode(x="ini:T", y=alt.datum(0), text="legenda:N"))

    cal =d[d["estado"] == "calibrando"]
    if not cal.empty:
        faixa = pd.DataFrame({"ini": [cal["hora"].min() - pd.Timedelta(seconds=60)],
                              "fim": [cal["hora"].max()], "legenda": ["calibração (repouso)"]})
        camadas.append(alt.Chart(faixa).mark_rect(color="#a3a29a", opacity=0.15).encode(
            x="ini:T", x2="fim:T", tooltip=alt.Tooltip("legenda:N", title="Faixa")))
        camadas.append(alt.Chart(faixa).mark_text(align="left", baseline="bottom", dx=4, dy=-4, color="#6b6a63",
                                                  fontSize=11).encode(x="ini:T", y=alt.datum(0),
                                                                      text="legenda:N"))

    limiares = pd.DataFrame({"y": [0.5, 0.8], "rotulo": ["alerta (0,5)", "alto (0,8)"]})
    camadas.append(alt.Chart(limiares).mark_rule(strokeDash=[4, 4], color="#8a8980", strokeWidth=1)
                   .encode(y="y:Q"))
    limiares["hora"] = d["hora"].max()   # rótulos na ponta direita, longe das faixas
    camadas.append(alt.Chart(limiares).mark_text(align="right", dy=-6, color="#6b6a63", fontSize=11)
                   .encode(y="y:Q", text="rotulo:N", x="hora:T"))

    tooltip = [alt.Tooltip("hora:T", title="Hora", format="%H:%M:%S"),
               alt.Tooltip("prob_txt:N", title="P(estresse)"),
               alt.Tooltip("nivel:N", title="Nível"), alt.Tooltip("estado:N", title="Estado")]
    if mostrar_rotulo and "rotulo" in d:
        tooltip.append(alt.Tooltip("condicao:N", title="WESAD"))
    base = alt.Chart(d).encode(x=x, y=y)
    camadas.append(base.mark_line(color=AZUL, strokeWidth=2).encode(detail="trecho:N"))
    hover = alt.selection_point(on="pointerover", nearest=True, fields=["hora"], empty=False, clear="pointerout")
    camadas.append(base.mark_point(size=120, opacity=0).encode(tooltip=tooltip).add_params(hover))
    camadas.append(base.mark_point(size=70, filled=True, color=AZUL, stroke="white", strokeWidth=2)
                   .encode(opacity=alt.condition(hover, alt.value(1), alt.value(0))))

    a = alertas_da_sessao(alertas, aluno, d["sessao"].iloc[0])
    if not a.empty:
        a = a.assign(descricao=a["tipo"].map({"inicio": "▲ alerta de início", "fim": "▼ fim do episódio"}))
        camadas.append(alt.Chart(a).mark_rule(strokeWidth=2).encode(
            x="hora:T",
            color=alt.Color("descricao:N", title=None,
                            scale=alt.Scale(domain=["▲ alerta de início", "▼ fim do episódio"],
                                            range=[CRITICO, BOM]),
                            legend=alt.Legend(orient="top")),
            tooltip=[alt.Tooltip("hora:T", title="Hora", format="%H:%M:%S"),
                     alt.Tooltip("descricao:N", title="Evento")]))

    return alt.layer(*camadas).properties(height=220, title=nome(aluno)).configure_view(stroke=None)


def grafico_sinal(df: pd.DataFrame, y: str, titulo: str, cor: str = AZUL):
    return (alt.Chart(df).mark_line(color=cor, strokeWidth=1.5)
            .encode(x=alt.X("s:Q", title="segundos atrás", scale=alt.Scale(reverse=False)),
                    y=alt.Y(f"{y}:Q", title=None, scale=alt.Scale(zero=False)),
                    tooltip=[alt.Tooltip("s:Q", title="s", format=".1f"), alt.Tooltip(f"{y}:Q", format=".3f")])
            .properties(height=150, title=titulo).configure_view(stroke=None))


def sinais_recentes(pacotes: list[dict]) -> dict[str, pd.DataFrame]:
    """Concatena os últimos pacotes; tempo em segundos relativos ao último (negativo = passado)."""
    fim = pacotes[-1]["t"] + 1

    def serie(chave: str, fs: int, f=lambda v: v) -> pd.DataFrame:
        partes = []
        for p in pacotes:
            v = np.asarray(p[chave], dtype=float)
            if v.size:
                partes.append(pd.DataFrame({"s": p["t"] - fim + np.arange(len(v)) / fs, chave: f(v)}))
        return pd.concat(partes) if partes else pd.DataFrame({"s": [], chave: []})

    mag = lambda v: np.linalg.norm(v.reshape(-1, 3), axis=1)  # noqa: E731
    return {"bvp": serie("bvp", 64).query("s >= -10"), "eda": serie("eda", 4), "acc": serie("acc", 32, mag)}


# ---------------------------------------------------------------- página

st.set_page_config(page_title="Painel do professor", page_icon="⌚", layout="wide")
estado = conectar()

with st.sidebar:
    st.header("Pulseira inteligente")
    st.caption(f"Broker MQTT: {MQTT_HOST}:{MQTT_PORT}")
    mostrar_rotulo = st.toggle("Mostrar a condição do WESAD (demo)", value=True,
                               help="A pulseira virtual envia a condição do protocolo do WESAD, para "
                                    "comparar com o que o modelo estimou. Uma pulseira real não tem isso.")
    st.divider()
    st.caption("**Privacidade.** Os alunos aparecem só por pseudônimo. O histórico guarda apenas "
               "probabilidades e alertas; os sinais brutos ficam só em memória (últimos 60 s).")
    st.caption("Ferramenta de **apoio** ao professor, não de diagnóstico.")

st.title("Painel do professor · Sala 1")


@st.fragment(run_every=ATUALIZAR_S)
def ao_vivo() -> None:
    if not estado.conectado:
        st.warning(f"Sem conexão com o broker MQTT em {MQTT_HOST}:{MQTT_PORT}. "
                   "Suba com `docker compose up -d mosquitto`; o painel reconecta sozinho.")
    agit, alertas = historico("agitacao"), historico("alertas")

    # avisos na tela para alertas novos
    with estado.lock:
        novos = list(estado.alertas)
    vistos = st.session_state.setdefault("alertas_vistos", len(novos))
    for a in novos[vistos:]:
        if a["tipo"] == "inicio":
            st.toast(f"{nome(a['aluno'])}: sinais de agitação (nível {a['nivel']})", icon="⚠️")
        else:
            st.toast(f"{nome(a['aluno'])}: sinais voltaram ao normal", icon="✅")
    st.session_state["alertas_vistos"] = len(novos)

    with estado.lock:
        alunos = sorted(set(ALUNOS_DEMO) | set(estado.agitacao))
    for col, aluno in zip(st.columns(len(alunos)), alunos):
        with col:
            cartao(aluno, estado, alertas, mostrar_rotulo)

    aba_sessao, aba_alertas, aba_horarios, aba_sinais = st.tabs(
        ["Agitação na sessão", "Alertas", "Horários de maior agitação", "Sinais ao vivo"])

    with aba_sessao:
        atual = sessao_atual(agit)
        if atual.empty:
            st.info("Ainda não há histórico. Inicie o serviço de inferência e uma pulseira virtual.")
        else:
            st.caption("Probabilidade de estresse a cada 30 s (janelas de 60 s) na sessão mais recente de "
                       "cada aluno. Alerta: 2 janelas seguidas acima de 0,5.")
            for aluno in sorted(atual["aluno"].unique()):
                g = grafico_sessao(atual, alertas, aluno, mostrar_rotulo)
                if g is not None:
                    st.altair_chart(g, width="stretch")

    with aba_alertas:
        if alertas.empty:
            st.info("Nenhum alerta registrado.")
        else:
            so_atual = st.toggle("Só a sessão atual", value=True, key="alertas_sessao")
            a = (sessao_atual(alertas) if so_atual else alertas).sort_values("t", ascending=False)
            tabela = pd.DataFrame({
                "Hora": a["hora"].dt.strftime("%d/%m %H:%M:%S"),
                "Aluno": a["aluno"].map(nome),
                "Evento": a["tipo"].map({"inicio": "⚠️ início", "fim": "✅ fim"}),
                "Nível": a["nivel"],
                "P(estresse)": a["prob"].map(lambda p: f"{p:.0%}"),
            })
            if mostrar_rotulo and "rotulo" in a:
                tabela["WESAD (demo)"] = a["rotulo"].map(CONDICOES).fillna(a["rotulo"])
            st.dataframe(tabela, hide_index=True, width="stretch")

    with aba_horarios:
        validas = agit.dropna(subset=["prob"]) if not agit.empty else agit
        if validas.empty:
            st.info("Ainda não há estimativas no histórico.")
        else:
            c1, c2 = st.columns(2)
            aluno = c1.selectbox("Aluno", sorted(validas["aluno"].unique()), format_func=nome,
                                 key="horarios_aluno")
            passo = c2.selectbox("Agrupar por", ["10 min", "1 hora"], index=0)
            v = validas[validas["aluno"] == aluno].copy()
            v["faixa"] = v["hora"].dt.floor("10min" if passo == "10 min" else "1h")
            # cada janela representa 30 s novos de sinal
            minutos = (v.assign(agitado=v["prob"] >= 0.5).groupby("faixa")
                       .agg(min_agitado=("agitado", lambda s: s.sum() * 0.5),
                            min_monitorado=("agitado", lambda s: len(s) * 0.5),
                            prob_max=("prob", "max")).reset_index())
            minutos["faixa_txt"] = minutos["faixa"].dt.strftime("%d/%m %H:%M")
            st.caption("Minutos com probabilidade ≥ 0,5 em cada faixa de horário, em todo o histórico. "
                       "No uso real, acumulado ao longo de semanas, isso ajuda a ver se a agitação se "
                       "repete em certos momentos da rotina (recreio, troca de atividade, barulho).")
            barras = (alt.Chart(minutos).mark_bar(color=AZUL, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                      .encode(x=alt.X("faixa_txt:N", title=None, sort=None),
                              y=alt.Y("min_agitado:Q", title="minutos agitado"),
                              tooltip=[alt.Tooltip("faixa_txt:N", title="Início da faixa"),
                                       alt.Tooltip("min_agitado:Q", title="Min. agitado", format=".1f"),
                                       alt.Tooltip("min_monitorado:Q", title="Min. monitorado", format=".1f"),
                                       alt.Tooltip("prob_max:Q", title="P máx.", format=".0%")])
                      .properties(height=240).configure_view(stroke=None))
            st.altair_chart(barras, width="stretch")
            top = v.nlargest(5, "prob")
            st.markdown("**Momentos de maior probabilidade**")
            st.dataframe(pd.DataFrame({"Hora": top["hora"].dt.strftime("%d/%m %H:%M:%S"),
                                       "P(estresse)": top["prob"].map(lambda p: f"{p:.0%}"),
                                       "FC (bpm)": top.get("fc"), "EDA (µS)": top.get("eda")}),
                         hide_index=True, width="stretch")

    with aba_sinais:
        with estado.lock:
            com_sinal = {a: list(p) for a, p in estado.sinais.items()
                         if p and time.time() - estado.ultimo_sinal.get(a, 0) <= 10}
        if not com_sinal:
            st.info("Nenhuma pulseira enviando sinais agora.")
        else:
            aluno = st.selectbox("Aluno", sorted(com_sinal), format_func=nome, key="sinais_aluno")
            s = sinais_recentes(com_sinal[aluno])
            st.caption("Sinais brutos dos últimos segundos, mantidos só em memória (não são gravados). "
                       "O professor não precisa olhar isto: serve para conferir se a pulseira está bem colocada.")
            c1, c2, c3 = st.columns(3)
            c1.altair_chart(grafico_sinal(s["bvp"], "bvp", "Pulso (BVP), últimos 10 s"), width="stretch")
            c2.altair_chart(grafico_sinal(s["eda"], "eda", "Condutância da pele (µS), 60 s"),
                            width="stretch")
            c3.altair_chart(grafico_sinal(s["acc"], "acc", "Movimento (g), 60 s"), width="stretch")


ao_vivo()
