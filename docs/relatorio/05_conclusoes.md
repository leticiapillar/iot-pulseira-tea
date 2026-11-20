# 5 Conclusões e Lições Aprendidas

## 5.1 Síntese

Este trabalho partiu de uma lacuna: estudos com jovens com TEA mostram que sinais fisiológicos medidos no pulso antecedem crises de agressão (GOODWIN et al., 2019; IMBIRIBA et al., 2023), mas usam uma pulseira de pesquisa cara e descontinuada, em ambiente hospitalar. Já os protótipos de baixo custo usam limiares fixos, sem modelo treinado nem avaliação em pessoas novas (MONTEIRO, 2022; SHAHEEN; DARABEE, 2026; TERTO; SILVA; SANTOS, 2023).

A prova de conceito construída aproxima esses dois lados. Uma pulseira (virtualizada) envia sinais por MQTT, um serviço de inferência estima a probabilidade de estresse a cada 30 s, e o professor recebe um alerta no Telegram e acompanha a turma num painel. A Tabela 5.1 retoma os objetivos específicos da Seção 1.4.

**Tabela 5.1:** Objetivos específicos e resultados

| Objetivo específico | Resultado | Onde |
|---|---|---|
| Extrair indicadores fisiológicos de sinais de pulseira | 18 indicadores de FC, temperatura, movimento e EDA, em janelas de 60 s. A variabilidade da FC foi calculada, mas **excluída**: no estresse ela é dominada pelo ruído de movimento | Seção 2.6 |
| Treinar e comparar modelos, avaliando em pessoas não vistas | Quatro modelos e uma referência, com LOSO. O pipeline reproduz o resultado de referência do WESAD (F1 macro 86,6% contra 86,1% de Schmidt et al., 2018). Com calibração por pessoa, a Random Forest chega a F1 macro de 0,95 | Seções 4.1, 4.2 e 4.6 |
| Comparar conjuntos de sensores de baixo custo | Só FC: F1 0,83. FC + temperatura + movimento: 0,84. + EDA: 0,95. A EDA é o sinal que mais pesa, e temperatura e movimento acrescentam pouco | Seções 4.1 e 4.3 |
| Implementar o fluxo IoT completo | Pulseira virtual → MQTT → serviço de inferência → Telegram e painel, testado com três alunos simultâneos que o modelo nunca viu. O estresse foi detectado nos três | Seção 3 |
| Discutir ética e proteção de dados | Requisitos e medidas na Seção 5.4. Parte das medidas já está na arquitetura (privacidade desde a concepção) | Seções 2.4.1 e 5.4 |

A resposta à pergunta central do experimento (quanto se perde ao trocar a pulseira de pesquisa por sensores que um ESP32 consegue ler) é: **com um sensor de pulso e um sensor de condutância da pele (GSR), quase nada**, nas condições do WESAD. Sem o GSR, a detecção continua possível, mas com duas a três vezes mais alarmes falsos e falhas nas pessoas cuja frequência cardíaca reage pouco ao estresse. Para uma pulseira escolar de baixo custo, isso sugere priorizar o GSR junto com o sensor óptico de pulso, e calibrar cada pulseira em poucos minutos de repouso do próprio aluno.

## 5.2 Contribuições

- **Uma referência quantitativa para hardware de baixo custo.** A comparação de conjuntos de sensores, avaliada em pessoas não vistas, estima o que cada sensor barato acrescenta, algo que os protótipos de baixo custo da literatura não mediram.
- **A calibração por pessoa como peça central.** Expressar cada indicador em relação ao repouso da própria pessoa elevou o F1 macro de 0,88 para 0,95 e mudou o papel da EDA: de sinal sem ganho (como em Schmidt et al., 2018, e Siirtola, 2019) para o sinal mais importante. Na pulseira, essa calibração custa só 5 minutos de repouso.
- **Uma regra de alerta pensada para o professor.** A simulação de uso mostrou que exigir duas janelas seguidas custa cerca de 30 s e reduz os alarmes falsos de um terço a mais da metade.
- **Um protótipo de ponta a ponta reproduzível.** Todo o código, o modelo e as instruções estão no repositório, e a demonstração roda num computador comum, sem hardware.

## 5.3 Limitações

As limitações já foram discutidas ao longo do relatório (Seções 1.5 e 4.8). As principais são:

1. **Não há dados de pessoas com TEA.** O dataset de crianças com TEA previsto não foi obtido a tempo, e o modelo foi treinado e avaliado com 15 adultos neurotípicos. A aplicação ao público com TEA é uma **hipótese**, apoiada por estudos que usaram a mesma pulseira em jovens com TEA (GOODWIN et al., 2019; IMBIRIBA et al., 2023).
2. **Estresse induzido não é crise.** O WESAD mede estresse provocado em laboratório (TSST), e não crises de desregulação. O sistema mede a **demora para detectar** um estresse que já começou, e não a **antecedência** em relação a uma crise.
3. **O baixo custo é simulado.** Os conjuntos de sensores usam sinais da própria pulseira de pesquisa. Sensores baratos reais são mais ruidosos, principalmente com movimento (MONTEIRO, 2022; TERTO; SILVA; SANTOS, 2023), e os resultados são um teto para esse hardware.
4. **Não houve pulseira física nem teste com alunos.** O firmware do ESP32 é uma proposta, e a demonstração usa uma pulseira virtual. Testes com crianças exigiriam aprovação ética, que levou cerca de dois anos no trabalho de Monteiro (2022).
5. **A recuperação depois do estresse gera alertas.** No teste da sessão completa, a probabilidade continuou alta por vários minutos depois do fim do estresse, porque a condutância da pele demora a voltar ao nível de base (Seção 3.7).
6. **Os indicadores em tempo real não são idênticos aos do treino.** Os de frequência cardíaca diferem, porque o detector de batimentos se ajusta ao trecho de sinal que recebe (Seção 3.3). O filtro da EDA usado no treino também não é causal (Seção 4.8).

## 5.4 Ética e proteção de dados

Uma pulseira que monitora o estado fisiológico de crianças e adolescentes na escola levanta questões éticas que vão além da técnica. Esta seção resume os requisitos para que uma versão real seja aceitável, e o que a arquitetura proposta já atende.

### 5.4.1 O que diz a LGPD

- **Os dados são sensíveis.** Sinais fisiológicos e a estimativa de estresse são **dados referentes à saúde** e, portanto, dados pessoais sensíveis (BRASIL, 2018, art. 5º, II). O tratamento depende, em regra, de **consentimento específico e destacado** do titular ou do responsável legal, para finalidades específicas (art. 11, I).
- **Os titulares são crianças e adolescentes.** O tratamento deve ser feito no **melhor interesse** deles, com consentimento específico e em destaque de pelo menos um dos pais ou do responsável legal (art. 14, *caput* e § 1º).
- **Princípios.** A **finalidade** deve ser explícita e limitada (apoiar o aluno), e a **necessidade** exige tratar só os dados indispensáveis para ela (art. 6º, I e III). A **segurança** exige medidas técnicas contra acessos não autorizados (arts. 6º, VII, e 46).
- **Direitos do titular.** Os responsáveis devem poder acessar, corrigir e pedir a eliminação dos dados (art. 18), e os dados devem ser eliminados ao fim do tratamento (art. 16).
- **Relatório de impacto.** Pelo volume e pela sensibilidade dos dados, uma implantação real deveria ser precedida de um relatório de impacto à proteção de dados pessoais (art. 38).
- **Pseudonimização não é anonimização.** Um pseudônimo como `aluno03` reduz a exposição, mas a escola consegue ligá-lo ao aluno. Os dados continuam sendo pessoais, e a LGPD continua valendo integralmente.

### 5.4.2 O que a arquitetura já atende

**Tabela 5.2:** Requisitos de proteção de dados e situação no protótipo

| Requisito | No protótipo | Para uma versão real |
|---|---|---|
| Minimização (art. 6º, III) | Os sinais brutos ficam só em memória (últimos 60 s), no serviço e no painel. Em disco, só probabilidades, resumo das janelas e alertas | Definir por quanto tempo o histórico é guardado e eliminá-lo depois |
| Pseudonimização | As mensagens identificam o aluno só pelo pseudônimo. A correspondência com o nome fica fora do sistema | Guardar essa correspondência separada, com acesso restrito, como no protocolo STREAM (GERNERT et al., 2024) |
| Rede local | Broker e serviço de inferência rodam na rede da escola. Os sinais não saem dela | Manter. Evitar serviços em nuvem para os sinais |
| Mensagem mínima a terceiros | O alerta do Telegram leva só o pseudônimo e o nível | Avaliar um canal próprio da escola, porque o Telegram é um serviço externo, com servidores fora do país |
| Segurança (art. 46) | Broker sem autenticação, por ser demonstração | Usuário e senha no broker, TLS, acesso ao painel com login |
| Consentimento (arts. 11 e 14) | Não se aplica: não há dados de alunos reais | Termo de consentimento dos responsáveis, com linguagem clara, e direito de desistir a qualquer momento |

### 5.4.3 Questões éticas além da lei

- **Apoio, não vigilância.** A pulseira só se justifica se o uso for **a favor do aluno**: antecipar o acolhimento. O histórico não deve servir para avaliar, punir ou rotular o aluno, nem para avaliar o professor. Essa finalidade precisa estar escrita no termo de consentimento e nas regras da escola.
- **Assentimento do aluno.** Além do consentimento dos responsáveis, o próprio aluno deve concordar, na medida da sua compreensão, e poder tirar a pulseira. Na pesquisa, isso corresponde ao termo de assentimento previsto na Resolução CNS nº 466/2012 (CONSELHO NACIONAL DE SAÚDE, 2012).
- **Conforto sensorial.** Cerca de 90% das crianças com TEA têm percepção sensorial atípica (GERNERT et al., 2024). Uma pulseira desconfortável pode ser, ela mesma, um gatilho de estresse. Material, peso, fecho e ausência de vibração ou som são requisitos de projeto.
- **Estigma.** Um dispositivo visível só em alguns alunos pode expô-los diante dos colegas. O alerta vai para o celular do professor, e não para a pulseira, para não chamar atenção.
- **Excesso de alarmes e falsa segurança.** Alarmes falsos frequentes fazem o professor ignorar a pulseira. Já a ausência de alerta não garante que o aluno está bem, porque o modelo erra. O professor continua sendo o responsável pela observação, e a pulseira é só um apoio.
- **Não é diagnóstico.** O sistema estima um estado momentâneo e não diagnostica nada. Se a finalidade declarada fosse médica, o produto poderia ser enquadrado como dispositivo médico e precisaria de regularização na Anvisa.
- **Participação das pessoas autistas.** O desenho de uma versão real deveria envolver pessoas autistas, famílias e professores desde o início, como fez o protocolo STREAM (GERNERT et al., 2024).
- **Pesquisa com seres humanos.** Qualquer teste com alunos precisa de aprovação de um Comitê de Ética em Pesquisa (CONSELHO NACIONAL DE SAÚDE, 2012).

## 5.5 Lições aprendidas

**Sobre dados**
- **Conferir os dados antes de confiar neles.** O segundo dataset parecia pronto para a validação externa, mas um teste simples (a frequência cardíaca sobe no "estresse"?) mostrou rótulos deslocados e incompletos (Seção 4.7). Sem essa checagem, o trabalho teria medido um erro de rotulagem.
- **Ter um plano B (e C).** O dataset de TEA não chegou a tempo, e o de enfermeiras foi descartado. Reformular a pergunta central para algo que os dados disponíveis respondem bem (a comparação de sensores) foi melhor do que forçar a pergunta original.

**Sobre modelagem**
- **Reproduzir o resultado de referência antes de inovar.** Chegar perto do F1 de Schmidt et al. (2018) nas mesmas condições deu confiança de que o pré-processamento estava correto. Só depois disso a calibração por pessoa foi acrescentada.
- **Avaliar como o sistema será usado.** A validação deixando uma pessoa de fora simula um aluno novo. Uma validação que misturasse janelas da mesma pessoa no treino e no teste daria números mais altos e enganosos.
- **A pessoa é a referência de si mesma.** A calibração por pessoa foi a decisão de maior impacto do trabalho, e a mais barata.
- **Métrica certa para o problema.** A acurácia de um classificador que sempre responde "não estresse" é 66%. O F1 macro, a latência e os alarmes falsos dizem muito mais sobre a utilidade para o professor.

**Sobre IoT**
- **O que funciona no notebook pode mudar em tempo real.** Calcular os indicadores só com o passado, em janelas curtas, mudou os de frequência cardíaca. A equivalência precisa ser medida, não suposta (Seção 3.3).
- **Os erros mais difíceis aparecem na integração.** A assinatura perdida após reconexão, as janelas que misturavam trechos e o episódio "fantasma" no painel só apareceram ao rodar todos os componentes juntos (Seção 3.8).
- **Desacoplar pelo broker.** Como cada componente só conversa pelo MQTT, foi possível construir e testar cada parte separadamente, e a pulseira virtual pode ser trocada pela física sem mudar o resto.
- **Honestidade na demonstração.** Usar na demo um modelo que já viu os participantes reproduzidos daria um resultado bonito e falso. Treinar um modelo sem eles torna a demonstração um teste de verdade.

## 5.6 Trabalhos futuros

1. **Validar com pessoas com TEA**, com aprovação ética e um protocolo de rotulagem por observação direta, como em Goodwin et al. (2019). O dataset de crianças com TEA do IEEE DataPort, se for obtido, é o primeiro passo.
2. **Construir a pulseira física** (ESP32, sensor óptico de pulso, GSR, sensor de temperatura e acelerômetro) e medir quanto o ruído dos sensores baratos afeta os resultados deste trabalho.
3. **Prever, e não só detectar.** Treinar modelos que antecipem a crise, como em Imbiriba et al. (2023), o que exige dados com o momento das crises anotado.
4. **Personalizar o modelo.** Além da calibração, ajustar o modelo a cada aluno com o uso, já que modelos personalizados tiveram melhor desempenho em jovens com TEA (GOODWIN et al., 2019).
5. **Usar o movimento como contexto**, para distinguir agitação física (educação física, recreio) de estresse e reduzir os alertas depois do esforço.
6. **Tratar a recuperação.** Ajustar a regra de alerta para não repetir alertas enquanto a condutância da pele volta ao nível de base.
7. **Avaliar com professores** a utilidade do painel e das mensagens, incluindo a função de horários de maior agitação.

---

## Referências citadas nesta seção

BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). *Diário Oficial da União*, Brasília, DF, 15 ago. 2018.

CONSELHO NACIONAL DE SAÚDE (Brasil). Resolução nº 466, de 12 de dezembro de 2012. Aprova diretrizes e normas regulamentadoras de pesquisas envolvendo seres humanos. *Diário Oficial da União*, Brasília, DF, 13 jun. 2013.

GERNERT, C. C. et al. Stress in autism (STREAM): a study protocol on the role of circadian activity, sleep quality and sensory reactivity. *PLoS ONE*, v. 19, n. 5, e0303209, 2024. DOI: 10.1371/journal.pone.0303209.

GOODWIN, M. S. et al. Predicting aggression to others in youth with autism using a wearable biosensor. *Autism Research*, v. 12, n. 8, p. 1286-1296, 2019. DOI: 10.1002/aur.2151.

IMBIRIBA, T. et al. Wearable biosensing to predict imminent aggressive behavior in psychiatric inpatient youths with autism. *JAMA Network Open*, v. 6, n. 12, e2348898, 2023. DOI: 10.1001/jamanetworkopen.2023.48898.

MONTEIRO, K. R. *Desenvolvimento de sistema para monitorar crises nervosas autistas por meio de sinais fisiológicos*. 2022. 105 f. Dissertação (Mestrado em Engenharia Biomédica) – Faculdade UnB Gama, Universidade de Brasília, Brasília, 2022.

SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: INTERNATIONAL CONFERENCE ON MULTIMODAL INTERACTION, 20., 2018, Boulder. *Proceedings* [...]. New York: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.

SHAHEEN, B.; DARABEE, R. *AutiSense*: smart assistant system for children with autism spectrum disorder. 2026. Trabalho de Conclusão de Curso (Bacharelado em Engenharia de Sistemas Computacionais) – Palestine Polytechnic University, Hebron, 2026.

SIIRTOLA, P. Continuous stress detection using the sensors of commercial smartwatch. In: ACM INTERNATIONAL JOINT CONFERENCE ON PERVASIVE AND UBIQUITOUS COMPUTING; INTERNATIONAL SYMPOSIUM ON WEARABLE COMPUTERS, 2019, London. *Adjunct Proceedings* [...]. New York: ACM, 2019. DOI: 10.1145/3341162.3344831.

TERTO, D. C. V.; SILVA, L. S.; SANTOS, A. *Pulseira indicadora de desregulação em autistas*. Pôster apresentado na Feira Brasileira de Ciências e Engenharia (FEBRACE), São Paulo, 2023.
