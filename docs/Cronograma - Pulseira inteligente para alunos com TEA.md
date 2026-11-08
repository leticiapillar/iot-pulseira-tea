# Cronograma: Pulseira inteligente para alunos com TEA

**Período:** 09/11/2026 a 28/11/2026 (20 dias)
**Premissas:** trabalho individual, cerca de 2 a 3 horas por dia. Os dias 1 a 15 são de desenvolvimento e os dias 16 a 20 são de revisão e gravação do vídeo.

---

## Fase 1: Fundamentação e dados (dias 1 a 4)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 1 | seg 09/11 | Criar conta no IEEE DataPort e baixar o dataset de TEA. Baixar o WESAD (UCI) e o wearable-and-stress (Hugging Face). Criar o repositório no GitHub | Os 3 datasets baixados e o repositório criado |
| 2 | ter 10/11 | Ler e fichar os 2 artigos de Goodwin (2019 e 2023) e a revisão sobre HRV e suor da pele em TEA | Fichamento: sinais, modelos e métricas usados |
| 3 | qua 11/11 | Ler e fichar os projetos com ESP32 (UnB, AutiSense, Febrace) e 2 ou 3 artigos que usam o WESAD, para ter números de comparação | Tabela comparativa de trabalhos relacionados |
| 4 | qui 12/11 | Escrever a **Contextualização** do relatório: o problema, a justificativa e a relevância (dados sobre TEA no Brasil e inclusão escolar) | Seção 1 do relatório (rascunho) |

## Fase 2: Exploração e preparação dos dados (dias 5 a 7)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 5 | sex 13/11 | Explorar o WESAD: ler os arquivos da pulseira, ver os rótulos e fazer gráficos dos sinais em repouso vs. estresse | Notebook `01_exploracao_wesad` |
| 6 | sáb 14/11 | Explorar o dataset de TEA e comparar com o WESAD: taxas de amostragem, unidades, sinais em comum | Notebook `02_exploracao_tea` |
| 7 | dom 15/11 | Pré-processar: filtrar ruído, dividir em janelas de 30 a 60 s, extrair indicadores (frequência cardíaca, HRV, picos de suor, intensidade de movimento) | Script de pré-processamento e dataset de indicadores |

## Fase 3: Modelagem e resultados (dias 8 a 11)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 8 | seg 16/11 | Treinar modelos no WESAD: regressão logística (como Goodwin), Random Forest e XGBoost. Validar deixando uma pessoa de fora por vez, para o modelo ser testado em gente que nunca viu | Tabela de métricas (acurácia, F1, AUROC) |
| 9 | ter 17/11 | **Experimento central:** testar o melhor modelo no dataset de TEA, sem e com ajuste ao novo público | Resultado da pergunta "funciona em crianças com TEA?" |
| 10 | qua 18/11 | Gerar os *insights*: quais sinais mais pesam na decisão e com quanto tempo de antecedência o alerta aparece. Fazer os gráficos finais | Gráficos e interpretação |
| 11 | qui 19/11 | Escrever a **Análise de Resultados**, comparando com a literatura da Fase 1 | Seção 4 do relatório |

## Fase 4: Arquitetura e demo (dias 12 a 14)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 12 | sex 20/11 | Desenhar o diagrama da arquitetura (pulseira → MQTT → IA → dashboard e alerta) e escrever a **Arquitetura e Metodologia** | Diagrama e Seção 2 |
| 13 | sáb 21/11 | Montar a demo: script que reproduz o WESAD como pulseira virtual → MQTT → modelo → alerta no Telegram | Pipeline funcionando de ponta a ponta |
| 14 | dom 22/11 | Dashboard em Streamlit com o sinal em tempo real, o nível de agitação, os alertas e o histórico. Escrever **Desenvolvimento e Funcionalidades** | Dashboard e Seção 3 |

## Fase 5: Fechamento (dia 15)

| Dia | Data | Tarefas | Entrega do dia |
|---|---|---|---|
| 15 | seg 23/11 | Escrever **Conclusões e Lições Aprendidas**, incluindo limitações, ética e LGPD. Escrever o README. Montar a primeira versão completa do relatório em PDF | Relatório v1 completo e repositório organizado |

## Revisão e vídeo (dias 16 a 20)

| Dia | Data | Tarefas |
|---|---|---|
| 16 | ter 24/11 | Revisar o relatório: texto, referências (ABNT) e figuras |
| 17 | qua 25/11 | Roteiro do pitch de 5 minutos: problema (1 min), solução (1 min), demo (2 min), resultados e impacto (1 min) |
| 18 | qui 26/11 | Gravar a demo e a narração |
| 19 | sex 27/11 | Editar o vídeo e testar o README do zero, como se fosse outra pessoa |
| 20 | sáb 28/11 | **Entrega:** PDF, link do GitHub e link do vídeo |

---

## Pontos de atenção

- **Dia 1 é crítico:** o IEEE DataPort pode exigir cadastro e demorar para liberar o download. Se o dataset de TEA não sair, o plano B é usar só o WESAD e tratar a aplicação em TEA como hipótese, sustentada pelos artigos de Goodwin.
- **Folga:** os dias 4, 11 e 15 são de escrita e absorvem atrasos das fases técnicas.
- **Escreva ao longo do caminho:** guarde gráficos e decisões em cada notebook, para o relatório quase se montar sozinho.

## Referências principais

- Goodwin et al. (2019). *Predicting aggression to others in youth with autism using a wearable biosensor*. Autism Research. https://zendy.io/title/10.1002/aur.2151
- Imbiriba, Demirkaya, Singh, Erdogmus & Goodwin (2023). *Wearable Biosensing to Predict Imminent Aggressive Behavior in Psychiatric Inpatient Youths With Autism*. JAMA Network Open. https://pesquisa.bvsalud.org/sms/resource/pt/mdl-38127348
- Revisão sobre monitoramento de estresse por wearables em TEA (PLoS ONE). https://doaj.org/article/5b48ae0d92704c078729119a53a97657
- Monteiro, K. R. (2022). Dissertação de mestrado, UnB. https://repositorio.unb.br/bitstream/10482/44757/1/2022_KlausRibeiroMonteiro.pdf
- AutiSense: Smart Assistant System for Children with ASD (PPU). https://scholar.ppu.edu/handle/123456789/9458
- Pulseira para identificação de crises (Febrace). https://virtual.febrace.org.br/2023/ENG/2017/poster

## Datasets

- WESAD (UCI Machine Learning Repository), dataset de detecção de estresse com pulseira Empatica E4.
- wearable-and-stress (Hugging Face): https://huggingface.co/datasets/evannh/wearable-and-stress
- Heart Rate as a Predictor of Challenging Behaviours among Children with Autism (IEEE DataPort): https://ieee-dataport.org/documents/dataset-heart-rate-predictor-challenging-behaviours-among-children-autism-wearable
