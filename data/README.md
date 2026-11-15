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
- **Uso no projeto:** a parte `NURSE` é a **validação externa** do experimento central (plano B): o modelo treinado no WESAD com `HR`, `TEMP` e movimento é testado nela. As linhas `WESAD_*` não são usadas, porque o WESAD bruto é mais completo
- **A confirmar:** o significado dos rótulos 1 e 2 e o tratamento dos `timestamp_unix` duplicados
- **Fonte:** https://huggingface.co/datasets/evannh/wearable-and-stress
- **Destino:** `data/raw/hf_wearable_stress/`

## 3. Children with Autism: Heart Rate as a Predictor of Challenging Behaviours

- **Conteúdo:** 5 crianças com TEA com pulseira (ACC, EDA, TEMP, HR, BVP), sessões rotuladas como *Challenging* ou *Non-Challenging*
- **Fonte:** https://ieee-dataport.org/documents/dataset-heart-rate-predictor-challenging-behaviours-among-children-autism-wearable
- **DOI:** 10.21227/5b7r-8j60
- **Observação:** pode exigir cadastro no IEEE DataPort. O download é manual.
- **Situação (15/11/2026):** **não obtido**, porque o acesso não foi liberado a tempo. O projeto segue o plano B (ver o cronograma em `docs/`), e a pasta `ieee_tea/` fica vazia.
- **Destino:** `data/raw/ieee_tea/`

## Verificação

Depois dos downloads manuais, rode `python -m src.data.download`: o script baixa o wearable-and-stress e confere o WESAD e o dataset de TEA.

## Estrutura esperada

```
data/
├── raw/
│   ├── WESAD/            # S2/ ... S17/, cada um com SX.pkl e SX_E4_Data.zip
│   ├── hf_wearable_stress/
│   └── ieee_tea/         # vazio (plano B)
└── processed/
    ├── features_wesad.csv
    └── features_nurse.csv
```
