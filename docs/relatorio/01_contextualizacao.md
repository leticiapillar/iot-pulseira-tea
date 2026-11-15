# 1 Contextualização

> **RASCUNHO PARA REVISÃO**: redigido com apoio de IA a partir dos fichamentos. Antes de usar:
> (1) reescreva com suas palavras; (2) confira os números marcados com **[conferir]** nas fontes oficiais;
> (3) apague estas notas. As citações seguem o sistema autor-data (ABNT NBR 10520).

## 1.1 O problema

O Transtorno do Espectro Autista (TEA) é uma condição do neurodesenvolvimento caracterizada por diferenças na comunicação e na interação social e por padrões restritos e repetitivos de comportamento. Além dessas características centrais, pessoas com TEA apresentam com frequência alterações no processamento sensorial: estima-se que cerca de 90% das crianças diagnosticadas tenham percepções sensoriais atípicas, e a sobrecarga sensorial é apontada como uma das principais fontes de estresse nessa população (GERNERT et al., 2024).

Um dos maiores desafios no cotidiano dessas crianças, de suas famílias e de seus professores são as **crises de desregulação** (em inglês, *meltdowns*). Diferentemente de uma birra, a crise é uma resposta involuntária a uma sobrecarga, sensorial, emocional ou de demandas, que excede a capacidade de autorregulação da criança. Ela pode se manifestar como choro intenso, gritos, autolesão ou agressão a outras pessoas. Comportamentos desse tipo ocorrem em até 80% das crianças e adolescentes com autismo e estão entre os motivos mais comuns de encaminhamento a serviços de saúde comportamental (IMBIRIBA et al., 2023).

O que torna essas crises especialmente difíceis de manejar é a sua **imprevisibilidade**. Entre 30% e 40% das pessoas com TEA são minimamente verbais, e mesmo as que se comunicam com fluência frequentemente têm dificuldade de reconhecer e relatar o próprio estado interno (IMBIRIBA et al., 2023). Para quem observa de fora, a crise parece surgir "do nada". Goodwin et al. (2019) destacam que essa imprevisibilidade cria uma barreira de acesso a serviços educacionais, terapêuticos e comunitários: famílias deixam de expor a criança a ambientes potencialmente estressantes por medo de uma crise sem aviso.

Na escola, o impacto é direto. Uma crise interrompe a aula, coloca em risco o próprio aluno e os colegas, gera estresse no professor e, quando recorrente, pode levar ao afastamento do aluno do ensino regular, o oposto do que a política de inclusão pretende.

## 1.2 Relevância

O tema ganha relevância à medida que cresce o número de alunos com TEA nas escolas brasileiras. Pela primeira vez, o Censo Demográfico 2022 investigou o diagnóstico de autismo e identificou cerca de **2,4 milhões de pessoas** com diagnóstico de TEA no Brasil, o equivalente a **1,2% da população**. O maior percentual foi observado entre **meninos de 5 a 9 anos (3,8%)**, justamente em idade escolar (IBGE, 2025) **[conferir na tabela oficial do IBGE]**. Como se trata de diagnósticos declarados, especialistas apontam que o número real tende a ser maior, por causa do subdiagnóstico.

No ambiente escolar, o crescimento é ainda mais acelerado. Segundo dados do Censo Escolar, o número de matrículas de estudantes com TEA na educação básica passou de cerca de **636 mil em 2023 para 919 mil em 2024**, um aumento de **44,4% em um único ano** (EXTRA CLASSE, 2025) **[conferir nas tabelas do INEP e, se possível, citar o INEP diretamente]**. Além disso, 95,7% dos estudantes da educação especial entre 4 e 17 anos estão matriculados em **classes comuns** (INEP, 2025) **[conferir]**. O cenário internacional confirma a tendência: nos Estados Unidos, a estimativa mais recente é de **1 em cada 31 crianças** de 8 anos com diagnóstico de TEA (CDC, 2025).

Esse crescimento é sustentado por um marco legal que garante o direito à educação inclusiva. A Lei nº 12.764/2012 (Lei Berenice Piana) instituiu a Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista e reconheceu a pessoa com TEA como pessoa com deficiência para todos os efeitos legais (BRASIL, 2012). A Lei nº 13.146/2015 (Lei Brasileira de Inclusão) assegurou o sistema educacional inclusivo em todos os níveis (BRASIL, 2015).

Na prática, isso significa que a maior parte desses alunos está em salas regulares, nas quais um professor atende simultaneamente dezenas de estudantes e raramente possui formação especializada em TEA. É nesse contexto que perceber os sinais de uma crise **antes** do seu pico pode fazer diferença. Com alguns minutos de antecedência, o professor pode oferecer uma pausa sensorial, reorganizar o ambiente ou acionar o profissional de apoio.

## 1.3 Justificativa

Há evidências científicas de que alterações fisiológicas precedem as crises. A crise está associada à ativação do sistema nervoso simpático, que acelera os batimentos cardíacos, reduz a variabilidade da frequência cardíaca e aumenta a sudorese, alterando a atividade eletrodérmica (EDA) da pele (SCHMIDT et al., 2018). Esses sinais podem ser medidos de forma contínua e pouco invasiva por uma pulseira.

Goodwin et al. (2019) monitoraram 20 jovens com TEA internados em uma unidade psiquiátrica com uma pulseira comercial (Empatica E4). Os autores mostraram que, a partir de 3 minutos de sinais anteriores, era possível prever uma agressão **1 minuto antes** de ela ocorrer, com área sob a curva ROC (AUC) de 0,71 para um modelo geral e de 0,84 para modelos personalizados. O estudo foi ampliado por Imbiriba et al. (2023) para 70 participantes em quatro hospitais, e a regressão logística previu comportamentos agressivos **3 minutos antes** do início, com AUROC de 0,80. Segundo Goodwin et al. (2019), familiares e profissionais consideram que mesmo **60 segundos de aviso** são suficientes para intervir e evitar a escalada da crise.

Esses resultados, no entanto, ainda não chegaram à escola, por três motivos:

1. **Custo do equipamento.** A pulseira usada nos estudos custava cerca de US$ 1.690 por unidade (MONTEIRO, 2022) e foi descontinuada pelo fabricante (SHAHEEN; DARABEE, 2026), o que inviabiliza seu uso em uma sala com vários alunos.
2. **Contexto de validação.** Os estudos foram conduzidos em ambiente hospitalar, com equipe de pesquisa dedicada à observação, e não na rotina escolar.
3. **Falta de inteligência nos protótipos de baixo custo.** As iniciativas com hardware acessível usam regras fixas de limiar em vez de modelos treinados e validados, e não foram testadas em crises reais. É o caso da luva-pulseira com Arduino da Universidade de Brasília (MONTEIRO, 2022), do sistema AutiSense com ESP32 (SHAHEEN; DARABEE, 2026) e da pulseira apresentada na Febrace (TERTO; SILVA; SANTOS, 2023). O próprio Monteiro (2022) aponta o aprendizado de máquina e o alerta em tempo real como próximos passos necessários.

Há, portanto, uma **lacuna** entre a evidência científica, obtida com equipamento caro em ambiente clínico, e as soluções de baixo custo, que ainda não usam inteligência artificial validada. Este trabalho se propõe a aproximar esses dois lados: uma arquitetura de pulseira de baixo custo baseada em Internet das Coisas (IoT), combinada com um modelo de aprendizado de máquina treinado e avaliado com dados públicos, capaz de alertar o professor em tempo real.

## 1.4 Objetivos

### 1.4.1 Objetivo geral

Desenvolver uma prova de conceito de pulseira inteligente, baseada em IoT e inteligência artificial, que monitore sinais fisiológicos associados ao estresse e alerte o professor antes do pico de uma possível crise de desregulação em alunos com TEA.

### 1.4.2 Objetivos específicos

- Extrair indicadores fisiológicos (frequência cardíaca, variabilidade da frequência cardíaca, atividade eletrodérmica, temperatura da pele e intensidade de movimento) de sinais de pulseira disponíveis em bases públicas.
- Treinar e comparar modelos de classificação de estresse (regressão logística, Random Forest e XGBoost), avaliando-os em pessoas não vistas no treino (validação deixando um participante de fora).
- Avaliar a capacidade de generalização do modelo para um público e um contexto diferentes daqueles usados no treino.
- Implementar o fluxo completo de uma solução IoT: pulseira (virtualizada) → protocolo MQTT → serviço de inferência → alerta via Telegram e painel de acompanhamento para o professor.
- Discutir os requisitos éticos e de proteção de dados (LGPD) envolvidos no monitoramento de dados de saúde de crianças e adolescentes.

## 1.5 Escopo e limitações

Este trabalho é uma **prova de conceito com sensores virtualizados**: a pulseira é simulada a partir do dataset público WESAD (SCHMIDT et al., 2018), que reproduz os sinais de uma pulseira real. Não foram realizados testes com crianças, pois isso exigiria aprovação de um Comitê de Ética em Pesquisa. Na pesquisa de Monteiro (2022), entre o primeiro parecer favorável e a aprovação final pelos comitês envolvidos passaram-se cerca de dois anos. O dataset de crianças com TEA inicialmente previsto (IEEE DataPort) não pôde ser obtido no prazo do trabalho. Por isso, a aplicação ao público com TEA é tratada como **hipótese**, sustentada pela literatura (GOODWIN et al., 2019; IMBIRIBA et al., 2023), que utilizou o mesmo modelo de pulseira presente no WESAD. Por fim, a solução proposta é uma ferramenta de **apoio** ao professor e não um dispositivo de diagnóstico.

---

## Referências citadas nesta seção

BRASIL. Lei nº 12.764, de 27 de dezembro de 2012. Institui a Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista. *Diário Oficial da União*, Brasília, DF, 28 dez. 2012.

BRASIL. Lei nº 13.146, de 6 de julho de 2015. Institui a Lei Brasileira de Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência). *Diário Oficial da União*, Brasília, DF, 7 jul. 2015.

CENTERS FOR DISEASE CONTROL AND PREVENTION (CDC). Prevalence and early identification of autism spectrum disorder among children aged 4 and 8 years: Autism and Developmental Disabilities Monitoring Network, 16 sites, United States, 2022. *MMWR Surveillance Summaries*, Atlanta, v. 74, n. 2, 2025. **[conferir autores (Shaw, K. A. et al.), volume e páginas no MMWR]**

EXTRA CLASSE. Matrículas de estudantes autistas cresceram 44,4% em um ano. *Extra Classe*, Porto Alegre, abr. 2025. Disponível em: https://www.extraclasse.org.br/educacao/2025/04/matriculas-de-estudantes-com-autistas-cresceram-444-em-um-ano/. Acesso em: 15 nov. 2026.

GERNERT, C. C. et al. Stress in autism (STREAM): a study protocol on the role of circadian activity, sleep quality and sensory reactivity. *PLoS ONE*, v. 19, n. 5, e0303209, 2024. DOI: 10.1371/journal.pone.0303209.

GOODWIN, M. S. et al. Predicting aggression to others in youth with autism using a wearable biosensor. *Autism Research*, v. 12, n. 8, p. 1286-1296, 2019. DOI: 10.1002/aur.2151.

IBGE. INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA. Censo 2022: Brasil tem 2,4 milhões de pessoas com diagnóstico de autismo. *Agência IBGE Notícias*, Rio de Janeiro, 23 maio 2025. Disponível em: https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43464. Acesso em: 15 nov. 2026. **[conferir título exato da notícia]**

IMBIRIBA, T. et al. Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism. *JAMA Network Open*, v. 6, n. 12, e2348898, 2023. DOI: 10.1001/jamanetworkopen.2023.48898.

INEP. INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. *Censo Escolar da Educação Básica 2024*: resumo técnico. Brasília, DF: Inep, 2025. **[conferir título e localizar os números de TEA e classes comuns no documento oficial]**

MONTEIRO, K. R. *Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos*. 2022. 105 f. Dissertação (Mestrado em Engenharia Biomédica) – Faculdade UnB Gama, Universidade de Brasília, Brasília, 2022.

SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: INTERNATIONAL CONFERENCE ON MULTIMODAL INTERACTION, 20., 2018, Boulder. *Proceedings* [...]. New York: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.

SHAHEEN, B.; DARABEE, R. *AutiSense*: smart assistant system for children with autism spectrum disorder. 2026. Trabalho de Conclusão de Curso (Bacharelado em Engenharia de Sistemas Computacionais) – Palestine Polytechnic University, Hebron, 2026.

TERTO, D. C. V.; SILVA, L. S.; SANTOS, A. *Pulseira indicadora de desregulação em autistas*. Pôster apresentado na Feira Brasileira de Ciências e Engenharia (FEBRACE), São Paulo, 2023.
