# README atualizado com acentos e estado real

Cole este bloco inteiro no editor do GitHub (lápis ✏️):

```markdown
# DataBank-Fintech

A Primeira Infraestrutura Financeira Pós-Quântica de Dados do Brasil.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Tests](https://img.shields.io/badge/Tests-Pytest-green)
![PQC](https://img.shields.io/badge/Security-PQC-00d4aa)
![NIST](https://img.shields.io/badge/NIST-FIPS_203/204/205-e8c547)
![License](https://img.shields.io/badge/License-Apache_2.0-green)
![Status](https://img.shields.io/badge/Status-MVP-yellow)
![Vetores](https://img.shields.io/badge/Vetores-41-ff6b6b)
![Campos](https://img.shields.io/badge/Campos_Granulares-4-9b59b6)

Transformando dados empresariais em ativos financeiros com segurança pós-quântica nativa, motor de inferência analógica e monitoramento de 41 vetores econômicos em tempo real.

---

## Visão Geral

O DataBank é uma fintech brasileira que trata dados como ativos financeiros estruturados. A plataforma oferece custódia, valuation, monetização, tokenização e crédito informacional — protegidos contra ameaças quânticas presentes e futuras.

O motor computacional é derivado de um axioma autoral sobre inflexão do pensamento humano aplicado à economia global.

---

## Pilares

| Pilar | Descrição | Status |
|-------|-----------|--------|
| Custódia PQC | Armazenamento com criptografia pós-quântica nativa | Implementado |
| Valuation | Score proprietário em 6 dimensões (π-Radical) | Implementado |
| Monetização | Tokenização de ativos com smart contracts | Em desenvolvimento |
| Crédito Informacional | Crédito lastreado em dados | Em desenvolvimento |

---

## Motor de Inferência Analógica

Arquitetura computacional executável derivada do axioma autoral:

> Inflecting human thought over the universe of phenomena, instantiating in parallel or series across multiple domains of knowledge, through systematic comparison and contrast operated by analogy (heuristic, functional, or homology), in a continuous flow of research, study, creation, teaching and economic production.

### Módulos implementados

| Módulo | Arquivo | Função |
|--------|---------|--------|
| Detecção de Inflexões | `src/core/inflexao.py` | Identifica mudanças de regime em séries temporais |
| 4 Campos Granulares | `src/core/campos_granulares.py` | 41 vetores em 4 domínios econômicos |
| Motor de Analogia | `src/core/analogia.py` | 3 tipos: heurística, funcional, homologia |
| Fluxo Contínuo | `src/core/fluxo_continuo.py` | Loop perpétuo de 5 fases |
| Gerador de Dados | `src/core/data_generator.py` | Dados simulados com correlações |
| Proteção HNDL | `src/pcq/harvest_guard.py` | Harvest Now Decrypt Later guard |
| Minerador PCQ | `src/mining/pcq_miner.py` | Avaliação quântica de blockchains |

### Ciclo de 5 fases

1. Pesquisa — Coleta de dados de todas as fontes
2. Estudo — Detecção de inflexões + operação de analogias
3. Criação — Geração de insights e oportunidades
4. Ensino — Documentação de padrões aprendidos
5. Produção Econômica — Ações concretas (mineração, hedge, alertas, re-criptografia)

---

## 4 Campos Granulares e 41 Vetores

### Campo 1: Eventos Climáticos (6 vetores)
Temperatura global, eventos extremos, transição energética, demanda minerais renováveis, preço carbono, capacidade renovável.

### Campo 2: Infraestrutura (7 vetores)
Data centers, demanda cobre, demanda alumínio, expansão 5G, fibra óptica, índice infraestrutura digital.

### Campo 3: Chips e Semicondutores (8 vetores)
Gálio, germânio, GPUs, controle exportação China, investimento fabs, lead time chips.

### Campo 4: Terras Raras e Desdolarização (20 vetores)
REEs, neodímio, disprósio, reservas Brasil, dólar reservas globais, comércio não-USD, yuan petróleo, BRICS, câmbio, ouro, petróleo, risco geopolítico, Bitcoin, conflitos, lítio, cobre.

---

## Segurança Pós-Quântica

Proteção contra ataques "Harvest Now, Decrypt Later" (HNDL) usando algoritmos aprovados pelo NIST:

| Função | Algoritmo | Padrão | Base Matemática |
|--------|-----------|--------|-----------------|
| Encapsulamento de chaves | ML-KEM-768 | FIPS 203 | Reticulados |
| Assinatura digital | ML-DSA-65 | FIPS 204 | Reticulados |
| Assinatura backup | SLH-DSA-128s | FIPS 205 | Hash-based |

A integração com o Hubstry Security fornece a infraestrutura criptográfica completa.

---

## Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_campos.py -v          # 41 vetores
pytest tests/test_inflexao.py -v        # Detecção de inflexões
pytest tests/test_analogia.py -v        # Motor de analogia
pytest tests/test_fluxo.py -v           # Fluxo contínuo
pytest tests/test_harvest_guard.py -v   # Proteção HNDL
pytest tests/test_miner.py -v           # Minerador PCQ
```

### Cobertura de testes

| Módulo | Testes | Cobertura |
|--------|--------|-----------|
| Campos Granulares | 8 testes | Estrutura dos 41 vetores |
| Detector de Inflexões | 8 testes | Subida, queda, série plana, cascata |
| Motor de Analogia | 6 testes | Heurística, funcional, homologia |
| Fluxo Contínuo | 7 testes | 5 fases, acumulação, contagem |
| HarvestGuard | 6 testes | Proteção HNDL, sensibilidade, validade |
| Minerador PCQ | 8 testes | Ranking, risco quântico, carteira |

---

## Quick Start

```bash
# Clonar
git clone https://github.com/guilherme-machado-ceo/DataBank-Fintech.git
cd DataBank-Fintech

# Instalar dependências
pip install -r requirements.txt

# Rodar motor completo (1 ciclo de demonstração)
python run_local.py

# Rodar testes
pytest tests/ -v
```

### O que run_local.py executa

1. Gera dados simulados para 41 vetores (120 dias)
2. Executa 1 ciclo completo do axioma (5 fases)
3. Detecta inflexões em séries temporais
4. Opera analogias entre 4 campos (heurística, funcional, homologia)
5. Gera insights e ações econômicas
6. Demonstra proteção HNDL com ML-KEM-768 / ML-DSA-65
7. Calcula ranking de mineração com risco quântico por blockchain

---

## Ecossistema Hubstry

- [Overall.xyz](https://www.overall.xyz) — Hub central do ecossistema
- [Hubstry Security](https://github.com/guilherme-machado-ceo/hubstry-security) — Infraestrutura PQC (ML-KEM, ML-DSA, SLH-DSA, HSL Auth)
- [DataBank Dashboard](https://databank-fintech.streamlit.app/) — Protótipo interativo Streamlit

---

## Site

[https://guilherme-machado-ceo.github.io/DataBank-Fintech/](https://guilherme-machado-ceo.github.io/DataBank-Fintech/)

Páginas:
- Home — Visão geral e 4 pilares
- PQC — Segurança pós-quântica e proteção HNDL
- Algoritmo — Motor de Inferência Analógica (conceitual)
- Contato — Colaboração e ecossistema

---

## Contato

- Email: guilhermemachado@hubstry.onmicrosoft.com
- LinkedIn: [linkedin.com/in/guilhermegoncalvesmachado](https://www.linkedin.com/in/guilhermegoncalvesmachado)
- Facebook: [facebook.com/guilhermemachadodonorte](https://www.facebook.com/guilhermemachadodonorte)
- GitHub: [github.com/guilherme-machado-ceo](https://github.com/guilherme-machado-ceo)

---

## Fundador

Guilherme Gonçalves Machado — Empreendedor 50+, indie maker, founder solo bootstrap, autodidata.

---

## Licença

Apache 2.0 (código) | Direitos autorais do autor (modelo de negócio, marca, visão estratégica)
```

---

## Como aplicar:

1. Abra: `https://github.com/guilherme-machado-ceo/DataBank-Fintech/blob/main/README.md`
2. Clique no **lápis** ✏️
3. **Ctrl+A** → **Delete** (apaga tudo)
4. **Ctrl+V** (cola o bloco acima)
5. **Commit changes**

Os badges aparecem como imagens. As tabelas renderizam com grid. Os acentos ficam corretos. Tudo é markdown padrão do GitHub, sem HTML que possa quebrar.
