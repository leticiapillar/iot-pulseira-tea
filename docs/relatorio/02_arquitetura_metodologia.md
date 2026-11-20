> **Rascunho gerado com apoio de IA em 17/11/2026.**
> - Os números da metodologia vêm de `src/data/preprocess.py`, `src/models/train.py` e `data/processed/features_wesad.csv`.
> - O formato das mensagens MQTT (2.3) é o **contrato da demonstração** do dia 13: se ele mudar na implementação, atualizar aqui.
> - **Reescrever com suas palavras e apagar este aviso.**

# 2 Arquitetura e Metodologia

Esta seção descreve a arquitetura IoT proposta para a pulseira (2.1 a 2.4) e a metodologia usada para desenvolver e avaliar o modelo de detecção de estresse (2.5 a 2.9). A seção 2.10 registra as mudanças de planejamento ao longo do trabalho.

## 2.1 Visão geral

A solução segue as quatro camadas clássicas de uma arquitetura IoT (Figura 2.1):

1. **Percepção:** uma pulseira com sensores fisiológicos, usada pelo aluno, amostra os sinais e os envia pela rede Wi-Fi da escola.
2. **Rede:** um broker MQTT recebe as mensagens das pulseiras e as distribui para quem as assina.
3. **Processamento:** um serviço de inferência, em um servidor da escola, monta janelas de sinais, calcula indicadores fisiológicos e estima a probabilidade de estresse com o modelo treinado.
4. **Aplicação:** o professor recebe um alerta no celular (Telegram) e acompanha um painel com o nível de agitação de cada aluno.

**Figura 2.1:** Arquitetura da solução (`docs/arquitetura/arquitetura.png`, gerada por `docs/arquitetura/gerar_diagrama.py`).

Este trabalho é uma **prova de conceito com sensores virtualizados**. Na demonstração, a pulseira física é substituída por uma **pulseira virtual**, que reproduz os sinais de pulso do dataset WESAD no mesmo formato de mensagem que a pulseira real usaria. As camadas de rede, processamento e aplicação são as mesmas nos dois casos. Assim, trocar a pulseira virtual pela física não exige mudanças no restante do sistema.

## 2.2 Camada de percepção: a pulseira

### 2.2.1 Pulseira proposta

O hardware proposto usa componentes de baixo custo, os mesmos ou equivalentes aos dos protótipos de Monteiro (2022) e do AutiSense (SHAHEEN; DARABEE, 2026):

| Componente | Função | Interface | Sinal no modelo |
|---|---|---|---|
| ESP32 | Microcontrolador com Wi-Fi: amostra os sensores e publica no broker | — | — |
| MAX30102 | Pulso óptico (fotopletismografia, PPG) | I²C | Frequência cardíaca |
| Módulo GSR (Grove) | Condutância da pele (atividade eletrodérmica, EDA) | ADC | EDA |
| MAX30205 | Temperatura da pele | I²C | Temperatura |
| MPU6050 | Acelerômetro de 3 eixos | I²C | Movimento |
| Bateria LiPo 3,7 V + TP4056 | Alimentação e recarga | — | — |

O firmware de referência está em `firmware/`. A pulseira não processa os sinais: ela amostra os sensores e publica **um pacote por segundo** com as amostras brutas. As taxas de amostragem são as mesmas da Empatica E4, a pulseira usada no WESAD (SCHMIDT et al., 2018): pulso a 64 Hz, EDA e temperatura a 4 Hz, acelerômetro a 32 Hz. Isso garante que o servidor calcule exatamente os mesmos indicadores usados no treino do modelo.

Uma alternativa seria calcular os indicadores na própria pulseira (*edge computing*) e enviar só 18 números a cada 30 s. Essa opção economiza rede e bateria e melhora a privacidade, mas exige reimplementar em C o processamento de sinais, hoje feito com bibliotecas Python. Fica como evolução do projeto.

**Cuidados de hardware conhecidos na literatura:**
- **Pulso óptico no pulso é instável com movimento.** Monteiro (2022) descartou dois sensores ópticos por instabilidade. A pulseira da Febrace também teve problemas, e o AutiSense posicionou o MAX30102 no dedo (TERTO; SILVA; SANTOS, 2023; SHAHEEN; DARABEE, 2026). Por isso o serviço de inferência mede a qualidade do sinal em cada janela (2.6) e não decide quando o sinal está ruim.
- **O módulo GSR precisa de conversão para microsiemens (µS).** O valor do ADC tem de ser convertido com a curva do módulo, e os eletrodos precisam de bom contato com a pele.
- **A aceitação da pulseira não é garantida.** No estudo de Imbiriba et al. (2023), 8 de 86 jovens com TEA não toleraram a pulseira. O dispositivo precisa ser leve e confortável, e é recomendável um período de adaptação.

### 2.2.2 Pulseira virtual (demonstração)

A pulseira virtual (`src/iot/virtual_wristband.py`) lê os sinais de pulso de um participante do WESAD e os publica em pacotes de 1 s, como a pulseira real faria. A reprodução pode ser acelerada (por exemplo, 10 vezes), para a demonstração caber em poucos minutos. Cada participante do WESAD é apresentado como um aluno, identificado por um pseudônimo (`aluno01`, `aluno02`...).

## 2.3 Camada de rede: MQTT

A comunicação usa o protocolo **MQTT**, padrão em IoT por ser leve e pelo modelo publicação/assinatura (*publish/subscribe*). Nesse modelo, a pulseira não precisa saber quem vai usar os dados: ela publica em um **tópico**, e cada serviço assina os tópicos de que precisa. O broker usado é o **Mosquitto**, executado em Docker (`docker-compose.yml`).

**Tabela 2.1:** Tópicos MQTT

| Tópico | Quem publica | Quem assina | Frequência | QoS |
|---|---|---|---|---|
| `escola/sala1/aluno/<id>/sinais` | pulseira | serviço de inferência (e o painel, só na aba de conferência da pulseira) | 1 por segundo | 0 |
| `escola/sala1/aluno/<id>/agitacao` | serviço de inferência | painel | 1 a cada 30 s (mensagem retida) | 0 |
| `escola/sala1/alertas` | serviço de inferência | painel e bot do Telegram | por evento | 1 |

Os níveis de QoS (qualidade de serviço do MQTT) foram escolhidos assim:
- **Sinais:** usam QoS 0 (sem confirmação de entrega). A perda ocasional de um pacote de 1 s é tolerada, porque a janela é marcada como inválida se faltarem dados.
- **Alertas:** usam QoS 1 (entrega garantida pelo menos uma vez), porque um alerta perdido é a falha mais grave do sistema.
- **Agitação:** a última mensagem fica **retida** no broker, para que o painel, ao ser aberto, mostre o estado atual sem esperar a próxima janela.

**Mensagem de sinais** (pulseira → serviço; unidades: EDA em µS, temperatura em °C, aceleração em g, pulso em unidade arbitrária):

```json
{"aluno": "aluno03", "seq": 1234, "t": 1731100000.0,
 "bvp": [64 valores], "eda": [4 valores], "temp": [4 valores],
 "acc": [[x, y, z], ... 32 amostras]}
```

Na pulseira virtual, as mensagens trazem também o campo `rotulo`, com a condição do protocolo do WESAD, para o painel mostrar a "verdade" durante a demonstração. O serviço de inferência não usa esse campo.

Cada pacote tem cerca de 1,4 KB. Uma sala com 30 alunos gera cerca de 45 KB/s, uma carga pequena para uma rede Wi-Fi.

**Mensagem de agitação** (serviço → painel):

```json
{"aluno": "aluno03", "t": 1731100030.0, "sessao": 1731099700.0, "estado": "monitorando",
 "prob": 0.83, "nivel": "alto", "janela_valida": true, "fc": 96, "eda": 1.42, "temp": 33.1}
```

- **`sessao`:** horário em que a pulseira começou a sessão (e a calibração). Separa as sessões no histórico.
- **`fc`, `eda`, `temp`:** resumo da janela para o painel (média da frequência cardíaca em bpm, da condutância da pele em µS e da temperatura da pele em °C). São indicadores já calculados, não sinais brutos.
- **`estado`:** `calibrando` (primeiros 5 min), `monitorando` ou `sinal_ruim`.
- **`nivel`:** `baixo` (prob. < 0,5), `moderado` (0,5 a 0,8) ou `alto` (≥ 0,8). Serve só para exibição.

**Mensagem de alerta** (serviço → painel e Telegram):

```json
{"aluno": "aluno03", "t": 1731100060.0, "sessao": 1731099700.0, "tipo": "inicio", "prob": 0.91, "nivel": "alto"}
```

- **`tipo`:** `inicio` quando o episódio começa; `fim` quando o aluno volta ao normal.

## 2.4 Camadas de processamento e aplicação

O **serviço de inferência** (`src/iot/inference_service.py`) assina os sinais de todas as pulseiras e, para cada aluno:

1. **mantém um buffer** com os últimos 60 s de sinais;
2. nos **primeiros 5 minutos**, com o aluno em repouso, acumula a **calibração**: a média de cada indicador, que vira o nível de base da pessoa;
3. a cada 30 s, **calcula os 18 indicadores** da janela (2.6), confere a qualidade do sinal e subtrai o nível de base;
4. aplica o **modelo** (`models/modelo_estresse.joblib`) e publica a probabilidade de estresse;
5. aplica a **regra de alerta**:
   - publica um alerta de início quando **duas janelas seguidas** têm probabilidade ≥ 0,5;
   - publica um alerta de fim quando duas janelas seguidas ficam abaixo de 0,5;
   - não publica novos alertas para o mesmo episódio.

Se a pulseira ficar mais de 5 s sem enviar dados (pacotes perdidos, bateria, Wi-Fi), o serviço esvazia o buffer e só volta a decidir depois de 60 s de sinal contínuo, para não misturar trechos diferentes na mesma janela. A calibração é mantida.

A regra de 2 janelas seguidas foi escolhida na simulação de uso (Seção 4.5). Ela custa cerca de 30 s a mais de latência e reduz os alarmes falsos.

O **bot do Telegram** (`src/iot/telegram_alert.py`) assina os alertas e envia ao professor uma mensagem curta, por exemplo: *"⚠️ Aluno 03: sinais de agitação (nível alto) às 10:42. Sugestão: aproximar-se com calma e oferecer uma pausa sensorial."* O **painel** (`dashboard/app.py`, em Streamlit) mostra (detalhes na Seção 3):
- o nível de agitação de cada aluno;
- os sinais recentes;
- o histórico de alertas;
- os horários de maior estresse, que podem ajudar o professor a identificar gatilhos na rotina da turma.

### 2.4.1 Privacidade desde a concepção

Como os sinais fisiológicos são **dados pessoais sensíveis** de crianças e adolescentes (LGPD, arts. 11 e 14), a arquitetura foi desenhada para minimizar o que circula e o que é guardado. A discussão completa está nas Conclusões.

- **Pseudônimos:** as mensagens identificam o aluno só por um pseudônimo (`aluno03`). A correspondência com o nome fica apenas com a escola, fora do sistema.
- **Rede local:** o broker e o serviço de inferência ficam na rede local da escola, e os sinais brutos não saem dela.
- **Sinais brutos não são gravados:** ficam só em memória (os últimos 60 s), tanto no serviço de inferência quanto no painel. O sistema guarda apenas as probabilidades, o resumo de cada janela e os alertas.
- **Mensagem mínima ao Telegram:** a mensagem enviada ao professor, que passa por um serviço externo, contém só o pseudônimo e o nível de agitação.
- **Autenticação e criptografia:** na demonstração o broker aceita conexões sem autenticação. Em produção, deve exigir usuário e senha e usar TLS.

## 2.5 Dados

O modelo foi desenvolvido com o **WESAD** (SCHMIDT et al., 2018), um dataset público de detecção de estresse com 15 adultos (idade média de 27,5 anos). Os participantes usaram uma Empatica E4 no pulso e uma cinta no peito durante um protocolo de laboratório com quatro condições:
- **repouso** (cerca de 20 min);
- **diversão** (vídeos engraçados);
- **estresse:** o *Trier Social Stress Test* (TSST), com discurso e aritmética diante de uma banca;
- **meditação** guiada.

Foram usados **apenas os sinais do pulso** (pulso óptico, EDA, temperatura e acelerômetro), que são os que uma pulseira escolar teria. A tarefa é **binária**, como em Schmidt et al. (2018):
- **estresse:** o TSST;
- **não estresse:** o repouso e a diversão.

A meditação ficou fora do treino e foi usada apenas na simulação de uso.

## 2.6 Pré-processamento e indicadores

O pré-processamento (`src/data/preprocess.py`) divide a sessão de cada participante em **janelas de 60 s com passo de 30 s**, usando só janelas inteiramente dentro de uma condição. Uma versão com janelas de 120 s foi usada como verificação. Para cada janela são calculados 18 indicadores, agrupados pelo sensor necessário para medi-los:

| Sensor | Indicadores | Processamento |
|---|---|---|
| Pulso óptico | FC média, mediana, desvio padrão, mínima e máxima | Detecção dos batimentos no sinal de pulso (neurokit2) |
| Temperatura | Média, desvio padrão e inclinação | — |
| Acelerômetro | Média, desvio padrão e percentil 95 da magnitude | — |
| GSR (EDA) | Média, desvio padrão e inclinação da EDA; nível tônico (SCL); respostas fásicas (SCR) por minuto e amplitude média; desvio padrão da componente fásica | Filtro passa-baixa de 1 Hz; separação tônica/fásica; picos com proeminência ≥ 0,01 µS |

**Qualidade do sinal.** Batimentos que implicam FC fora de 40 a 180 bpm são tratados como ruído. A janela é descartada se mais de 20% dos batimentos forem ruído ou se houver menos de 30 batimentos válidos. Foram descartadas 123 de 1.349 janelas (9%). O descarte foi desigual entre condições: 1,8% no repouso, 9,3% no estresse, 16,8% na meditação e 18,6% na diversão. Isso reflete o efeito do movimento sobre o pulso óptico.

**Variabilidade da frequência cardíaca (HRV).** A HRV é um indicador clássico de estresse, mas foi **excluída**. No estresse, os valores calculados a partir do pulso foram implausíveis: maiores que no repouso, o oposto do esperado pela fisiologia. Isso indica ruído de movimento, já que no TSST a pessoa fala e gesticula. A própria Empatica E4 só conseguiu medir os intervalos entre batimentos em menos de 10% do tempo de estresse.

## 2.7 Conjuntos de sensores e calibração

O experimento central compara três conjuntos de indicadores, que correspondem a três versões de hardware:

| Conjunto | Sensores | Indicadores |
|---|---|---|
| Só FC | pulso óptico | 5 |
| Baixo custo | pulso óptico, temperatura e acelerômetro | 11 |
| Baixo custo + EDA | os anteriores e o GSR (equivale a todos os sensores de pulso da E4) | 18 |

Os conjuntos usam subconjuntos dos sinais da própria E4. Portanto, o "baixo custo" é **simulado**: sensores baratos reais tendem a ser mais ruidosos, e os resultados representam um teto para esse hardware.

**Calibração por pessoa.** Os sinais fisiológicos variam muito de uma pessoa para outra. Por isso, cada indicador é transformado na **diferença em relação à média dos primeiros 5 minutos de repouso da própria pessoa**. Na escola, isso corresponde a uma calibração em repouso no início do dia. Esses 5 minutos servem só para a calibração e **ficam fora da avaliação**. Caso contrário, as janelas de repouso seriam comparadas com a própria média e pareceriam artificialmente fáceis.

A calibração usa apenas dados da própria pessoa, sem vazamento de informação entre participantes. Também foi avaliada a versão sem calibração (valores brutos), para medir o efeito da calibração. Após descartar as janelas ruidosas e as de calibração, restaram **800 janelas** para avaliação, sendo 34% de estresse.

## 2.8 Modelos, validação e métricas

Foram treinados quatro modelos de classificação com scikit-learn e XGBoost (`src/models/train.py`):

- **regressão logística**, usada por Goodwin et al. (2019) e Imbiriba et al. (2023);
- **análise discriminante linear (LDA)**, melhor modelo de Siirtola (2019);
- **Random Forest**, melhor modelo de Schmidt et al. (2018) no pulso;
- **XGBoost**.

Um classificador que sempre responde a classe mais frequente serve de referência mínima. As classes desbalanceadas foram compensadas com pesos.

**Validação.** Todos os modelos foram avaliados com **validação deixando um participante de fora** (*leave-one-subject-out*, LOSO):
- o modelo é treinado com 14 participantes e testado no 15º;
- o processo é repetido para cada participante.

Esse esquema simula o uso da pulseira em um aluno novo, que o modelo nunca viu. Pelo mesmo motivo, o modelo usado na demonstração foi treinado **sem** os três participantes que a demonstração reproduz como alunos (S8, S10 e S15). É mais rigoroso que a validação cruzada comum, em que janelas da mesma pessoa podem estar no treino e no teste.

**Métricas.** No WESAD, um classificador que sempre responde "não estresse" acerta cerca de 66% das janelas, e por isso a acurácia sozinha engana. As métricas principais são:
- **F1 macro:** média do F1 das duas classes;
- **acurácia balanceada;**
- **AUROC:** área sob a curva ROC, que avalia o modelo em todos os limiares de decisão.

As métricas são calculadas juntando as previsões de todos os participantes e também por participante, para mostrar a variação entre pessoas.

**Análises complementares** (`notebooks/02_experimento_central.ipynb`):
- **Importância por permutação dentro do LOSO:** quanto o AUROC cai quando os indicadores de um sensor são embaralhados.
- **Simulação de uso:** cada sessão é reproduzida janela a janela, incluindo a meditação, para medir:
  - a demora até o alerta;
  - a fração do estresse com alerta;
  - a taxa de alarmes falsos.

**Modelo final.** O modelo da demonstração é a **Random Forest com o conjunto baixo custo + EDA, calibrado**, que teve o melhor desempenho (Seção 4). Ele foi treinado com os 15 participantes.

## 2.9 Ferramentas

| Finalidade | Ferramenta |
|---|---|
| Linguagem | Python 3 |
| Processamento de sinais | NumPy, SciPy, pandas, neurokit2 |
| Aprendizado de máquina | scikit-learn, XGBoost, joblib |
| Análise e figuras | Jupyter, Matplotlib |
| Comunicação IoT | Mosquitto (Docker), paho-mqtt |
| Alertas e painel | python-telegram-bot, Streamlit |
| Firmware proposto | Arduino (ESP32) |

Todo o código, as métricas e as figuras estão no repositório do projeto, com instruções para reproduzir os resultados.

## 2.10 Mudanças de planejamento

O planejamento inicial previa avaliar o modelo em um dataset público de **crianças com TEA** (IEEE DataPort), com frequência cardíaca de pulseira registrada durante comportamentos desafiadores. O acesso não foi liberado a tempo, e o trabalho passou por duas mudanças:

- **Plano B:** validação externa em um segundo dataset público (*wearable-and-stress*, no Hugging Face). O modelo seria treinado no WESAD com os sinais em comum (frequência cardíaca, temperatura e movimento) e testado em dados de enfermeiras em ambiente hospitalar.
- **Plano C (adotado):** a verificação desse segundo dataset, feita antes do uso, mostrou rótulos de estresse não confiáveis (detalhes na Seção 4.7). O experimento central passou a ser a **comparação de conjuntos de sensores** no WESAD. Ela responde a uma pergunta diretamente ligada à lacuna do trabalho: quanto se perde ao trocar a pulseira de pesquisa por sensores de baixo custo?

Com isso, a aplicação ao público com TEA permanece uma **hipótese**, apoiada pelos estudos que usaram a mesma pulseira em jovens com TEA (GOODWIN et al., 2019; IMBIRIBA et al., 2023). A validação com esse público é o principal trabalho futuro e depende de aprovação ética.

---

## Referências citadas nesta seção

BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). *Diário Oficial da União*, Brasília, DF, 15 ago. 2018.

GOODWIN, M. S. et al. Predicting aggression to others in youth with autism using a wearable biosensor. *Autism Research*, v. 12, n. 8, p. 1286-1296, 2019. DOI: 10.1002/aur.2151.

IMBIRIBA, T. et al. Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism. *JAMA Network Open*, v. 6, n. 12, e2348898, 2023. DOI: 10.1001/jamanetworkopen.2023.48898.

MONTEIRO, K. R. *Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos*. 2022. 105 f. Dissertação (Mestrado em Engenharia Biomédica) – Faculdade UnB Gama, Universidade de Brasília, Brasília, 2022.

SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: INTERNATIONAL CONFERENCE ON MULTIMODAL INTERACTION, 20., 2018, Boulder. *Proceedings* [...]. New York: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.

SHAHEEN, B.; DARABEE, R. *AutiSense*: smart assistant system for children with autism spectrum disorder. 2026. Trabalho de Conclusão de Curso (Bacharelado em Engenharia de Sistemas Computacionais) – Palestine Polytechnic University, Hebron, 2026.

SIIRTOLA, P. Continuous stress detection using the sensors of commercial smartwatch. In: ACM INTERNATIONAL JOINT CONFERENCE ON PERVASIVE AND UBIQUITOUS COMPUTING; INTERNATIONAL SYMPOSIUM ON WEARABLE COMPUTERS, 2019, London. *Adjunct Proceedings* [...]. New York: ACM, 2019. DOI: 10.1145/3341162.3344831.

TERTO, D. C. V.; SILVA, L. S.; SANTOS, A. *Pulseira indicadora de desregulação em autistas*. Pôster apresentado na Feira Brasileira de Ciências e Engenharia (FEBRACE), São Paulo, 2023.
