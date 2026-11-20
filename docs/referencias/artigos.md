# Artigos e fontes de dados do projeto

Lista das fontes usadas no relatório: os documentos guardados em [`artigos/`](artigos/) e as bases de dados do Inep (microdados do Censo Escolar 2025 e Sinopse Estatística da Educação Básica 2025). As referências seguem o mesmo formato ABNT das seções do relatório. As anotações de leitura (páginas, números conferidos) estão em [`fichamentos.md`](fichamentos.md).

> Os PDFs e as bases do Inep **não vão para o git** (direitos autorais e tamanho; ver `.gitignore`). Para reproduzir, baixe cada um pelo link indicado e salve com o nome de arquivo da tabela.

## 1. Documentos em `artigos/`

### 1.1 Artigos científicos e trabalhos acadêmicos

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
| Shaw et al. (MMWR, CDC) | 2025 | Crianças de 4 e 8 anos, 16 locais da rede ADDM, Estados Unidos (dados de 2022) | Não se aplica: vigilância epidemiológica a partir de registros de saúde e educação | Não se aplica | — | Prevalência de **1 em cada 31** crianças de 8 anos com TEA (1 em 36 em 2020; 1 em 150 em 2000) | https://www.cdc.gov/mmwr/volumes/74/ss/ss7402a1.htm |

> ⚠️ **Atenção ao usar a tabela:**
> - O trabalho da PLoS ONE **não é uma revisão**. É o *protocolo* do estudo STREAM, ainda sem resultados. Se você precisar de uma revisão de verdade sobre wearables e estresse em TEA, é preciso buscar outra.
> - Só o AutiSense usa **ESP32**. A UnB usa Arduino Nano e a Febrace não nomeia o microcontrolador no pôster.
> - Imbiriba: os 0,80 de AUROC vêm da divisão por sessão. Na validação que deixa indivíduos de fora, a mais comparável à sua, o valor é 0,77.

### 1.2 Legislação e normas

| Arquivo | Referência curta | Seções |
|---|---|---|
| `LEI Nº 12.764, DE 27 DE DEZEMBRO DE 2012.pdf` | BRASIL, 2012 (Política Nacional dos Direitos da Pessoa com TEA) | 1 |
| `LEI Nº 13.146, DE 6 DE JULHO DE 2015.pdf` | BRASIL, 2015 (Lei Brasileira de Inclusão) | 1 |
| `LEI Nº 13.709, DE 14 DE AGOSTO DE 2018.pdf` | BRASIL, 2018 (LGPD) | 2, 5 |
| `RESOLUÇÃO Nº 466, DE 12 DE DEZEMBRO DE 2012.pdf` | CONSELHO NACIONAL DE SAÚDE, 2012 | 5 |

### 1.3 Publicação do Inep

| Arquivo | Referência curta | Seções |
|---|---|---|
| `resumo_tecnico_censo_da_educacao_basica_2025.pdf` | INEP, 2026a | 1 |

## 2. Bases de dados do Inep

| Pasta | Conteúdo | Referência curta | Uso no projeto |
|---|---|---|---|
| `microdados_censo_escolar_2025_v2/` | Tabelas `Escola`, `Matricula`, `Docente`, `Gestor_Escolar` e `Curso_Tecnico` (CSV), com o dicionário de dados e os questionários em `Anexos/` | INEP, 2026b | Elaboração própria com `src/data/contexto_censo_escolar.py` (saída em `results/metrics/contexto_censo_escolar_2025.csv`): turmas com aluno da educação especial, escolas com profissional de apoio, docentes com formação em educação especial (Seção 1) |
| `Sinopse_Estatistica_da_Educação_Basica_2025_V2/` (há uma cópia em `dados/`) | Planilhas `.xlsx` e `.ods` com as tabelas consolidadas, e o arquivo `md5` | INEP, 2026c | Tab. 1.58 (matrículas da educação especial por tipo: 1.298.637 de TEA no Brasil; 64.201 no RS) e Tab. 1.55 (classes comuns) (Seção 1) |

Links para baixar:

- Microdados: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- Sinopse: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica
- Resumo técnico: https://download.inep.gov.br/publicacoes/institucionais/estatisticas_e_indicadores/resumo_tecnico_censo_da_educacao_basica_2025.pdf

## 3. Referências completas (ABNT)

BRASIL. Lei nº 12.764, de 27 de dezembro de 2012. Institui a Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista. *Diário Oficial da União*, Brasília, DF, 28 dez. 2012.

BRASIL. Lei nº 13.146, de 6 de julho de 2015. Institui a Lei Brasileira de Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência). *Diário Oficial da União*, Brasília, DF, 7 jul. 2015.

BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). *Diário Oficial da União*, Brasília, DF, 15 ago. 2018.

CONSELHO NACIONAL DE SAÚDE (Brasil). Resolução nº 466, de 12 de dezembro de 2012. Aprova diretrizes e normas regulamentadoras de pesquisas envolvendo seres humanos. *Diário Oficial da União*, Brasília, DF, 13 jun. 2013.

GERNERT, C. C. et al. Stress in autism (STREAM): a study protocol on the role of circadian activity, sleep quality and sensory reactivity. *PLoS ONE*, v. 19, n. 5, e0303209, 2024. DOI: 10.1371/journal.pone.0303209.

GOODWIN, M. S. et al. Predicting aggression to others in youth with autism using a wearable biosensor. *Autism Research*, v. 12, n. 8, p. 1286-1296, 2019. DOI: 10.1002/aur.2151.

IMBIRIBA, T. et al. Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism. *JAMA Network Open*, v. 6, n. 12, e2348898, 2023. DOI: 10.1001/jamanetworkopen.2023.48898.

INEP. INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. *Censo Escolar da Educação Básica 2025*: resumo técnico. Brasília, DF: Inep, 2026a. ISBN 978-65-5801-132-3. Disponível em: https://download.inep.gov.br/publicacoes/institucionais/estatisticas_e_indicadores/resumo_tecnico_censo_da_educacao_basica_2025.pdf. Acesso em: 15 nov. 2026.

INEP. INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. *Microdados do Censo Escolar da Educação Básica 2025*. Brasília, DF: Inep, 2026b. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar. Acesso em: 15 nov. 2026.

INEP. INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. *Sinopse Estatística da Educação Básica 2025*. Brasília, DF: Inep, 2026c. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica. Acesso em: 15 nov. 2026.

MONTEIRO, K. R. *Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos*. 2022. 105 f. Dissertação (Mestrado em Engenharia Biomédica) – Faculdade UnB Gama, Universidade de Brasília, Brasília, 2022.

SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: INTERNATIONAL CONFERENCE ON MULTIMODAL INTERACTION, 20., 2018, Boulder. *Proceedings* [...]. New York: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.

SHAHEEN, B.; DARABEE, R. *AutiSense*: smart assistant system for children with autism spectrum disorder. 2026. Trabalho de Conclusão de Curso (Bacharelado em Engenharia de Sistemas Computacionais) – Palestine Polytechnic University, Hebron, 2026.

SHAW, K. A. et al. Prevalence and early identification of autism spectrum disorder among children aged 4 and 8 years: Autism and Developmental Disabilities Monitoring Network, 16 sites, United States, 2022. *MMWR Surveillance Summaries*, Atlanta, v. 74, n. 2, p. 1-22, 17 abr. 2025. Disponível em: https://www.cdc.gov/mmwr/volumes/74/ss/ss7402a1.htm. Acesso em: 15 nov. 2026.

SIIRTOLA, P. Continuous stress detection using the sensors of commercial smartwatch. In: ACM INTERNATIONAL JOINT CONFERENCE ON PERVASIVE AND UBIQUITOUS COMPUTING; INTERNATIONAL SYMPOSIUM ON WEARABLE COMPUTERS, 2019, London. *Adjunct Proceedings* [...]. New York: ACM, 2019. DOI: 10.1145/3341162.3344831.

TERTO, D. C. V.; SILVA, L. S.; SANTOS, A. *Pulseira indicadora de desregulação em autistas*. Pôster apresentado na Feira Brasileira de Ciências e Engenharia (FEBRACE), São Paulo, 2023.
