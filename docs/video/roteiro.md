# Roteiro: Vídeo Pitch & Demo (até 5 min)

Duração prevista: cerca de 4min40s. A demo ocupa cerca de 40% do tempo.

**Ideia central do vídeo:** *"A crise não vem do nada. O corpo avisa antes, e a professora pode ficar sabendo."*

## Cena 1: Gancho (0:00 a 0:20)

**Tela:** capa da apresentação, com você falando para a câmera ou em off.

> "Imagine uma sala de aula com trinta alunos e uma professora. Um deles começa a ficar agitado, mas não consegue dizer o que sente, e ninguém percebe até a crise acontecer. Hoje, na maioria das escolas, ninguém recebe um aviso antes disso. Eu sou a Leticia, e este é o projeto Pulseira Inteligente para Alunos com TEA."

## Cena 2: O problema (0:20 a 0:55)

**Tela:** 2 ou 3 slides simples, cada um com um número grande.

> "Em 2025, o Brasil tinha 1,3 milhão de matrículas de estudantes com autismo. Só 31,7% das escolas com alunos da educação especial em turmas comuns tinham profissional de apoio. Então quem precisa perceber os sinais costuma ser uma professora sozinha, com a turma inteira.
>
> Muitos desses alunos têm dificuldade de dizer como estão, e a crise parece surgir do nada. Só que a pesquisa mostra que sinais medidos no pulso conseguem prever uma crise de 1 a 3 minutos antes. O problema é que esses estudos usaram uma pulseira de pesquisa cara, que já foi descontinuada, e foram feitos em hospital."

## Cena 3: A solução (0:55 a 1:35)

**Tela:** [arquitetura.png](../arquitetura/arquitetura.png), com zoom em cada camada enquanto você fala.

> "A minha proposta é uma pulseira de baixo custo com um ESP32, um sensor de pulso, um sensor de condutância da pele, temperatura e acelerômetro. A cada segundo, ela envia os sinais por MQTT para um serviço que roda na própria rede da escola. Esse serviço calcula 18 indicadores a cada 30 segundos e uma Random Forest estima a probabilidade de estresse. O modelo é calibrado nos primeiros 5 minutos de repouso de cada aluno. Quando duas janelas seguidas passam de 50%, a professora recebe um alerta no Telegram e acompanha tudo em um painel.
>
> Um ponto importante: isto é uma prova de conceito. A pulseira é virtual e reproduz sinais reais do dataset público WESAD, no mesmo formato de mensagem que a pulseira física enviaria."

## Cena 4: Demo ao vivo (1:35 a 3:35), a parte principal

**Tela:** gravação de tela com os terminais à esquerda e o painel à direita. Se puder, mostre o celular em um canto (com a câmera ou espelhando a tela).

| Tempo | O que aparece | Narração (resumida) |
|---|---|---|
| 1:35 | `docker compose up`, serviço de inferência, `telegram_alert`, `streamlit` (sobem rápido, pode acelerar na edição) | "Primeiro subo o broker MQTT, o serviço de inferência, o bot de alertas e o painel da professora." |
| 1:50 | Rodar `virtual_wristband --aluno aluno02 --velocidade 20 --curta` e o aluno03 | "Agora coloco a pulseira em dois alunos. Cada um é um participante do WESAD que o modelo **nunca viu** no treino." |
| 2:00 | Cartões mostrando "calibrando" | "Nos primeiros 5 minutos, a pulseira aprende como é o repouso daquele aluno." |
| 2:15 | Probabilidade baixa, cartão verde. Abrir a aba "Sinais ao vivo" | "Aqui a professora também confere se a pulseira está bem colocada." |
| 2:35 | Começa o teste de estresse, a probabilidade sobe e o cartão fica **vermelho** | "Agora começa o teste de estresse do protocolo. A probabilidade passa de 50% duas vezes seguidas e…" |
| 2:50 | 🔔 alerta no celular, em close | "…o alerta chega com o pseudônimo do aluno e uma sugestão de ação. O nome real do aluno não aparece." |
| 3:05 | Marcar "Mostrar a condição do WESAD" e abrir a aba de agitação ao longo da sessão | "Comparando com a fase real do protocolo, a estimativa acompanha o estresse de verdade." |
| 3:20 | Abas "Alertas" e "Horários de maior agitação" | "Com o tempo, a professora vê em que horários a turma fica mais agitada e pode planejar a rotina." |

## Cena 5: Resultados (3:35 a 4:15)

**Tela:** a tabela da Seção 4 do README, com a linha "Baixo custo + EDA" destacada.

> "A pergunta central do trabalho era: quanto desempenho se perde ao trocar a pulseira de pesquisa por sensores baratos? Testando sempre em uma pessoa que o modelo nunca viu, com sensor de pulso e GSR, chegamos a F1 de 0,95 e AUROC de 0,99, com 2,8% de alarmes falsos. Ou seja, quase não há perda. A decisão que mais fez diferença foi a calibração individual: o F1 subiu de 0,88 para 0,95. Na demo de ponta a ponta, o estresse foi detectado nos três alunos."

## Cena 6: Limites, ética e fechamento (4:15 a 4:40)

**Tela:** você falando para a câmera, ou um slide com 3 tópicos.

> "Este projeto não faz diagnóstico, e ainda não foi validado com crianças com TEA. Esse é o próximo passo, com comitê de ética e a pulseira física montada. Os dados ficam na rede da escola e os alunos aparecem só por pseudônimo.
>
> A ideia é simples: dar à professora alguns minutos de vantagem. Às vezes, dois minutos bastam para evitar uma crise."

**Tela final:** nome do projeto, link do GitHub, disciplina e Unisinos 2026.

---

## Dicas para a gravação

- **Grave a demo separada da narração** e encaixe a voz depois. Assim você pode acelerar as esperas na edição, colocando um selo "⏩ 4x" na tela para ficar claro que foi acelerado.
- **Antes de gravar:** apague os arquivos `data/demo/*.csv` para o painel começar vazio, confira o token do Telegram no `.env` (`python -m src.iot.telegram_alert --teste`) e aumente a fonte dos terminais.
- O `--curta --velocidade 20` dura ~1,5 min por aluno, o que encaixa bem nos 2 minutos da demo.
- Narração a ~140 palavras/min: o texto tem por volta de 550 palavras, então sobra tempo para pausas.
- Aproveite a gravação para fazer as capturas que faltam na Seção 3 do relatório (Figura 3.1, alerta no celular, e Figuras 3.2 a 3.5, painel).
