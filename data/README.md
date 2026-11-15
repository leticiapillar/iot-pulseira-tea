# Dados

Os dados brutos **não são versionados** no git, por causa do tamanho e das licenças de uso. Baixe-os em `data/raw/` seguindo as instruções abaixo.

## 1. WESAD (Wearable Stress and Affect Detection)

- **Conteúdo:** 15 participantes (S2 a S17, sem o S12) com pulseira Empatica E4 (sinais BVP, EDA, TEMP, ACC) e sensor de peito (RespiBAN). Condições rotuladas: neutro, estresse e diversão.
- **Fonte oficial:** https://ubi29.informatik.uni-siegen.de/usi/data_wesad.html (download manual do `WESAD.zip`, cerca de 2 GB compactado e 17 GB extraído)
- **Licença:** uso acadêmico e não comercial, com citação obrigatória
- **Citação:** SCHMIDT, P. et al. Introducing WESAD, a multimodal dataset for wearable stress and affect detection. In: *Proceedings of the 20th ACM International Conference on Multimodal Interaction (ICMI '18)*. Boulder: ACM, 2018. p. 400-408. DOI: 10.1145/3242969.3242985.
- **Destino:** extrair o zip em `data/raw/`, gerando `data/raw/WESAD/S2/S2.pkl` etc.

## 2. wearable-and-stress (Hugging Face)

- **Conteúdo:** indicadores agregados (`HR_mean`, `TEMP_mean`, `MOTION_intensity`, `label` 1 ou 2) de duas fontes. A maior parte vem do dataset de enfermeiras (`NURSE_*`: 15 pessoas, cerca de 10,7 milhões de linhas). Do WESAD há só 406 linhas (`WESAD_*`: 14 pessoas, uma linha por minuto)
- **Uso no projeto:** **nenhum para medir desempenho** (plano C, decidido em 15/11/2026). A checagem abaixo mostrou que os rótulos não são confiáveis. O dataset aparece no relatório só na Análise e nas Limitações
- **Checagem de 15/11/2026:**
  - **Sem documentação.** O repositório no Hugging Face não tem README nem descrição das colunas. O único arquivo publicado se chama `DATASET_SAMSUNG_WATCH.csv`, mas os dados são de pulseiras Empatica E4.
  - **Parte `WESAD_*`: rótulos deslocados.** Os valores batem exatamente com os arquivos brutos do E4 (`SX_E4_Data.zip`). Os rótulos, porém, foram montados aplicando os tempos do `SX_quest.csv` (contados a partir do sensor de peito) ao início do E4 bruto, que começa de 16 a 26 min antes. Resultado: nos 14 participantes, o "estresse" (rótulo 2) cai em baseline, meditação ou transições entre condições no `.pkl` oficial, e em nenhum caso no estresse, e o "baseline" (rótulo 1) cai antes do protocolo.
  - **Parte `NURSE_*`: rótulos sem significado claro.** No estudo original (HOSSEINI et al., 2022), as enfermeiras rotularam (0, 1 ou 2 = sem, médio e alto estresse) apenas eventos já detectados por um modelo de estresse. Os períodos sem estresse nunca foram confirmados. O arquivo do HF só tem os rótulos 1 e 2, sem dizer como foram convertidos. O rótulo 2 cobre 80% do tempo, e duas enfermeiras (CE, EG) têm 100% de rótulo 2.
  - **Teste de sanidade:** a frequência cardíaca é maior no rótulo 2 do que no rótulo 1 em só **6 de 13** enfermeiras com os dois rótulos (no WESAD oficial, sobe no estresse em 15 de 15). O movimento também não separa os rótulos (7 de 13).
  - **Estrutura:** 32 linhas por segundo (uma por amostra do acelerômetro, 32 Hz). `HR_mean` e `TEMP_mean` se repetem dentro de cada segundo, e `MOTION_intensity` é a magnitude da aceleração de cada amostra, em g. Por isso os `timestamp_unix` se repetem. São cerca de 92 h de dados, só em torno dos eventos detectados.
  - **Referência do estudo original:** HOSSEINI, S. et al. A multimodal sensor dataset for continuous stress detection of nurses in a hospital. *Scientific Data*, v. 9, 255, 2022. DOI: 10.1038/s41597-022-01361-y.
- **Fonte:** https://huggingface.co/datasets/evannh/wearable-and-stress
- **Destino:** `data/raw/hf_wearable_stress/`

## 3. Children with Autism: Heart Rate as a Predictor of Challenging Behaviours

- **Conteúdo:** 5 crianças com TEA com pulseira (ACC, EDA, TEMP, HR, BVP), sessões rotuladas como *Challenging* ou *Non-Challenging*
- **Fonte:** https://ieee-dataport.org/documents/dataset-heart-rate-predictor-challenging-behaviours-among-children-autism-wearable
- **DOI:** 10.21227/5b7r-8j60
- **Observação:** pode exigir cadastro no IEEE DataPort. O download é manual.
- **Situação (15/11/2026):** **não obtido**, porque o acesso não foi liberado a tempo. O projeto seguiu para o plano B e depois para o plano C (ver o cronograma em `docs/`), e a pasta `ieee_tea/` fica vazia.
- **Destino:** `data/raw/ieee_tea/`

## Verificação

Depois dos downloads manuais, rode `python -m src.data.download`: o script baixa o wearable-and-stress e confere o WESAD e o dataset de TEA.

## Estrutura esperada

```
data/
├── raw/
│   ├── WESAD/            # S2/ ... S17/, cada um com SX.pkl e SX_E4_Data.zip
│   ├── hf_wearable_stress/
│   └── ieee_tea/         # vazio (não obtido)
└── processed/
    ├── wesad_wrist/       # cache dos sinais de pulso (src/data/wesad.py)
    └── features_wesad.csv
```
