# Cronograma: Pulseira inteligente para alunos com TEA

**Período:** 09/11/2026 a 28/11/2026 (20 dias)
**Premissas:** trabalho individual, cerca de 2 a 3 horas por dia. Os dias 1 a 15 são de desenvolvimento e os dias 16 a 20 são de revisão e gravação do vídeo.

> **Replanejamento em 15/11/2026: plano B ativado.** O acesso ao dataset de TEA do IEEE DataPort não foi liberado a tempo. Com isso:
> - O dia 6 (explorar o dataset de TEA) foi **cancelado**.
> - ~~O experimento central (dia 9) passa a ser **validação externa**: treinar no WESAD com os sinais que os dois datasets têm em comum (frequência cardíaca, temperatura e movimento) e testar na parte `NURSE` do wearable-and-stress, sem e com ajuste ao novo público.~~ (substituído pelo plano C, abaixo)
> - A aplicação em TEA passa a ser tratada como **hipótese**. Ela se apoia em Goodwin et al. (2019) e Imbiriba et al. (2023), que usaram a mesma pulseira (Empatica E4) em jovens com TEA. Essa limitação está registrada na Seção 1.5 do relatório e será retomada nas Conclusões.
> - As fases técnicas foram empurradas 1 dia, e o dia 10 foi juntado ao dia 9. A Contextualização (dia 4) foi feita em 15/11, o que libera parte do dia 11 como folga.
>
> **Replanejamento em 15/11/2026 (noite): plano C ativado.** A checagem do `NURSE` mostrou que os rótulos do wearable-and-stress não são confiáveis (detalhes em `data/README.md`). Com isso:
> - O `NURSE` **deixa de ser usado para medir desempenho**. Ele entra só na Análise e nas Limitações, como exemplo da dificuldade de rotular estresse no mundo real.
> - O experimento central (dia 9) passa a ser **sensores completos vs. sensores de baixo custo**, todo no WESAD, com validação deixando uma pessoa de fora (LOSO). A pergunta é: quanto desempenho se perde ao trocar a pulseira de pesquisa por sensores que um ESP32 consegue ler?
> - A aplicação em TEA continua sendo uma **hipótese**. O plano C fortalece o elo do custo, que é a lacuna central do projeto.

**Legenda:** ✅ feito · ⏳ replanejado · ❌ cancelado

---

## Fase 1: Fundamentação e dados (dias 1 a 4)

| Dia | Data | Tarefas | Entrega do dia | Status |
|---|---|---|---|---|
| 1 | seg 09/11 | Criar conta no IEEE DataPort e baixar o dataset de TEA. Baixar o WESAD (UCI) e o wearable-and-stress (Hugging Face). Criar o repositório no GitHub | 2 datasets baixados (WESAD e wearable-and-stress) e repositório criado | ✅ O dataset de TEA não foi obtido (plano B) |
| 2 | ter 10/11 | Ler e fichar os artigos de Goodwin (2019) e Imbiriba (2023) e o protocolo STREAM (Gernert et al., PLoS ONE) | Fichamento: sinais, modelos e métricas usados | ✅ Feito em 15/11 |
| 3 | qua 11/11 | Ler e fichar os projetos de baixo custo (UnB, AutiSense, Febrace) e 2 artigos que usam o WESAD (Schmidt 2018, Siirtola 2019) | Tabela comparativa de trabalhos relacionados | ✅ Feito em 15/11 |
| 4 | qui 12/11 | Escrever a **Contextualização** do relatório: o problema, a justificativa e a relevância (dados sobre TEA no Brasil e inclusão escolar) | Seção 1 do relatório (rascunho) | ✅ Feito em 15/11; faltam os itens `[conferir]` |

## Fase 2: Exploração e preparação dos dados (dias 5 a 7)

| Dia | Data | Tarefas | Entrega do dia | Status |
|---|---|---|---|---|
| 5 | ~~sex 13/11~~ **dom 15/11** | Explorar o WESAD: ler os arquivos da pulseira, ver os rótulos e fazer gráficos dos sinais em repouso vs. estresse | Notebook `01_exploracao_wesad` | ⏳ |
| 6 | ~~sáb 14/11~~ | ~~Explorar o dataset de TEA e comparar com o WESAD~~ | ~~Notebook `02_exploracao_tea`~~ | ❌ Sem o dataset de TEA |
| 7 | ~~dom 15/11~~ **seg 16/11** | Pré-processar o WESAD: filtrar ruído, dividir em janelas de 60 s (testar também 120 s), extrair indicadores (frequência cardíaca, HRV, picos de suor, temperatura, intensidade de movimento), marcando cada indicador com o grupo de sensores de que depende (completo, baixo custo, GSR). ~~Checar o `NURSE`~~: feito em 15/11, levou ao plano C | Script de pré-processamento e dataset de indicadores | ⏳ |

## Fase 3: Modelagem e resultados (dias 8 a 11)

| Dia | Data | Tarefas | Entrega do dia | Status |
|---|---|---|---|---|
| 8 | ~~seg 16/11~~ **ter 17/11** | Treinar modelos no WESAD: regressão logística (como Goodwin), LDA, Random Forest e XGBoost. Validar deixando uma pessoa de fora por vez (LOSO), para o modelo ser testado em gente que nunca viu. Comparar com Schmidt et al. (2018) | Tabela de métricas (acurácia, F1 macro, acurácia balanceada, AUROC) | ⏳ |
| 9 | ~~ter 17/11~~ **qua 18/11** | **Experimento central (plano C):** comparar, com LOSO no WESAD, três conjuntos de sensores: (1) completo, como na Empatica E4; (2) baixo custo: frequência cardíaca, temperatura e movimento; (3) baixo custo + EDA (sensor GSR). Na mesma sessão, gerar os *insights*: quais sinais mais pesam na decisão, desempenho por participante e gráficos finais | Resultado da pergunta "quanto se perde ao trocar a pulseira de pesquisa por sensores de baixo custo?" e gráficos | ⏳ Inclui o antigo dia 10 |
| 10 | ~~qua 18/11~~ | Juntado ao dia 9 | — | ⏳ |
| 11 | qui 19/11 | Escrever a **Análise de Resultados**, comparando com a literatura da Fase 1 e discutindo o que a comparação de sensores sugere para uma pulseira escolar de baixo custo e por que o `NURSE` não pôde ser usado | Seção 4 do relatório | Meio dia livre como folga |

## Fase 4: Arquitetura e demo (dias 12 a 14)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 12 | sex 20/11 | Desenhar o diagrama da arquitetura (pulseira → MQTT → IA → dashboard e alerta) e escrever a **Arquitetura e Metodologia**, incluindo as mudanças para os planos B e C | Diagrama e Seção 2 |
| 13 | sáb 21/11 | Montar a demo: script que reproduz o WESAD como pulseira virtual → MQTT → modelo → alerta no Telegram | Pipeline funcionando de ponta a ponta |
| 14 | dom 22/11 | Dashboard em Streamlit com o sinal em tempo real, o nível de agitação, os alertas e o histórico. Escrever **Desenvolvimento e Funcionalidades** | Dashboard e Seção 3 |

## Fase 5: Fechamento (dia 15)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 15 | seg 23/11 | Escrever **Conclusões e Lições Aprendidas**, incluindo as limitações (sem dados de TEA, sem teste com crianças), ética e LGPD. Escrever o README. Montar a primeira versão completa do relatório em PDF | Relatório v1 completo e repositório organizado |

## Revisão e vídeo (dias 16 a 20)

| Dia | Data | Tarefas |
|---|---|---|
| 16 | ter 24/11 | Revisar o relatório: texto, referências (ABNT) e figuras. Resolver os itens `[conferir]` da Seção 1 |
| 17 | qua 25/11 | Roteiro do pitch de 5 minutos: problema (1 min), solução (1 min), demo (2 min), resultados e impacto (1 min) |
| 18 | qui 26/11 | Gravar a demo e a narração |
| 19 | sex 27/11 | Editar o vídeo e testar o README do zero, como se fosse outra pessoa |
| 20 | sáb 28/11 | **Entrega:** PDF, link do GitHub e link do vídeo |

---

## Pontos de atenção

- **O "baixo custo" é simulado.** O plano C usa um subconjunto dos sinais da própria E4, não sensores baratos reais, que são mais ruidosos. O resultado é um teto para o hardware barato e precisa ser apresentado assim.
- **Folga:** a folga do dia 4 já foi usada. Restam o meio dia livre do dia 11 e o dia 15, de escrita, para absorver atrasos.
- **Escreva ao longo do caminho:** guarde gráficos e decisões em cada notebook, para o relatório quase se montar sozinho.

## Referências principais

- Goodwin et al. (2019). *Predicting aggression to others in youth with autism using a wearable biosensor*. Autism Research. https://zendy.io/title/10.1002/aur.2151
- Imbiriba, Demirkaya, Singh, Erdogmus & Goodwin (2023). *Wearable Biosensing to Predict Imminent Aggressive Behavior in Psychiatric Inpatient Youths With Autism*. JAMA Network Open. https://pesquisa.bvsalud.org/sms/resource/pt/mdl-38127348
- Gernert et al. Protocolo do estudo STREAM sobre monitoramento de estresse por wearables em TEA (PLoS ONE). https://doaj.org/article/5b48ae0d92704c078729119a53a97657
- Schmidt et al. (2018). *Introducing WESAD, a multimodal dataset for wearable stress and affect detection*. ICMI '18.
- Siirtola (2019). Detecção de estresse com sensores de pulso usando o WESAD.
- Monteiro, K. R. (2022). Dissertação de mestrado, UnB. https://repositorio.unb.br/bitstream/10482/44757/1/2022_KlausRibeiroMonteiro.pdf
- AutiSense: Smart Assistant System for Children with ASD (PPU). https://scholar.ppu.edu/handle/123456789/9458
- Pulseira para identificação de crises (Febrace). https://virtual.febrace.org.br/2023/ENG/2017/poster

As referências completas, em ABNT, estão em `docs/referencias/fichamentos.md`.

## Datasets

- WESAD (UCI Machine Learning Repository), dataset de detecção de estresse com pulseira Empatica E4. **Dataset principal.**
- wearable-and-stress (Hugging Face): https://huggingface.co/datasets/evannh/wearable-and-stress. Checado em 15/11: rótulos não confiáveis, **não usado para medir desempenho** (plano C).
- ~~Heart Rate as a Predictor of Challenging Behaviours among Children with Autism (IEEE DataPort)~~: https://ieee-dataport.org/documents/dataset-heart-rate-predictor-challenging-behaviours-among-children-autism-wearable. **Não obtido** (plano B).
