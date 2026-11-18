# Pulseira Inteligente para Alunos com TEA

> Monitoramento de sinais fisiológicos de estresse e agitação em alunos com Transtorno do Espectro Autista (TEA), com alertas ao professor antes do pico da crise, usando IoT e Inteligência Artificial.

Trabalho final da disciplina **Internet das Coisas e Aplicações de IA (Big Data)**.

🎥 **Vídeo pitch & demo:** _[link a adicionar]_
📄 **Relatório técnico:** [docs/relatorio/relatorio.pdf](docs/relatorio/relatorio.pdf)

---

## 1. Problema

_[Resumo do problema: crises de desregulação em alunos com TEA no ambiente escolar, dificuldade de o professor perceber os sinais com antecedência e impacto na inclusão.]_

## 2. Solução

_[Resumo da solução: uma pulseira com sensores de frequência cardíaca, atividade eletrodérmica e movimento envia dados via MQTT para um modelo de IA que detecta sinais de estresse e alerta o professor por Telegram e por um dashboard.]_

Este projeto é uma **prova de conceito com sensores virtualizados**: a pulseira é simulada a partir de datasets públicos de referência (WESAD e dataset de crianças com TEA do IEEE DataPort).

## 3. Arquitetura

![Arquitetura](docs/arquitetura/arquitetura.png)

```
[Pulseira virtual] --MQTT--> [Broker Mosquitto] --> [Serviço de IA] --> [Alerta Telegram]
                                                           |
                                                           v
                                                  [Dashboard Streamlit]
```

## 4. Principais resultados

| Modelo | Dataset de teste | Acurácia | F1 | AUROC |
|---|---|---|---|---|
| _a preencher_ | WESAD (validação deixando uma pessoa de fora) | | | |
| _a preencher_ | TEA (IEEE DataPort) | | | |

## 5. Estrutura do repositório

```
├── data/          # datasets (brutos não versionados; veja data/README.md)
├── docs/          # cronograma, referências, arquitetura e relatório
├── notebooks/     # exploração, modelagem e análise de resultados
├── src/
│   ├── data/      # download e pré-processamento
│   ├── models/    # treino e predição
│   └── iot/       # pulseira virtual, serviço de inferência e alertas
├── dashboard/     # aplicação Streamlit
├── firmware/      # código proposto para a pulseira ESP32 (opcional)
├── models/        # modelo treinado
└── results/       # figuras e métricas
```

## 6. Instalação

Pré-requisitos: Python 3.11+ e Docker (para o broker MQTT).

```bash
git clone <url-do-repositorio>
cd iot-pulseira-tea
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # e preencha as variáveis
```

## 7. Dados

Veja as instruções completas em [data/README.md](data/README.md).

```bash
python -m src.data.download
python -m src.data.preprocess
```

## 8. Como executar a demo

Pré-requisito: o WESAD em `data/raw/WESAD/` (veja [data/README.md](data/README.md)). Cada comando roda em um terminal.

```bash
# 1. Subir o broker MQTT
docker compose up -d mosquitto

# 2. Serviço de inferência (assina os sinais, calcula a probabilidade de estresse e publica alertas)
python -m src.iot.inference_service

# 3. Alertas no Telegram (sem token no .env, mostra no terminal a mensagem que enviaria)
python -m src.iot.telegram_alert

# 4. Pulseiras virtuais (reproduzem participantes do WESAD como alunos)
python -m src.iot.virtual_wristband --aluno aluno01 --velocidade 10           # sessão completa (~10 min)
python -m src.iot.virtual_wristband --aluno aluno02 --velocidade 20 --curta   # calibração + estresse (~1,5 min)

# 5. Painel do professor (dia 14)
streamlit run dashboard/app.py
```

**Modelo da demo.** O serviço usa `models/modelo_demo_sem_S8_S10_S15.joblib`, treinado **sem** os três participantes que a demo reproduz (aluno01 = S10, aluno02 = S15, aluno03 = S8). Assim, a demo mostra a pulseira em pessoas que o modelo nunca viu. Para recriá-lo: `python -m src.models.train --salvar rf baixo_custo_eda --excluir S8 S10 S15`.

**Calibração.** Os primeiros 5 minutos de cada pulseira são de repouso e servem de calibração: só depois deles o serviço começa a estimar o estresse.

**Telegram.** Crie um bot com o @BotFather, coloque o token em `TELEGRAM_BOT_TOKEN` no `.env`, mande uma mensagem ao bot e rode `python -m src.iot.telegram_alert --descobrir-chat` para obter o `TELEGRAM_CHAT_ID`. Teste com `python -m src.iot.telegram_alert --teste`.

**Verificação sem MQTT.** `python -m src.models.predict S10 models/modelo_demo_sem_S8_S10_S15.joblib` compara os indicadores calculados em tempo real com os do treino.

## 9. Limitações e ética

- Não houve testes com usuários reais, pois isso exigiria aprovação de Comitê de Ética em Pesquisa (CEP).
- O dataset de crianças com TEA é pequeno (5 participantes).
- A solução é uma ferramenta de **apoio** ao professor e ao cuidador, **não** um dispositivo de diagnóstico.
- Dados de saúde de menores são sensíveis (LGPD, art. 11 e art. 14): a proposta prevê anonimização e consentimento dos responsáveis.

## 10. Referências

Veja [docs/referencias/fichamentos.md](docs/referencias/fichamentos.md).

## Licença

Código sob licença MIT (veja [LICENSE](LICENSE)). Os datasets seguem as licenças de seus autores originais.
