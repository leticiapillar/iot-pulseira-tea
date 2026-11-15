# Fichamentos e trabalhos relacionados

> **Status:** rascunho preenchido com apoio de IA a partir dos PDFs em `docs/referencias/artigos/` (não versionados).
> Os números de página (**p.**) referem-se à **página do arquivo PDF**, não à numeração impressa. Conferir os números principais antes de usá-los no relatório.
> O campo "O que uso no meu trabalho" é uma **sugestão**: reescrever com suas palavras.

## Tabela comparativa

| Trabalho | Ano | Público | Sensores / sinais | Modelo de IA | Validação | Resultado principal | Link |
|---|---|---|---|---|---|---|---|
| Goodwin et al. (Autism Research) | 2019 | 20 jovens com TEA, 6–17 anos, internação psiquiátrica | Empatica E4: BVP/IBI, EDA, ACC | Regressão logística com regularização ridge | 5-fold CV repetida 5× (não deixa o sujeito de fora) | AUC 0,71 (modelo global) e 0,84 (modelos por pessoa), prevendo agressão **1 min antes** com 3 min de dados | https://zendy.io/title/10.1002/aur.2151 |
| Imbiriba et al. (JAMA Netw. Open) | 2023 | 70 jovens com TEA analisados (86 inscritos), 5–19 anos, 4 hospitais | Empatica E4: BVP, EDA, ACC | Regressão logística, SVM, rede neural, adaptação de domínio | Divisão por sessão (80/20) e CV deixando indivíduos de fora | Regressão logística: AUROC 0,80 **3 min antes** (divisão por sessão); 0,77 deixando indivíduos de fora | https://pesquisa.bvsalud.org/sms/resource/pt/mdl-38127348 |
| Schmidt et al. (WESAD, ICMI) | 2018 | 15 adultos saudáveis (laboratório, TSST) | E4 no pulso: BVP, EDA, TEMP, ACC; RespiBAN no peito | DT, RF, AdaBoost, LDA, kNN | **LOSO** | Binário, só pulso (fisiológicos): **acurácia 88,3% / F1 86,1%** (RF). Melhor geral: 93,1% (peito, LDA) | https://www.eti.uni-siegen.de/ubicomp/papers/ubi_icmi2018.pdf |
| Siirtola (UbiComp/ISWC Adjunct) | 2019 | WESAD (15 adultos), só E4 do pulso | ACC, EDA, TEMP, BVP, HR | LDA, QDA, RF | **LOSO** | **Acurácia balanceada 87,4%** com TEMP+BVP+HR, sem EDA (LDA, janela de 120 s) | https://urn.fi/URN:NBN:fi-fe2019121648252 |
| Monteiro (Dissertação UnB) | 2022 | 10 adultos saudáveis (simulação) + 1 adolescente autista | Luva + pulseira: GSR (Grove), ECG (AD8232), termistor, MPU6050; **Arduino Nano**, nRF24L01+, Raspberry Pi 3 | Índice de *meltdown* por limiares ponderados (sem aprendizado de máquina) | Teste funcional (crise simulada e *Cold Pressor Test*) | 90% (simulação) e 100% (CPT) de detecção; nenhuma crise real observada | https://repositorio.unb.br/bitstream/10482/44757/1/2022_KlausRibeiroMonteiro.pdf |
| AutiSense (TCC PPU) | 2025–26 | Crianças com TEA (público-alvo); testes em cenários controlados | **ESP32-C3**, MAX30102 (dedo), Grove GSR, MPU6050 | Limiares relativos à linha de base pessoal + classificação de movimento (repouso, atividade, *stimming*) | Testes de unidade e integração com cenários roteirizados | Classificou corretamente os 5 cenários; alerta via Telegram | https://scholar.ppu.edu/handle/123456789/9458 |
| Pulseira Febrace (ETE Henrique Lage) | 2023 | Autistas (público-alvo); sem teste com usuários | Sensor de batimento (dedo), DHT11 (umidade como suor), módulo transceptor | Limiar fixo (BPM > 100; umidade > 80%) | Testes de bancada | Sensores de batimento **instáveis com movimento** e ruins no pulso; alcance de 50 m | https://virtual.febrace.org.br/2023/ENG/2017/poster |
| Gernert et al. (STREAM, PLoS ONE) | 2024 | 20 adultos com TEA + 20 controles (planejado) | Pulseira: HR, HRV, EDA; faixa de EEG para sono | **Não se aplica**: é um protocolo de estudo, sem resultados | — | Define os indicadores de HR, HRV e EDA e o manejo de dados (GDPR) | https://doaj.org/article/5b48ae0d92704c078729119a53a97657 |

> ⚠️ **Correções em relação à versão anterior da tabela:**
> - O trabalho da PLoS ONE **não é uma revisão**. É o *protocolo* do estudo STREAM, ainda sem resultados. Se você precisar de uma revisão de verdade sobre wearables e estresse em TEA, é preciso buscar outra.
> - Só o AutiSense usa **ESP32**. A UnB usa Arduino Nano e a Febrace não nomeia o microcontrolador no pôster.
> - Imbiriba: os 0,80 de AUROC vêm da divisão por sessão. Na validação que deixa indivíduos de fora, a mais comparável à sua, o valor é 0,77.

---

## Números de referência para o seu experimento (WESAD, só pulso, LOSO)

Use estes valores na **Análise de Resultados** (dia 11). Eles estão nas mesmas condições do seu projeto: só a pulseira E4, validação deixando um sujeito de fora e estresse vs. não estresse.

| Fonte | Sinais | Modelo | Métrica | Valor | Onde |
|---|---|---|---|---|---|
| Schmidt 2018 | BVP+EDA+TEMP (pulso) | RF | Acurácia / F1 macro | 88,33% / 86,10% | p. 7, Tab. 4 |
| Schmidt 2018 | BVP+EDA+TEMP (pulso) | AdaBoost | Acurácia / F1 macro | 88,05% / 85,86% | p. 7, Tab. 4 |
| Schmidt 2018 | BVP+EDA+TEMP (pulso) | LDA | Acurácia / F1 macro | 86,46% / 83,77% | p. 7, Tab. 4 |
| Schmidt 2018 | Só BVP (pulso) | RF | Acurácia | 84,18% | p. 7, Tab. 4 |
| Schmidt 2018 | Só EDA (pulso) | AdaBoost | Acurácia | 79,71% | p. 7, Tab. 4 |
| Schmidt 2018 | Só ACC (pulso) | — | Acurácia | ~70–72% | p. 7, Tab. 4 |
| Siirtola 2019 | TEMP+BVP+HR | LDA | Acurácia balanceada | 87,4% (DP 10,4) | p. 3, Tab. 3 |
| Siirtola 2019 | Todos (ACC+EDA+TEMP+BVP+HR) | LDA / RF | Acurácia balanceada | 83,4% / 80,5% | p. 3, Tab. 3 |
| Siirtola 2019 | Por sujeito (melhor modelo) | LDA | Acurácia | 62,6% (S15) a 98,8% (S13) | p. 4, Tab. 4 |
| Referências de chance (Schmidt) | — | Sempre a classe majoritária | Acurácia / F1 | 69,94% / 41,15% | p. 7, Tab. 4 |

**Cuidado ao comparar:** Schmidt reporta acurácia e F1 macro, enquanto Siirtola reporta acurácia balanceada. Reporte as três no seu trabalho para comparar de forma justa. Também mostre a referência de chance (~70% de acurácia sempre chutando "não estresse"), para evidenciar que acurácia sozinha engana no WESAD.

## Parâmetros sugeridos para o pré-processamento (dia 7)

Extraídos da literatura acima, para justificar as escolhas do `src/data/preprocess.py`:

| Decisão | Valor sugerido | Justificativa |
|---|---|---|
| Rótulos | Estresse (2) vs. não estresse (baseline 1 + diversão 3) | Schmidt p. 6; Siirtola p. 2 |
| Janela dos sinais fisiológicos | **60 s** (testar também 120 s) | Schmidt usa 60 s (p. 4); Siirtola mostra ganho com 120 s (p. 3, Tab. 2: 81,7% → 84,0%) |
| Janela do ACC | 5 s | Schmidt p. 4 |
| Passo da janela | 0,25 s nos artigos; **sugiro 5 a 15 s** para gerar menos janelas quase idênticas | Schmidt p. 4; Goodwin/Imbiriba decidem a cada 15 s (Goodwin p. 6) |
| Filtro EDA | Passa-baixa 5 Hz; separar o componente tônico (SCL) do fásico (SCR) e contar picos de SCR | Schmidt p. 4 |
| Features de BVP | HR médio e DP, HRV (RMSSD, pNN50, LF, HF, LF/HF) | Schmidt p. 4–5, Tab. 1; Gernert p. 6, Tab. 3 |
| Features de TEMP | Média, DP, mín., máx., inclinação | Schmidt p. 5 |
| Taxas de amostragem do E4 | BVP 64 Hz, EDA 4 Hz, TEMP 4 Hz, ACC 32 Hz | Schmidt p. 3 |
| Validação | LOSO (15 rodadas) | Schmidt p. 5; Siirtola p. 2 |

---

## Fichamentos

### 1. Goodwin et al. (2019): Predicting aggression to others in youth with autism using a wearable biosensor

- **Referência (ABNT):** GOODWIN, M. S. et al. Predicting aggression to others in youth with autism using a wearable biosensor. *Autism Research*, v. 12, n. 8, p. 1286-1296, 2019. DOI: 10.1002/aur.2151.
- **Objetivo:** verificar se sinais fisiológicos e de movimento de uma pulseira permitem prever agressão a outras pessoas antes que ela ocorra (p. 1, p. 3).
- **Participantes:** 20 jovens com TEA, 6–17 anos (média 10,8), 75% meninos, 85% minimamente verbais, internados em unidade psiquiátrica especializada. Foram 69 sessões de observação naturalística, somando 87 h e 548 episódios de agressão com duração média de 28 s (p. 1, p. 4, p. 6).
- **Sensores e sinais:** Empatica E4, com BVP e IBI a 64 Hz, EDA a 4 Hz e ACC de 3 eixos a 32 Hz (p. 4–5).
- **Pré-processamento / janelas:** janelas deslizantes de **15 s** com estatísticas simples (primeiro, último, máx., mín., média, mediana, soma, DP, variância). Usa os **3 min anteriores** (τp = 180 s) para prever o **próximo 1 min** (τf). Também inclui features temporais: flag de agressão observada e tempo desde a última agressão (p. 5–6).
- **Modelo e validação:** regressão logística com regularização ridge, avaliada em 5-fold CV repetida 5 vezes. Compara um modelo global (todos os participantes) com modelos por pessoa (p. 5–6). Não usa LOSO.
- **Resultados:** AUC de **0,71** no modelo global e **0,84** em média nos modelos por pessoa (mín. 0,69, máx. 0,99). Os modelos com sinais fisiológicos e de movimento superaram os que usavam só informação temporal, e nenhum sinal isolado (EDA, BVP, IBI) foi indispensável (p. 6–7, Tab. 3 p. 19). A pulseira foi bem tolerada após dessensibilização (p. 6).
- **Limitações:** possível sobreajuste, frequência e duração de agressões desiguais entre participantes, amostra pequena e homogênea (95% brancos) e ambiente hospitalar (p. 8–9).
- **O que uso no meu trabalho:** é a principal evidência de que estresse fisiológico **antecede** a crise em TEA. Justifica a regressão logística como linha de base. Também mostra que **modelos personalizados** funcionam melhor que um modelo global, o que motiva o experimento "com ajuste" do dia 9. Os autores relatam que familiares e profissionais consideram **60 s de aviso** suficientes para intervir (p. 7), o que justifica o alerta ao professor.

### 2. Imbiriba et al. (2023): Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism

- **Referência (ABNT):** IMBIRIBA, T. et al. Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism. *JAMA Network Open*, v. 6, n. 12, e2348898, 2023. DOI: 10.1001/jamanetworkopen.2023.48898.
- **Objetivo:** replicar e ampliar Goodwin (2019) com mais participantes e mais tipos de comportamento: autolesão, desregulação emocional e agressão a outros (p. 1–2).
- **Participantes:** 86 inscritos e **70 analisados**, de 5–19 anos (média 11,9), 88,6% meninos, em 4 hospitais psiquiátricos. Dos 16 excluídos, **8 não toleraram a pulseira** por sensibilidade tátil ou não adesão (p. 4). Foram 429 sessões, 497 h e 6.665 episódios (p. 1, p. 4).
- **Sensores e sinais:** Empatica E4 no pulso não dominante, com BVP, EDA e ACC (p. 3).
- **Pré-processamento / janelas:** decisão a cada 15 s, usando 1–3 min de dados anteriores para prever 1–3 min à frente. Os vetores aumentados (AFV) incluem informação sobre agressões anteriores (p. 3).
- **Modelo e validação:** regressão logística com regularização ridge, SVM e rede neural, mais adaptação de domínio por pseudo-rotulagem para individualizar o modelo. Três esquemas de divisão: por sessão (primeiros 80% para treino), CV deixando indivíduos de fora e CV deixando sessões de fora (p. 3–4).
- **Resultados:** regressão logística com **AUROC 0,80** prevendo **3 min antes** (divisão por sessão, AFV-onset). Com indivíduos fora: 0,77 (p. 7). A SVM teve o melhor valor isolado (0,87), mas a regressão logística foi a mais consistente e foi escolhida como melhor modelo (p. 7, p. 10). A adaptação de domínio aumentou a AUROC em mediana de **+14,5 pontos** (τp 180 s, τf 60 s, sem labels) (p. 9).
- **Limitações:** demografia e geografia restritas, frequência desigual de comportamentos e apenas ambiente hospitalar. É preciso testar em ambulatório e em contextos mais diversos (p. 10).
- **O que uso no meu trabalho:** reforça a regressão logística (simples e interpretável) como escolha sólida, inclusive contra modelos mais complexos. A adaptação de domínio é uma referência direta para o experimento "com ajuste ao novo público" do dia 9. Os 8 de 86 que não toleraram a pulseira são um **requisito de projeto**: a pulseira precisa ser leve e confortável, e é necessário um protocolo de dessensibilização.

### 3. Schmidt et al. (2018): Introducing WESAD, a multimodal dataset for wearable stress and affect detection

- **Referência (ABNT):** SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: INTERNATIONAL CONFERENCE ON MULTIMODAL INTERACTION, 20., 2018, Boulder. *Proceedings* [...]. New York: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.
- **Objetivo:** publicar um dataset multimodal padrão para detecção de estresse e afeto com wearables, junto com um benchmark (p. 1–2).
- **Participantes:** 15 adultos (17 coletados, 2 descartados por falha de sensor), idade média de 27,5 anos, 12 homens, estudantes de pós-graduação sem transtornos mentais (p. 2–3).
- **Sensores e sinais:** RespiBAN no peito (ECG, EDA, EMG, RESP, TEMP, ACC, a 700 Hz) e **Empatica E4** no pulso não dominante (BVP 64 Hz, EDA 4 Hz, TEMP 4 Hz, ACC 32 Hz) (p. 3).
- **Protocolo:** baseline de 20 min, diversão (vídeos, 392 s), estresse pelo **TSST** (discurso + aritmética, ~10 min) e meditações. O rótulo vem do protocolo, não dos questionários (p. 3–4).
- **Pré-processamento / janelas:** janela deslizante com passo de 0,25 s. **60 s** para sinais fisiológicos e 5 s para ACC. EDA com passa-baixa de 5 Hz e separação SCL/SCR. HR e HRV extraídos de picos do BVP/ECG (p. 4–5, Tab. 1).
- **Modelo e validação:** DT, RF, AdaBoost, LDA e kNN (scikit-learn), avaliados com **LOSO**. Métricas: acurácia e F1 macro (p. 5).
- **Resultados:** 3 classes com até 80,34% (peito, AdaBoost); binário com até 93,12% (peito, LDA). **Só pulso, fisiológicos:** 76% (3 classes) e **88%** no binário (p. 8; Tab. 4 p. 7). Juntar pulso e peito não melhora sobre o peito sozinho. Usar só ACC dá resultado bem pior, o que indica que o modelo não aprende apenas padrões de movimento (p. 6). A acurácia por sujeito varia de 82% a 100% no binário (p. 8).
- **Limitações:** poucos sujeitos, pouca diversidade de idade e gênero, estresse induzido em laboratório. Parte do sinal de respiração pode refletir apenas a fala durante o TSST (p. 6, p. 8).
- **O que uso no meu trabalho:** é o dataset principal e o benchmark de comparação, nas mesmas condições (E4 no pulso, LOSO, binário). Define os parâmetros de janela e as features. A diferença de população (adultos saudáveis em laboratório vs. crianças com TEA na escola) é a principal limitação a discutir.

### 4. Siirtola (2019): Continuous stress detection using the sensors of commercial smartwatch

- **Referência (ABNT):** SIIRTOLA, P. Continuous stress detection using the sensors of commercial smartwatch. In: ACM INTERNATIONAL JOINT CONFERENCE ON PERVASIVE AND UBIQUITOUS COMPUTING; INTERNATIONAL SYMPOSIUM ON WEARABLE COMPUTERS, 2019, London. *Adjunct Proceedings* [...]. New York: ACM, 2019. DOI: 10.1145/3341162.3344831.
- **Objetivo:** verificar se dá para detectar estresse de forma independente do usuário **sem EDA**, que smartwatches comerciais não têm, e qual o efeito do tamanho da janela (p. 1–2).
- **Participantes:** os 15 sujeitos do WESAD, usando apenas os dados do E4 (p. 2).
- **Sensores e sinais:** ACC, TEMP, EDA, BVP e HR do E4, testando **todas as combinações** de sensores (p. 2–3).
- **Pré-processamento / janelas:** mesmas features de Schmidt mais HR. Janelas de 15, 30, 60, 90 e 120 s com passo de 0,25 s. Problema binário (diversão e baseline juntos como "não estresse") (p. 2).
- **Modelo e validação:** LDA, QDA e RF com **LOSO**, sem seleção de features. Métrica: **acurácia balanceada** (p. 2).
- **Resultados:** janelas maiores são melhores (15 s: 81,2% → 120 s: 84,0%) (p. 3, Tab. 2). Melhor resultado: **87,4% com TEMP+BVP+HR (LDA)**, sem EDA. O LDA superou o RF na maioria das combinações. Só BVP já passa de 80%, e o ACC **piora** o resultado (p. 3). A variação entre sujeitos vai de 62,6% a 98,8% (p. 4, Tab. 4).
- **Limitações:** dataset pequeno, que não permitiu janelas maiores que 120 s, variação grande entre sujeitos e falta de seleção de features (p. 3–4).
- **O que uso no meu trabalho:** justifica testar janelas de 60 e 120 s. O resultado de que **EDA não é indispensável** é importante para a pulseira de baixo custo, já que o GSR barato é ruidoso (ver AutiSense e Monteiro). A variação entre sujeitos reforça a necessidade de personalização, como em Goodwin e Imbiriba. Vale incluir LDA entre os modelos testados.

### 5. Monteiro (2022): Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos

- **Referência (ABNT):** MONTEIRO, K. R. *Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos*. 2022. 105 f. Dissertação (Mestrado em Engenharia Biomédica) – Faculdade UnB Gama, Universidade de Brasília, Brasília, 2022.
- **Objetivo:** desenvolver um sistema vestível de baixo custo para monitorar crises (*meltdowns*) em adolescentes autistas (p. 7, p. 20).
- **Participantes:** 10 adultos saudáveis em teste funcional com crise simulada, outros 10 adultos com *Cold Pressor Test* e **1 adolescente autista** em uma sessão de 20 min (p. 53, p. 57).
- **Sensores e sinais:** luva com GSR Grove (dedos indicador e médio), termistor (polegar), MPU6050 (dorso) e ECG AD8232 no peito. O Pulse Sensor e o MAX30102 foram testados e **descartados por instabilidade** (p. 33–35, p. 44). Processamento em Arduino Nano, rádio nRF24L01+ até um Raspberry Pi 3, depois Wi-Fi para a nuvem (p. 7, p. 38–40).
- **Pré-processamento / janelas:** energia do acelerômetro em janelas de 30 s e variação percentual de GSR, HR e temperatura em relação ao instante inicial (p. 42).
- **Modelo e validação:** **índice de meltdown** = soma ponderada de flags binárias por limiar (E > 990%, GSR < −18 a −25%, HR > 20%, Temp > 2%). Crise se IM ≥ 0,75 e pré-crise entre 0,26 e 0,50 (p. 42–43, p. 51). Não usa aprendizado de máquina.
- **Resultados:** 90% de detecção na crise simulada e 100% no *Cold Pressor Test*. No adolescente autista não houve crise nem falso positivo, e ele relatou conforto com a luva (p. 53, p. 56–58).
- **Limitações:** a pandemia e a demora em **dois comitês de ética** (CEP UnB e FEPECS) impediram testes com autistas (p. 43–44, p. 59). O próprio autor reconhece que os testes não mostram se o sistema detecta *meltdowns* reais. Sugere aprendizado de máquina para calibrar os limiares e app ou alerta automático como trabalho futuro (p. 51, p. 59).
- **O que uso no meu trabalho:** é a referência brasileira que mostra a **lacuna**: hardware de baixo custo sem IA validada. Ele próprio aponta o aprendizado de máquina e o alerta em tempo real como próximo passo, que é o que o seu projeto faz. Também cita o preço do E4 (US$ 1.690, p. 20) e a dificuldade de aprovação ética, o que justifica a prova de conceito com dados públicos.

### 6. AutiSense (2025–2026): Smart assistant system for children with autism spectrum disorder

- **Referência (ABNT):** SHAHEEN, B.; DARABEE, R. *AutiSense*: smart assistant system for children with autism spectrum disorder. 2026. Trabalho de Conclusão de Curso (Bacharelado em Engenharia de Sistemas Computacionais) – Palestine Polytechnic University, Hebron, 2026. *(confirmar ano e cidade no repositório)*
- **Objetivo:** detectar sinais de estresse cedo e apoiar o cuidador na intervenção, sobretudo em transições de tarefa (p. 3).
- **Participantes:** testes em cenários controlados e roteirizados. As páginas lidas não relatam teste com crianças com TEA (p. 53, p. 57).
- **Sensores e sinais:** **ESP32-C3 Zero**, MAX30102 no dedo indicador (mais perfusão que o pulso), Grove GSR e MPU6050 a ~50 Hz. Anel de LED como timer visual. Raspberry Pi com tela para atividades calmantes (p. 26–28, p. 44–45).
- **Pré-processamento / janelas:** HR como média de 5 batimentos e GSR suavizado com **média móvel exponencial**, porque o movimento da mão gerava falsos positivos. Features de movimento em janelas de 1 s (RMS da aceleração, vibração e RMS do giroscópio) para distinguir repouso, atividade e *stimming* (p. 47–48, p. 51).
- **Modelo e validação:** **limiares relativos à linha de base pessoal**: moderado se HR > +20% e GSR > +2%; alto se HR > +40% e GSR > +5%. O estado de movimento muda a interpretação (p. 38, p. 58–59).
- **Resultados:** classificou corretamente os 5 cenários testados (normal, *stimming*, atividade, estresse moderado e alto). Alertas pelo **bot do Telegram** com intervalo mínimo de 30 s entre eles (p. 50, p. 57–59).
- **Limitações:** sem modelo treinado nem métricas em dados reais, testes roteirizados, custo, alcance e bateria (p. 23).
- **O que uso no meu trabalho:** é a referência mais próxima do seu hardware (ESP32 + MAX30102 + GSR + MPU6050), útil para o firmware proposto. Ideias diretas para o seu sistema: linha de base individual, uso do **acelerômetro para não confundir agitação física ou stimming com estresse**, suavização do GSR e intervalo mínimo entre alertas no Telegram. O seu diferencial é **substituir os limiares por um modelo treinado e validado**.

### 7. Pulseira Febrace (2023): Pulseira indicadora de desregulação em autistas

- **Referência (ABNT):** TERTO, D. C. V.; SILVA, L. S.; SANTOS, A. *Pulseira indicadora de desregulação em autistas*. Pôster apresentado na Feira Brasileira de Ciências e Engenharia (FEBRACE), São Paulo, 2023. ETE Henrique Lage – FAETEC, Niterói.
- **Objetivo:** identificar crises de desregulação por batimentos acelerados e aumento de suor e avisar o responsável em tempo real (p. 1).
- **Participantes:** não houve teste com autistas, apenas testes de bancada.
- **Sensores e sinais:** três sensores de batimento testados (o melhor foi da DFRobot, no dedo), **DHT11** (umidade e temperatura) como indicador de suor, módulo transceptor (pulseira → chaveiro do responsável), buzzer e display OLED (p. 1).
- **Modelo e validação:** limiares fixos: buzzer se BPM > 100 e LED se umidade da pele > 80% (p. 1).
- **Resultados:** os sensores de batimento foram **instáveis com movimento** e nenhum funcionou bem no pulso. O transceptor alcançou 50 m (p. 1).
- **Limitações:** limiares genéricos (BPM > 100 é comum em crianças em atividade normal), DHT11 não mede atividade eletrodérmica e não houve validação.
- **O que uso no meu trabalho:** evidencia o principal problema de hardware: **ruído de movimento no sensor óptico do pulso**. Isso justifica tratar o ACC como sinal de contexto e o processamento em janelas. Também mostra por que um limiar fixo e igual para todos é frágil.

### 8. Gernert et al. (2024): Stress in autism (STREAM), protocolo de estudo

- **Referência (ABNT):** GERNERT, C. C. et al. Stress in autism (STREAM): a study protocol on the role of circadian activity, sleep quality and sensory reactivity. *PLoS ONE*, v. 19, n. 5, e0303209, 2024. DOI: 10.1371/journal.pone.0303209.
- **Tipo:** **protocolo de estudo, não revisão**. Ainda não há resultados (p. 1).
- **Objetivo:** investigar a relação entre sono, ritmo circadiano, reatividade sensorial e estresse em adultos autistas (p. 1, p. 3).
- **Participantes:** planejados 20 adultos com TEA e 20 controles, de 18–65 anos, com QI > 70 (p. 3).
- **Sensores e sinais:** pulseira (HR a 64 Hz, EDA a 4 Hz) por 7 dias, faixa de EEG no sono e relatos subjetivos por *Temporal Experience Tracing* (p. 4–6).
- **Pré-processamento / indicadores:** lista detalhada de indicadores. **HR/HRV:** HR médio, amplitude, SDNN, pNN50, LF, HF, LF/HF. **EDA:** média, amplitude, área, componentes fásico e tônico, número e amplitude dos picos (p. 6–7, Tab. 3–4).
- **Ética e dados:** pseudonimização com identificador numérico aleatório, dados pessoais separados dos experimentais, chave guardada fora da rede, conformidade com GDPR e Helsinque. Estudo desenhado com participação de pessoas autistas (p. 4, p. 6–7).
- **Limitações (previstas):** amostra pequena, viés de seleção (só participa quem tolera a pulseira, o que é relevante por causa da sensibilidade sensorial), artefatos de movimento e baixa amostragem dos wearables (p. 10–11).
- **O que uso no meu trabalho:** a lista de indicadores HR/HRV/EDA para o pré-processamento. O **modelo de manejo de dados** (pseudonimização, separação de identidade, consentimento) é uma referência para a seção de **ética e LGPD** (dia 15). O dado de ~90% das crianças com TEA com percepção sensorial atípica (p. 2) reforça o requisito de conforto da pulseira.

---

## Pendências

- [ ] Conferir os números da tabela de referência nas páginas indicadas.
- [ ] Reescrever o campo "O que uso no meu trabalho" com suas palavras.
- [ ] Decidir se busca uma **revisão sistemática de verdade** sobre wearables e estresse em TEA, já que o STREAM é um protocolo.
- [ ] Confirmar ano e cidade da referência do AutiSense.
- [ ] Dataset do IEEE DataPort (TEA): ainda não baixado.

---

## Modelo de fichamento

### [Título do trabalho]

- **Referência (ABNT):**
- **Objetivo:**
- **Participantes:**
- **Sensores e sinais:**
- **Pré-processamento / janelas:**
- **Modelo e validação:**
- **Resultados:**
- **Limitações:**
- **O que uso no meu trabalho:**
