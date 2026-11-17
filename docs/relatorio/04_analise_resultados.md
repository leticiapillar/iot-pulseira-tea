# 4 Análise de Resultados

Esta seção apresenta os resultados do experimento central do trabalho: medir quanto desempenho na detecção de estresse se perde quando a pulseira de pesquisa (Empatica E4) é substituída por um conjunto de sensores que um microcontrolador de baixo custo, como o ESP32, consegue ler. A metodologia está descrita na Seção 2. Em resumo:

- **Tarefa:** binária, estresse (TSST) contra não estresse (repouso e diversão), no dataset WESAD (SCHMIDT et al., 2018).
- **Janelas:** de 60 s, com passo de 30 s.
- **Calibração por pessoa:** cada indicador é expresso como diferença em relação aos 5 primeiros minutos de repouso da própria pessoa, e esses 5 minutos ficam fora da avaliação.
- **Validação:** deixa um participante de fora (LOSO). Cada pessoa é avaliada por um modelo que nunca viu dados dela, como aconteceria com um aluno novo.
- **Métrica principal:** F1 macro, porque a acurácia engana nesse problema. Um classificador que sempre responde "não estresse" acerta 66% das janelas, mas tem F1 macro de apenas 0,40.

## 4.1 Comparação dos conjuntos de sensores

Foram comparados três conjuntos de sensores, em ordem crescente de custo:

1. **Só FC:** frequência cardíaca, obtida de um sensor óptico de pulso;
2. **Baixo custo:** FC, temperatura da pele e movimento (acelerômetro);
3. **Baixo custo + EDA:** os sinais anteriores mais a atividade eletrodérmica (sensor GSR). Equivale a todos os sensores de pulso da E4.

A Tabela 4.1 mostra o melhor modelo de cada conjunto. A Figura 4.1 mostra todos os modelos e as configurações alternativas.

**Tabela 4.1:** Desempenho por conjunto de sensores (LOSO, 15 participantes, 800 janelas avaliadas, 34% de estresse; janelas de 60 s, calibradas)

| Conjunto | Indicadores | Melhor modelo | F1 macro | Acurácia balanceada | AUROC |
|---|---|---|---|---|---|
| Classe majoritária (referência) | — | — | 0,397 | 0,500 | 0,500 |
| Só FC | 5 | LDA | 0,826 | 0,812 | 0,892 |
| Baixo custo (FC, temperatura, movimento) | 11 | Regressão logística | 0,835 | 0,840 | 0,907 |
| Baixo custo + EDA | 18 | Random Forest | **0,948** | **0,950** | **0,988** |

Fonte: elaboração própria (`results/metrics/loso_wesad.csv`).

**Figura 4.1:** F1 macro por conjunto de sensores e modelo, em três configurações (`results/figures/02_comparacao_conjuntos.png`).

Todos os conjuntos ficam muito acima da referência, o que confirma que a detecção não é um acaso da distribuição das classes. O resultado central, porém, é que **o ganho vem quase todo do sensor de EDA**:

- **Temperatura e movimento acrescentam pouco.** Somá-los à frequência cardíaca leva o F1 macro de 0,826 para 0,835.
- **A EDA dá o salto.** Somá-la leva o F1 para 0,948 e o AUROC para 0,988.

Em outras palavras, sem o sensor de EDA perde-se cerca de 0,11 a 0,12 de F1 macro. Nos quatro algoritmos testados (regressão logística, LDA, Random Forest e XGBoost), as diferenças entre modelos foram menores que as diferenças entre conjuntos de sensores: **a escolha dos sensores importa mais que a escolha do algoritmo**.

A curva ROC (Figura 4.2) mostra o mesmo de outro ângulo. Com EDA, é possível detectar mais de 95% das janelas de estresse com menos de 5% de alarmes falsos. Sem EDA, para detectar 80% do estresse é preciso aceitar cerca de 15% de alarmes falsos.

**Figura 4.2:** Curvas ROC da Random Forest para os três conjuntos, com e sem calibração (`results/figures/02_roc.png`).

## 4.2 O papel da calibração por pessoa

O experimento também foi repetido **sem calibração**, com os valores brutos dos indicadores, e com **janelas de 120 s**. A Tabela 4.2 resume o melhor modelo em cada caso.

**Tabela 4.2:** F1 macro do melhor modelo por configuração

| Configuração | Só FC | Baixo custo | Baixo custo + EDA |
|---|---|---|---|
| 60 s, calibrado (principal) | 0,826 | 0,835 | 0,948 |
| 60 s, sem calibração | 0,828 | 0,887 | 0,880 |
| 120 s, calibrado | 0,836 | 0,900 | 0,952 |

Fonte: elaboração própria (`results/metrics/02_perda_por_conjunto.csv`).

Sem calibração, o conjunto com EDA cai de 0,948 para 0,880 e deixa de superar o conjunto de baixo custo. Isso tem uma explicação fisiológica. O nível de condutância da pele varia muito de uma pessoa para outra, por fatores como espessura da pele, hidratação e temperatura ambiente. Assim, o valor absoluto da EDA diz pouco sobre o estado de uma pessoa nova. O que carrega informação é a **mudança em relação ao repouso da própria pessoa**.

A calibração não beneficia os conjuntos sem EDA: a FC em valores absolutos já generaliza razoavelmente entre pessoas. Por isso o resultado do conjunto de baixo custo varia de 0,835 a 0,900 conforme a configuração. Já o conjunto com EDA calibrada fica estável em torno de 0,95 nas duas janelas.

A consequência prática para a pulseira escolar é um **requisito de uso**: se ela tiver sensor de EDA, precisa de alguns minutos de calibração em repouso, por exemplo no início do dia, antes de gerar alertas.

## 4.3 Quais sinais pesam na decisão

Para medir a contribuição de cada sensor, foi usada a **importância por permutação** dentro do LOSO. Em cada participante de teste, os indicadores de um sensor são embaralhados, e mede-se quanto o AUROC cai (Figura 4.3). No conjunto completo, embaralhar a EDA reduz o AUROC em **0,22**, e embaralhar a FC, em 0,05. Temperatura e movimento ficam próximos de zero.

Quando a EDA não está disponível, o modelo passa a depender da FC (queda de 0,20). A temperatura ganha algum peso (0,05), e o movimento continua pouco relevante (0,02).

Entre os indicadores individuais, os mais importantes são:

- o **nível tônico da EDA** (média do SCL e da EDA);
- a **FC média**;
- o **número de respostas fásicas da pele por minuto** (picos de suor).

A importância de cada indicador isolado é pequena porque os indicadores do mesmo sensor são redundantes: embaralhar um deles deixa os outros intactos. Por isso a análise por sensor é a mais informativa.

**Figura 4.3:** Importância por permutação, por sensor e por indicador (`results/figures/02_importancia.png`).

## 4.4 Diferenças entre pessoas

As métricas agregadas escondem uma variação grande entre participantes (Figura 4.4):

- **Sem EDA:** o F1 macro por pessoa vai de 0,48 a 1,00, com desvio padrão de 0,17.
- **Com EDA:** 12 dos 15 participantes passam de 0,94, e o desvio cai para 0,11.

**Figura 4.4:** F1 macro de cada participante nos três conjuntos (`results/figures/02_por_participante.png`).

Os casos mais difíceis sem EDA são explicados pelas anotações do próprio WESAD:

- **S6** relatou ter tido uma semana estressante, de modo que o estudo foi relaxante para ele. Também não se estressou com a entrevista do TSST, porque havia feito várias entrevistas nas semanas anteriores.
- **S15** não acreditou na encenação do TSST.

Nesses dois participantes, a FC média subiu apenas 1,5 e 5,9 bpm no estresse. Em 6 dos 15 participantes, a subida passou de 15 bpm. A EDA, porém, subiu, e o conjunto com EDA acertou S6 (0,85) e S15 (1,00). Siirtola (2019, p. 4) também encontrou em S15 o pior resultado (62,6%) com sensores sem EDA.

O pior caso com EDA é **S2** (0,60), que teve uma resposta eletrodérmica fraca no estresse e para o qual o WESAD não traz anotação explicativa.

Duas lições saem daqui:

- **Diferentes pessoas reagem ao estresse por canais fisiológicos diferentes**, e um sensor a mais reduz o risco de a pulseira "não enxergar" um aluno específico.
- **Nenhum conjunto funcionou para todas as pessoas.** Isso reforça o que Goodwin et al. (2019) e Imbiriba et al. (2023) observaram em jovens com TEA: modelos personalizados ou adaptados à pessoa tendem a funcionar melhor que um modelo único.

## 4.5 Simulação de uso: tempo até o alerta e alarmes falsos

Para aproximar a análise do uso real, a sessão completa de cada participante foi reproduzida como se a pulseira gerasse uma probabilidade de estresse a cada 30 s. A sessão incluiu a meditação, condição de calma que não fez parte do treino. Foram testadas duas regras de alerta:

- **imediata:** alerta na primeira janela com probabilidade acima de 0,5;
- **2 janelas seguidas:** alerta só quando duas janelas consecutivas passam de 0,5.

**Tabela 4.3:** Simulação de uso (Random Forest, LOSO, 15 participantes)

| Conjunto | Regra | Estresse detectado (participantes) | Latência mediana (máx.) | Janelas de estresse com alerta | Alarme falso: repouso e diversão | Alarme falso: meditação |
|---|---|---|---|---|---|---|
| Só FC | imediata | 15 de 15 | 1,3 min (1,8) | 78% | 13,3% | 7,0% |
| Só FC | 2 seguidas | 15 de 15 | 1,9 min (4,3) | 66% | 5,6% | 2,3% |
| Baixo custo | imediata | 15 de 15 | 1,3 min (6,8) | 76% | 9,8% | 23,4% |
| Baixo custo | 2 seguidas | 15 de 15 | 1,8 min (7,3) | 67% | 4,9% | 16,7% |
| Baixo custo + EDA | imediata | 15 de 15 | 1,3 min (5,1) | 94% | 4,1% | 7,3% |
| Baixo custo + EDA | 2 seguidas | 15 de 15 | 1,8 min (5,6) | 86% | 2,8% | 4,9% |

Fonte: elaboração própria (`results/metrics/02_uso_alertas.csv`). A latência conta do início do estresse até o fim da janela que dispara o alerta.

**Figura 4.5:** Probabilidade de estresse ao longo da sessão de três participantes (`results/figures/02_sessao_probabilidade.png`).

Em todos os conjuntos, o estresse foi detectado em todos os participantes, com latência mediana de cerca de 1,3 minuto. Essa latência é quase toda o tempo de preencher uma janela de 60 s: o modelo só decide depois de ter um minuto de dados.

A diferença entre os conjuntos aparece na **qualidade** dos alertas:

- **Com EDA**, o alerta fica ativo em 94% do período de estresse e dispara em apenas 4% dos momentos calmos.
- **Sem EDA**, a cobertura do estresse cai para cerca de 77%, e os alarmes falsos sobem para 10% a 13%.

O conjunto de baixo custo teve ainda **23% de alarmes falsos na meditação**. Isso indica que temperatura e movimento confundem calma com estresse fora das condições vistas no treino. Na escola, onde as atividades variam ao longo do dia, esse é um ponto de atenção.

A regra de **2 janelas seguidas** custa cerca de 30 s a mais de latência e reduz os alarmes falsos de um terço a mais da metade, conforme o conjunto. Para o professor, um alarme falso frequente leva a ignorar a pulseira, e um atraso de 30 s ainda é compatível com os 60 s de aviso que Goodwin et al. (2019) consideram suficientes para intervir. Por isso, essa é a regra adotada na demonstração (Seção 3).

**Atenção à interpretação:** o WESAD não tem um período "antes da crise". O que se mediu aqui é a **demora para detectar** um estresse que já começou, e não a **antecedência** em relação a uma crise. Goodwin et al. (2019) e Imbiriba et al. (2023) medem antecedência: preveem agressões 1 a 3 minutos antes de ocorrerem, em jovens com TEA. Os dois resultados não devem ser comparados diretamente.

## 4.6 Comparação com a literatura

**Validação do pipeline.** Nas mesmas condições de Schmidt et al. (2018), isto é, todos os sensores fisiológicos do pulso, Random Forest, LOSO e sem calibração, este trabalho obteve **acurácia de 87,7% e F1 macro de 86,6%**. Schmidt et al. (2018, p. 7, Tab. 4) relatam 88,3% e 86,1%. A proximidade indica que o pré-processamento e a avaliação reproduzem corretamente o benchmark do dataset. A calibração por pessoa, contribuição deste trabalho, eleva o F1 macro para 94,8%.

**Frequência cardíaca sozinha.** Schmidt et al. (2018, p. 7, Tab. 4) obtiveram F1 macro de até 83,1% usando só o BVP do pulso (LDA). O conjunto "só FC" deste trabalho chegou a 82,6%, com apenas 5 indicadores de FC. O resultado é coerente com a ideia de que um sensor óptico de pulso, sozinho, já detecta a maior parte do estresse induzido em laboratório.

**O papel da EDA.** Siirtola (2019, p. 3, Tab. 3) concluiu que a EDA não é necessária: o melhor resultado (87,4% de acurácia balanceada, LDA, janelas de 120 s) usou temperatura e sinais cardíacos, e incluir a EDA piorava o resultado. Schmidt et al. (2018) também obtiveram resultados piores com a EDA do pulso sozinha do que com o BVP sozinho. Os resultados deste trabalho **sem calibração** concordam com os dois:

- o conjunto de baixo custo alcançou 88,5% de acurácia balanceada (88,9% com janelas de 120 s, calibrado), próximo dos 87,4% de Siirtola;
- a EDA não trouxe ganho.

**Com calibração por pessoa**, porém, a EDA passou a ser o sinal mais importante. Uma interpretação possível é que a EDA do pulso só é útil quando referida ao repouso da própria pessoa, o que os dois trabalhos anteriores não fizeram. Essa interpretação precisa ser confirmada em outros dados.

**Projetos de baixo custo.** Os protótipos de baixo custo da literatura usam limiares fixos ou relativos à linha de base pessoal:

- MONTEIRO (2022): luva com GSR, ECG, termistor e acelerômetro;
- SHAHEEN e DARABEE (2026): AutiSense, com ESP32, MAX30102, GSR e MPU6050;
- TERTO, SILVA e SANTOS (2023): pulseira da Febrace, com limiar de BPM > 100.

Nenhum deles foi avaliado com métricas em pessoas não vistas. Os resultados aqui oferecem uma referência quantitativa para esse tipo de hardware. Também confirmam duas escolhas do AutiSense: comparar com a **linha de base pessoal** e usar o **GSR** junto com a FC. A diferença deste trabalho é substituir os limiares definidos à mão por um modelo treinado e avaliado.

## 4.7 Por que o segundo dataset não foi usado

O planejamento previa uma validação externa com outro dataset público do Hugging Face (*wearable-and-stress*), que reúne dados de enfermeiras em ambiente hospitalar com a mesma pulseira E4. A verificação feita antes do uso mostrou que os rótulos desse arquivo não são confiáveis:

- **A parte copiada do WESAD tem rótulos deslocados em cerca de 20 minutos.** O "estresse" cai em períodos de repouso ou meditação.
- **Os rótulos da parte das enfermeiras são incompletos.** No estudo original (HOSSEINI et al., 2022), um modelo de detecção de estresse marcava episódios, e as enfermeiras apenas validavam esses episódios em um questionário no fim do turno, limitado aos seis mais longos. Nenhuma enfermeira acrescentou episódios não detectados, e os períodos sem rótulo nunca foram confirmados como calmos.
- **O teste de sanidade falhou.** A frequência cardíaca é maior no rótulo de "estresse alto" em apenas 6 das 13 enfermeiras, contra 15 de 15 participantes no WESAD.

Esse episódio ilustra uma dificuldade central da área: **rotular estresse fora do laboratório é difícil**, e um rótulo derivado de outro modelo pode só reproduzir os erros dele. Para uma pulseira escolar, isso significa que a coleta de dados reais com alunos com TEA precisará de um protocolo de rotulagem cuidadoso. Um exemplo é a observação direta de comportamentos, como fazem Goodwin et al. (2019).

## 4.8 O que os resultados sugerem para uma pulseira escolar de baixo custo

Nas condições do WESAD, uma pulseira com **sensor óptico de pulso e sensor GSR**, calibrada em poucos minutos de repouso, aproxima-se do desempenho da pulseira de pesquisa (F1 macro 0,95). Também gera poucos alarmes falsos com a regra de 2 janelas seguidas.

Uma pulseira só com sensor de pulso ainda detecta o estresse na maioria das pessoas (F1 0,83), mas com duas a três vezes mais alarmes falsos e falhas nas pessoas cuja frequência cardíaca reage pouco. Temperatura e acelerômetro acrescentam pouco à detecção. O acelerômetro, porém, continua útil como **sinal de contexto** (por exemplo, distinguir agitação física de estresse), como propõe o AutiSense.

Esses resultados devem ser lidos com as seguintes limitações:

1. **O baixo custo é simulado.** Os conjuntos usam sinais da própria E4, que são mais limpos que os de sensores baratos. Monteiro (2022) descartou dois sensores ópticos de pulso por instabilidade, e a pulseira da Febrace teve problemas com o movimento. Os números aqui são um **teto** para o hardware barato.
2. **A população é diferente.** São 15 adultos jovens neurotípicos, em estresse induzido em laboratório (TSST), e não crianças com TEA em sala de aula. A transferência para esse público é uma hipótese, apoiada por estudos com a mesma pulseira (GOODWIN et al., 2019; IMBIRIBA et al., 2023).
3. **Mede-se latência, não antecedência.** O WESAD não permite avaliar a previsão de uma crise antes que ela aconteça.
4. **Parte do processamento não é causal.** O filtro da EDA usa amostras futuras dentro da janela (`filtfilt`). Uma pulseira em tempo real precisaria de um filtro causal, o que pode alterar ligeiramente os resultados.
5. **O descarte por ruído é desigual.** A fração de janelas descartadas por ruído no sinal de pulso variou entre condições: 1,8% no repouso, 9,3% no estresse e 18,6% na diversão. Ou seja, o movimento já prejudica o sensor óptico mesmo em laboratório.
6. **A amostra é pequena.** Com 15 participantes, cada pessoa pesa quase 7% do resultado, e diferenças de poucos centésimos entre modelos não devem ser interpretadas como relevantes.

---

## Referências citadas nesta seção

GOODWIN, M. S. et al. Predicting aggression to others in youth with autism using a wearable biosensor. *Autism Research*, v. 12, n. 8, p. 1286-1296, 2019. DOI: 10.1002/aur.2151.

HOSSEINI, S. et al. A multimodal sensor dataset for continuous stress detection of nurses in a hospital. *Scientific Data*, v. 9, 255, 2022. DOI: 10.1038/s41597-022-01361-y.

IMBIRIBA, T. et al. Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism. *JAMA Network Open*, v. 6, n. 12, e2348898, 2023. DOI: 10.1001/jamanetworkopen.2023.48898.

MONTEIRO, K. R. *Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos*. 2022. 105 f. Dissertação (Mestrado em Engenharia Biomédica) – Faculdade UnB Gama, Universidade de Brasília, Brasília, 2022.

SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: INTERNATIONAL CONFERENCE ON MULTIMODAL INTERACTION, 20., 2018, Boulder. *Proceedings* [...]. New York: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.

SHAHEEN, B.; DARABEE, R. *AutiSense*: smart assistant system for children with autism spectrum disorder. 2026. Trabalho de Conclusão de Curso (Bacharelado em Engenharia de Sistemas Computacionais) – Palestine Polytechnic University, Hebron, 2026.

SIIRTOLA, P. Continuous stress detection using the sensors of commercial smartwatch. In: ACM INTERNATIONAL JOINT CONFERENCE ON PERVASIVE AND UBIQUITOUS COMPUTING; INTERNATIONAL SYMPOSIUM ON WEARABLE COMPUTERS, 2019, London. *Adjunct Proceedings* [...]. New York: ACM, 2019. DOI: 10.1145/3341162.3344831.

TERTO, D. C. V.; SILVA, L. S.; SANTOS, A. *Pulseira indicadora de desregulação em autistas*. Pôster apresentado na Feira Brasileira de Ciências e Engenharia (FEBRACE), São Paulo, 2023.
