# DataBank-Macro

> Inteligência de Mercado para PMEs
> TRL 3+ — Prova de conceito com dados reais validados

---

## Visão Geral

O DataBank-Macro é um dashboard open source que cataloga 49 vetores econômicos em 6 campos granulares, com 17 vetores reais operacionais via APIs gratuitas.

**TRL 3+** significa: o código existe, roda, e demonstra a ideia com dados reais. Não é mais protótipo de papel. Mas também não é um produto final.

---

## O que funciona hoje

| Componente | Descrição | Status |
|---|---|---|
| Dashboard Streamlit | App funcional com upload CSV/Excel/JSON e visualização | ✅ Funcional |
| APIs Reais | NASA GISS, BCB, Yahoo Finance, CoinGecko, World Bank | ✅ 17 vetores |
| Cache SQLite | Dados persistentes com timestamp e audit trail | ✅ Funcional |
| Detector CUSUM | Detecção de regimes em séries temporais reais | ✅ Funcional |
| Catálogo de 49 Vetores | 6 campos com nomes, fontes, pesos e sensibilidades | ✅ Estruturado |
| Data Generator | Geração de séries simuladas para testes | ✅ Apenas em tests/ |

**17 vetores com dados reais** | **32 vetores com estrutura catalogada, aguardando fontes**

---

## 6 Campos Granulares

| Campo | Vetores | Reais / Total | Fontes |
|---|---|---|---|
| Clima | 6 | 2/6 | NASA GISS |
| Infraestrutura | 7 | 2/7 | Yahoo Finance |
| Chips | 8 | 0/8 | — |
| Terras Raras | 18 | 7/18 | Yahoo Finance |
| Carbono | 5 | 5/5 | KraneShares, World Bank |
| Geopolítica | 5 | 1/5 | Yahoo Finance |

---

## Estrutura do Projeto

```
DataBank-Macro/
├── run_local.py              # Script demo end-to-end
├── streamlit_app.py          # Dashboard
├── src/
│   ├── core/
│   │   ├── campos_granulares.py   # Taxonomia de 49 vetores
│   │   ├── vetor.py               # Estrutura e cálculos básicos
│   │   ├── inflex.py              # Detector CUSUM
│   │   ├── anamorf.py             # Features e correlação
│   │   └── fluxus.py              # Orquestração
│   ├── ingestion/
│   │   ├── real_data.py           # Conectores de APIs reais
│   │   └── cache.py               # Cache SQLite
│   ├── pcq/
│   │   └── custodia.py            # Estrutura de criptografia (experimental)
│   └── mining/
│       └── pcq_miner.py           # Ranking estático de risco
├── tests/
│   └── test_fusion.py             # 11 testes de estrutura
└── docs/
    └── index.html                 # Site GitHub Pages
```

**Stats:** 1.500 linhas | 18 arquivos Python | 11 testes | 0 simulações em produção

---

## Roadmap

### TRL 4 — Validação em ambiente controlado
- [ ] Ingestão real dos 32 vetores pendentes
- [ ] Integrar Streamlit com `src/core/` (fórmulas ad-hoc → engine real)
- [ ] Backtest e métricas de acurácia ao CUSUM

### TRL 5+ — Produto
- [ ] Pipeline ETL com scheduler
- [ ] APIs REST para consumo externo
- [ ] Relatórios setoriais automatizados

---

## Como executar

```bash
pip install -r requirements.txt
python run_local.py
streamlit run streamlit_app.py
pytest tests/ -v
```

---

## Segurança

⚠️ A criptografia em `src/pcq/` é experimental. Não é um produto de segurança comercial.

---

## Licença

- **Código:** Apache 2.0
- **Modelo de negócio, marca, visão estratégica:** Direitos autorais reservados ao autor

---

## Autor

**Guilherme Gonçalves Machado** — Hubstry Deep Tech — 2026
