# DataBank PCQ v3 -- Fusion Edition

**Post-Quantum Custody | Harvest Now, Decrypt Later | Economia Glocal | Soberania Tecnologica**

[Site GitHub Pages](https://guilherme-machado-ceo.github.io/DataBank-Fintech/) | [Repositorio](https://github.com/guilherme-machado-ceo/DataBank-Fintech)

---

## Visao

O DataBank PCQ e a primeira instituicao brasileira de **custodia, valuation e monetizacao de dados empresariais** operando sob o paradigma **Harvest Now, Decrypt Later (HNDL)**.

- **Harvest**: Coleta dados valiosos de 41 vetores economicos glocais via APIs reais (BCB, Yahoo Finance, CoinGecko, Open-Meteo)
- **Encrypt**: Protege com criptografia pos-quantica (Kyber1024 + Dilithium5)
- **Store**: Custodia em cold storage air-gapped + blockchain de registro
- **Decrypt Later**: Decifracao no Q-Day para analise quantica avancada
- **Monetize**: Tokenizacao DREX, credito informacional, marketplace de dados

> "O DataBank nao e apenas uma fintech. E uma instituicao de soberania tecnologica e informacional do Brasil."
> -- Guilherme Goncalves Machado, Hubstry Deep Tech

---

## Arquitetura de 6 Camadas

**CAMADA 6 -- Monetizacao**: Tokenizacao DREX, Credito Informacional (Score PCQ), Marketplace de Dados Pos-Quanticos, Liquidacao via PIX + Smart Contracts

**CAMADA 5 -- Inteligencia e Valuation**: INFLEx (deteccao de inflexoes via CUSUM + Hilbert), ANAMORF (analogia semiotica via PCA + KNN), FLUXUS (ciclo de valorizacao continua), IA Simbolica + IA Generativa (Hubstry Core), Predictive Analytics Quantico (pre-Q-Day)

**CAMADA 4 -- Custodia PCQ (HNDL)**: Criptografia Hibrida RSA-4096 + CRYSTALS-Kyber1024, Assinaturas ECDSA-P384 + CRYSTALS-Dilithium5, AES-256-GCM para dados em repouso, Cold Storage Air-Gapped + Multi-Sig, Blockchain de Registro (prova de existencia)

**CAMADA 3 -- Governanca e Compliance**: Scanner ECA Digital (8 Pilares + Pilar 9 PCQ), LGPD / GDPR / CCPA Compliance, Consentimento Granular e Revogavel, Pseudonimizacao e Anonimizacao, Auditoria Continua (Hubstry Compliance)

**CAMADA 2 -- Ingestao e ETL**: Open Finance APIs (Bacen), Alpha Vantage (Forex, Commodities, Indices), Open-Meteo (Dados Climaticos), Web Scraping Geopolitico + IoT, ETL com Pseudonimizacao Automatica

**CAMADA 1 -- Vetores Economicos Glocal (41 vetores)**:
- CAMPO I -- Climaticos: 6 vetores (temperatura, eventos extremos, transicao energetica, minerais renovaveis, carbono EU, capacidade renovavel)
- CAMPO II -- Infraestrutura: 7 vetores (data centers, cobre, aluminio, 5G, fibra otica, infra digital)
- CAMPO III -- Chips e Semicondutores: 8 vetores (galio, germanio, GPUs, controle exportacao China, fabs, lead time)
- CAMPO IV -- Terras Raras + Desdolarizacao + Classicos: 20 vetores (REEs, yuan, BRICS, USD/BRL, DXY, ouro, brent, BTC, risco geopolitico, litio, cobre, OPEC)

---

## APIs Reais Utilizadas (Gratuitas)

| API | Dados | Limite | Key |
|-----|-------|--------|-----|
| BCB (Banco Central BR) | USD/BRL, SELIC | Ilimitado | Nao |
| Yahoo Finance (yfinance) | Acoes, commodities, indices | Ilimitado | Nao |
| CoinGecko | BTC, ETH, crypto | 10-50 calls/min | Nao |
| Open-Meteo | Clima global | Ilimitado | Nao |
| Alpha Vantage | Forex, commodities | 25/dia | Sim (gratis) |
| FRED | Dados economicos EUA | 120/dia | Sim (gratis) |

---

## Os 3 Algoritmos Semioticos

**INFLEx** -- Inflexao de Vetores Economicos: detecta pontos de inflexao (regime changes) via CUSUM (Cumulative Sum) para mudanca de regime, Transformada de Hilbert para extracao de fase, thresholds por campo (sensibilidade granular), cascata entre campos (MAPA_CASCATA), modelo Bayesiano para probabilidade final.

**ANAMORF** -- Anamorfose Semiotica de Dados: cria embedding latente onde proximidade reflete homologia estrutural. Tres tipos de analogia: HEURISTICA (correlacao estatistica), FUNCIONAL (mesma funcao economica), HOMOLOGIA (estrutura similar). Operacao: A esta para B assim como C esta para ?

**FLUXUS** -- Fluxo Continuo de Valorizacao: ciclo de auto-reforco em 5 fases (Pesquisa, Estudo, Criacao, Ensino, Producao Economica).

---

## Criptografia Pos-Quantica (PCQ-HNDL)

| Componente | Algoritmo | Status |
|------------|-----------|--------|
| Cifra simetrica | AES-256-GCM | Ativo |
| Encapsulamento (classico) | RSA-4096-OAEP | Ativo |
| Assinatura (classico) | ECDSA-P384 | Ativo |
| Encapsulamento (PQC) | CRYSTALS-Kyber1024 | Se liboqs-python instalado |
| Assinatura (PQC) | CRYSTALS-Dilithium5 | Se liboqs-python instalado |
| Validade por sensibilidade | 5-30 anos | Ativo |
| Cold Storage | Air-gapped + Multi-Sig | Ativo |
| Blockchain Registry | Prova de existencia | Ativo |

---

## Instalacao

```bash
# Clone
git clone https://github.com/guilherme-machado-ceo/DataBank-Fintech.git
cd DataBank-Fintech

# Instale dependencias
pip3 install --break-system-packages -r requirements.txt

# Instale yfinance (dados reais Yahoo Finance)
pip3 install --break-system-packages yfinance

# Opcional: ativar PQC real
pip3 install --break-system-packages liboqs-python

# Rode com dados REAIS
python3 run_local.py

# Testes
python3 -m pytest tests/test_fusion.py -v
```

---

## Uso

### Rodar o Motor com Dados Reais

```bash
python3 run_local.py
```

Output: coleta USD/BRL do BCB, commodities do Yahoo Finance, crypto do CoinGecko, clima do Open-Meteo, executa INFLEx + ANAMORF + FLUXUS, gera ativos, protege com PCQ.

### Dashboard Streamlit

```bash
streamlit run src/dashboard/streamlit_app.py
```

---

## Testes

```bash
python3 -m pytest tests/test_fusion.py -v
```

- test_41_vetores_4_campos: confirma 41 vetores em 4 campos
- test_sensibilidade_por_campo: thresholds adaptativos
- test_inflexao_detecta: INFLEx detecta inflexoes
- test_anamorf_operar: ANAMORF gera analogias
- test_fluxus_ciclo: FLUXUS executa ciclo completo
- test_custodia_proteger: PCQ protege dados com HNDL
- test_miner_5_chains: PCQMiner avalia 5 blockchains
- test_miner_qrl_menor_risco: QRL tem risco quantico zero
- test_dados_para_vetores: converte dados em vetores tensoriais

---

## Mineracao PCQ

O PCQMiner avalia 5 blockchains pelo risco pos-quantico:

| # | Chain | Algoritmo | Risco Q | Recomendacao |
|---|-------|-----------|---------|--------------|
| 1 | QRL | XMSS | 0.00 | Minerar |
| 2 | Algorand | EdDSA+FALCON | 0.30 | Minerar |
| 3 | Solana | EdDSA | 0.65 | Monitorar |
| 4 | Ethereum | ECDSA | 0.70 | Monitorar |
| 5 | Bitcoin | ECDSA | 0.75 | Minerar com precaucao |

---

## Site

[guilherme-machado-ceo.github.io/DataBank-Fintech](https://guilherme-machado-ceo.github.io/DataBank-Fintech/)

---

## Axioma Autoral

> "Inflexao do pensamento humano incidindo sobre o conjunto universo dos fenomenos, instanciando-se em paralelo ou serie em multiplas areas do conhecimento, em comparacao e contraste sistematicos operada pela analogia (heuristica, funcional ou homologia), em um fluxo continuo de pesquisa, estudo, criacao, ensino e producao economica."
> -- Guilherme Goncalves Machado

---

## Hubstry Deep Tech

Hubstry Deep Tech -- Deep Tech R&D Lab
- Web: [hubstry.dev](https://www.hubstry.dev)
- Email: guilhermemachado@hubstry.onmicrosoft.com
- LinkedIn: [guilhermegoncalvesmachado](https://www.linkedin.com/in/guilhermegoncalvesmachado)
- GitHub: [guilherme-machado-ceo](https://github.com/guilherme-machado-ceo)

---

## Licenca

Apache 2.0 -- Codigo aberto. Propriedade intelectual de Guilherme Goncalves Machado.

Copyright 2026 Guilherme Goncalves Machado / Hubstry Deep Tech
