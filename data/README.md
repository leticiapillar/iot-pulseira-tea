# Dados

Os dados brutos **não são versionados** no git, por causa do tamanho e das licenças de uso. Baixe-os em `data/raw/` seguindo as instruções abaixo.

## 1. WESAD (Wearable Stress and Affect Detection)

- **Conteúdo:** 15 participantes com pulseira Empatica E4 (sinais BVP, EDA, TEMP, ACC) e sensor de peito (RespiBAN). Condições rotuladas: neutro, estresse e diversão.
- **Fonte:** UCI Machine Learning Repository
- **Licença:** uso acadêmico e não comercial
- **Destino:** `data/raw/wesad/`

## 2. wearable-and-stress (Hugging Face)

- **Conteúdo:** versão do WESAD agregada por minuto (`HR_mean`, `TEMP_mean`, `MOTION_intensity`, `label`)
- **Fonte:** https://huggingface.co/datasets/evannh/wearable-and-stress
- **Destino:** `data/raw/hf_wearable_stress/`

## 3. Children with Autism: Heart Rate as a Predictor of Challenging Behaviours

- **Conteúdo:** 5 crianças com TEA com pulseira (ACC, EDA, TEMP, HR, BVP), sessões rotuladas como *Challenging* ou *Non-Challenging*
- **Fonte:** https://ieee-dataport.org/documents/dataset-heart-rate-predictor-challenging-behaviours-among-children-autism-wearable
- **DOI:** 10.21227/5b7r-8j60
- **Observação:** pode exigir cadastro no IEEE DataPort. O download é manual.
- **Destino:** `data/raw/ieee_tea/`

## Estrutura esperada

```
data/
├── raw/
│   ├── wesad/
│   ├── hf_wearable_stress/
│   └── ieee_tea/
└── processed/
    ├── features_wesad.csv
    └── features_tea.csv
```
