"""Gera o diagrama da arquitetura (docs/arquitetura/arquitetura.png).

Uso: python docs/arquitetura/gerar_diagrama.py
Cronograma: dia 12
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SAIDA = Path(__file__).resolve().parent / "arquitetura.png"

# uma cor por camada (paleta categórica fixa usada nas figuras do projeto)
CAMADA = {
    "percepcao": ("#2a78d6", "#e8f1fc"),
    "rede": ("#eb6834", "#fdece5"),
    "processamento": ("#1baf7a", "#e4f6ef"),
    "aplicacao": ("#eda100", "#fdf3dc"),
}
TINTA, TINTA2 = "#222222", "#555555"


def caixa(ax, x, y, w, h, camada, titulo, linhas=(), tracejada=False, fs_titulo=10.5):
    borda, fundo = CAMADA[camada]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fundo, ec=borda, lw=1.6, ls="--" if tracejada else "-"))
    ax.text(x + w / 2, y + h - 0.22, titulo, ha="center", va="top", fontsize=fs_titulo,
            fontweight="bold", color=TINTA)
    for i, l in enumerate(linhas):
        ax.text(x + w / 2, y + h - 0.62 - i * 0.30, l, ha="center", va="top", fontsize=8.3, color=TINTA2)


def seta(ax, p0, p1, rotulo=None, dx=0, dy=0.12, cor=TINTA2, estilo="-|>", ls="-", fs=7.8, ha="center"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=estilo, mutation_scale=13, color=cor, lw=1.3, ls=ls,
                                 shrinkA=2, shrinkB=2))
    if rotulo:
        ax.text((p0[0] + p1[0]) / 2 + dx, (p0[1] + p1[1]) / 2 + dy, rotulo, ha=ha, va="bottom",
                fontsize=fs, color=TINTA2, family="monospace")


fig, ax = plt.subplots(figsize=(15, 8.6))
ax.set_xlim(0, 15)
ax.set_ylim(-0.75, 8.2)
ax.axis("off")

# faixas das camadas
for x0, x1, camada, nome in [(0.15, 3.85, "percepcao", "1. Percepção (na sala)"),
                             (4.15, 6.65, "rede", "2. Rede"),
                             (6.95, 10.75, "processamento", "3. Processamento (servidor da escola)"),
                             (11.05, 14.85, "aplicacao", "4. Aplicação (professor)")]:
    ax.text((x0 + x1) / 2, 7.95, nome, ha="center", va="top", fontsize=11.5, fontweight="bold",
            color=CAMADA[camada][0])
    ax.plot([x0, x1], [7.55, 7.55], color=CAMADA[camada][0], lw=2.5, solid_capstyle="round")

# 1. percepção
caixa(ax, 0.3, 4.0, 3.4, 3.3, "percepcao", "Pulseira proposta (ESP32)",
      ["MAX30102: pulso óptico (PPG)", "Grove GSR: atividade eletrodérmica",
       "MAX30205: temperatura da pele", "MPU6050: acelerômetro",
       "ESP32: amostra, empacota e", "publica 1 pacote/s via Wi-Fi", "bateria LiPo + TP4056"])
caixa(ax, 0.3, 1.5, 3.4, 2.1, "percepcao", "Pulseira virtual (demo)",
      ["src/iot/virtual_wristband.py", "reproduz os sinais de pulso", "do WESAD (Empatica E4),",
       "no mesmo formato da real"], tracejada=True)
ax.text(2.0, 3.8, "substitui na demonstração", ha="center", va="center", fontsize=8, color=TINTA2,
        style="italic")

# 2. rede
caixa(ax, 4.3, 3.2, 2.2, 2.6, "rede", "Broker MQTT",
      ["Mosquitto", "(Docker, rede local)", "", "produção:", "TLS + usuário/senha"])

# 3. processamento
caixa(ax, 7.1, 1.5, 3.5, 5.8, "processamento", "Serviço de inferência",
      ["src/iot/inference_service.py", "",
       "1. buffer de 60 s por aluno", "2. calibração: 5 min de repouso",
       "    (média de base da pessoa)", "3. 18 indicadores: FC, EDA,",
       "    temperatura, movimento", "4. qualidade do sinal (ruído)",
       "5. Random Forest → P(estresse)", "    a cada 30 s",
       "6. regra: 2 janelas seguidas", "    ≥ 0,5 → alerta", "",
       "models/modelo_estresse.joblib"])

# 4. aplicação
caixa(ax, 11.2, 4.6, 3.5, 2.7, "aplicacao", "Painel do professor",
      ["Streamlit (dashboard/app.py)", "nível de agitação por aluno",
       "sinais recentes e histórico", "horários de maior estresse"])
caixa(ax, 11.2, 1.5, 3.5, 2.6, "aplicacao", "Alerta no celular",
      ["src/iot/telegram_alert.py", "bot do Telegram:", "\"Aluno 03: agitação alta.",
       "Sugestão: pausa sensorial.\""])

# setas: pulseiras -> broker -> IA -> broker
seta(ax, (3.7, 5.6), (4.3, 5.0), "sinais", dx=-0.2, dy=0.35, ha="left")
seta(ax, (3.7, 2.6), (4.3, 3.5), ls="--")
seta(ax, (6.5, 5.0), (7.1, 5.0), "sinais", dy=0.08)
seta(ax, (7.1, 4.0), (6.5, 4.0), "agitação\nalertas", dy=-0.62)

# barramento de assinatura: broker -> painel e Telegram (passa por baixo do serviço de IA)
yb, xb = 1.05, 10.9
ax.plot([5.4, 5.4, xb, xb], [3.2, yb, yb, 5.95], color=TINTA2, lw=1.3, solid_joinstyle="round")
seta(ax, (xb, 5.95), (11.2, 5.95))
seta(ax, (xb, 2.8), (11.2, 2.8))
ax.text(8.85, yb + 0.08, "painel e Telegram assinam agitação e alertas", ha="center", va="bottom",
        fontsize=7.8, color=TINTA2, family="monospace")

# tópicos MQTT (legenda em faixa)
ax.text(0.3, 0.45, "Tópicos MQTT:", fontsize=9, fontweight="bold", color=TINTA, va="center")
for x, t, d in [(2.0, "escola/sala1/aluno/<id>/sinais", "pulseira → IA, 1 pacote/s"),
                (6.4, "escola/sala1/aluno/<id>/agitacao", "IA → painel, a cada 30 s"),
                (10.9, "escola/sala1/alertas", "IA → painel e Telegram")]:
    ax.text(x, 0.55, t, fontsize=8, family="monospace", color=TINTA, va="center")
    ax.text(x, 0.22, d, fontsize=7.8, color=TINTA2, va="center")
ax.text(7.5, -0.4, "Dados identificados só por pseudônimo (ex.: aluno03); "
        "os sinais brutos ficam só em memória (últimos 60 s).",
        ha="center", fontsize=8.5, color=TINTA2, style="italic")

fig.savefig(SAIDA, dpi=170, bbox_inches="tight", facecolor="white")
print(f"salvo em {SAIDA}")
