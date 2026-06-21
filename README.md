# GuruDev Core · Hubstry-DeepTech

> **Idioma**: **Português** | [English](README_EN.md)

**GuruDev** é uma linguagem de programação holística e ontológica, criada integralmente por **Guilherme Gonçalves Machado** — desde a concepção teórica até a arquitetura completa, incluindo a invenção da **GuruMatrix** (álgebra hexarrelacional π√f(A)) e toda a fundamentação ontológica que diferencia a linguagem. Desenvolvida sob o guarda-chuva da deep tech **Hubstry-DeepTech**, GuruDev não é um "port" ou wrapper de nenhuma linguagem existente — é uma criação original, construída do zero.

---

## Visão

GuruDev integra linguística, inteligência artificial, epistemologia e engenharia de software para criar um paradigma de programação **multimodal e semântico**, alinhado às demandas da próxima geração de sistemas computacionais. Sua sintaxe única de blocos ontológicos, anotações semânticas e interoperabilidade multilíngue a diferencia de qualquer outra linguagem de programação existente.

A ideia central é usar GuruDev com IA para que a máquina capture nível semântico — transcendendo a execução puramente sintática e alcançando compreensão ontológica do código.

---

## O Diferencial Ontológico

GuruDev não é "Python em português". É uma linguagem com identidade própria, fundamentada em três pilares acadêmicos publicados no Zenodo:

### 1. Programação Comparada — Fundamentos Teóricos
A linguagem se baseia na análise estrutural de 15+ linguagens de programação, extraindo padrões semânticos universais para criar uma gramática que é simultaneamente acessível e expressiva.

📄 **doi:** [10.5281/zenodo.20028887](https://doi.org/10.5281/zenodo.20028887)

### 2. IMIP — Interface de Múltiplas Interpretações Paramétricas
O **DISPATCH_ON_HERMENEUTICS** (§4.3 do IMIP) define 7 níveis de interpretação para texto computacional, permitindo que a mesma expressão seja compreendida em múltiplas camadas semânticas. A **Contenção Constitucional** (§5.5) restringe tokens por instância, garantindo segurança ontológica.

📄 **doi:** [10.5281/zenodo.19772798](https://doi.org/10.5281/zenodo.19772798)

### 3. π√f(A) — Álgebra Hexarrelacional (GuruMatrix)
A **GuruMatrix** é um tensor de 5 dimensões que rastreia operações por categoria, semântica e nível de interpretação — a estrutura de dados central que dá poder à máquina de capturar nível semântico. Este trabalho também explora a interseção com computação quântica.

📄 **doi:** [10.5281/zenodo.19775021](https://doi.org/10.5281/zenodo.19775021)
📄 **doi:** [10.5281/zenodo.18776401](https://doi.org/10.5281/zenodo.18776401)

---

## Sintaxe Ontológica — O Motor

A sintaxe da GuruDev permite **blocos ontológicos** com capacidade de subescrita, compensação e interoperabilidade:

| Construto | Sintaxe | Descrição |
|---|---|---|
| Bloco | `[$$bloco$$]` ... `[$$/bloco$$]` | Unidade ontológica principal |
| Sobrescrita | `[$$sobrescrita$$]` ... `[$$/sobrescrita$$]` | Redefine comportamento de operações |
| Código GuruDev | `¡codigo!` ... `!/codigo!` | Código nativo dentro do bloco |
| Subescrita Python | `¿python?` ... `?/python?` | Interoperabilidade com Python (exec()) |
| Compensação | `$$compensacao$$` ... `$$/compensacao$$` | Fallback automático em caso de erro |
| Tratamento de erro | `$$erro]` | Captura falhas com AST executável |

---

## Verticais de Negócio

GuruDev foi projetada com foco em quatro verticais estratégicas:

- **Segurança Cibernética** — Blocos ontológicos com contenção constitucional proporcionam segurança em nível semântico, impedindo interpretações não autorizadas de código.
- **Games** — A multimodalidade da linguagem e a capacidade de redefinir comportamentos via sobrescrita permitem criar sistemas de regras dinâmicos e adaptáveis para engines de jogos.
- **Interoperabilidade entre Linguagens** — Subescritas permitem executar Python, JavaScript, Rust e outras linguagens dentro de blocos ontológicos, com rastreamento semântico via GuruMatrix.
- **IA Geral** — A integração nativa com o DISPATCH_ON_HERMENEUTICS permite que modelos de IA operem em múltiplos níveis de interpretação, capturando semântica e não apenas sintaxe.

---

## Estado Atual do Projeto (Maio 2026)

### Funcionalidades Implementadas
- **38/38 testes passando** — suite completa de testes automatizados
- **Lexer (PLY)** — máquina de estados com 9 estados léxicos dedicados
- **Parser (PLY)** — gramática completa incluindo blocos ontológicos
- **Interpretador** — execução completa com motor ontológico ativo
- **REPL interativo** — modo read-eval-print com auto-finalização
- **CLI** — `gurudev run`, `gurudev test`, `gurudev repl`
- **Métodos String** (18) — `tamanho()`, `maiusculo()`, `minusculo()`, `contem()`, `substituir()`, `fatiar()`, `dividir()`, `remover_espacos()`, `inverter()`, `repetir()`, `comeca_com()`, `termina_com()`, `indice_de()`, `ultima_posicao()`, `para_maiusculo()`, `para_minusculo()`, `eh_numero()`, `eh_vazio()`
- **Métodos Array** (17) — `adicionar()`, `remover()`, `tamanho()`, `contem()`, `indice_de()`, `ordenar()`, `inverter()`, `fatiar()`, `juntar()`, `copiar()`, `limpar()`, `primeiro()`, `ultimo()`, `mapa()`, `filtrar()`, `reduzir()`, `plano()`
- **Classes** — `isto`, `this`, `iniciar()`, propriedades, métodos
- **Motor Ontológico** — blocos, subescritas, compensação ativos

### Instalação

```bash
git clone https://github.com/Hubstry-DeepTech/gurudev-core.git
cd gurudev-core
python -m pip install -e .
```

### Uso

```bash
# Executar arquivo .guru
gurudev run examples/calc.guru

# Exemplo ontológico
gurudev run examples/ontologico.guru

# REPL interativo
gurudev repl

# Suite de testes
gurudev test
```

---

## Estrutura do Repositório

```
gurudev-core/
├── src/
│   ├── lexer/                  # Máquina de estados PLY
│   ├── parser.py               # Gramática com blocos ontológicos
│   ├── interpreter.py          # Interpretador + motor ontológico
│   ├── ast_nodes.py            # Nós da AST
│   └── repl.py                 # REPL interativo
├── examples/
│   ├── calc.guru               # Exemplo String/Array methods
│   └── ontologico.guru         # Exemplo motor ontológico
├── run_interpreter_test.py     # Suite de testes (38)
├── pyproject.toml
├── README.md                   # Este arquivo (PT-BR)
├── README_EN.md                # Versão em inglês
└── LICENSE                     # Business Source License 1.1
```

---

## Links Oficiais

- **Site Hubstry:** [www.hubstry.dev](https://www.hubstry.dev)
- **Site GuruDev:** [gurudev-tech.site](https://gurudev-tech.site)
- **Repositório:** [github.com/Hubstry-DeepTech/gurudev-core](https://github.com/Hubstry-DeepTech/gurudev-core)

---

## Sobre o Criador

**Guilherme Gonçalves Machado** é o criador original da GuruDev — desde a concepção da ideia, passando pela arquitetura, design da linguagem, invenção da GuruMatrix, e toda a fundamentação teórica publicada nos papers acadêmicos. Toda a propriedade intelectual da linguagem, incluindo sua gramática, sintaxe ontológica, motor de interpretação e estruturas de dados, é criação original sua.

---

## Licença

Este projeto está licenciado sob a **Business Source License 1.1 (BSL 1.1)**.

O uso **não comercial** (pesquisa acadêmica, educação, projetos pessoais) é livre e encorajado. O uso comercial (venda, licenciamento, SaaS, integração em produtos comerciais) requer autorização expressa do criador.

Consulte o arquivo [LICENSE](LICENSE) para os termos completos.

© 2024-2026 Guilherme Gonçalves Machado · Hubstry-DeepTech. Todos os direitos reservados.
