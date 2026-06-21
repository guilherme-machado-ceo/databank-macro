from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# Importa o motor real do projeto
from src.core.campos_granulares import REGISTRO_CAMPOS
from src.ingestion.real_data import IngestorReal


APP_TITLE = "Data Bank – Dashboard de Vetores Reais"
LOGO_PATH = Path("logo-databank.png")

SECTOR_PROFILES = {
    "Agro": {"base_multiplier": 1.10, "market_demand": 82, "privacy_risk": 38},
    "Saúde": {"base_multiplier": 1.28, "market_demand": 88, "privacy_risk": 78},
    "Educação": {"base_multiplier": 0.95, "market_demand": 66, "privacy_risk": 52},
    "Energia": {"base_multiplier": 1.18, "market_demand": 76, "privacy_risk": 44},
    "Financeiro": {"base_multiplier": 1.35, "market_demand": 92, "privacy_risk": 72},
    "Varejo": {"base_multiplier": 1.08, "market_demand": 80, "privacy_risk": 58},
}

REVENUE_LINES = {
    "Assinatura SaaS": 0.10,
    "Comissão de monetização": 0.18,
    "Relatórios e Score-as-a-Service": 0.08,
    "Custódia e tokenização": 0.07,
    "Crédito informacional": 0.14,
}


@dataclass(frozen=True)
class DatasetMetrics:
    rows: int
    columns: int
    completeness: float
    numeric_columns: int
    categorical_columns: int
    duplicates: int
    estimated_size_mb: float


def build_demo_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cliente_id": range(1001, 1051),
            "setor": ["Agro", "Saúde", "Financeiro", "Varejo", "Energia"] * 10,
            "receita_mensal": [
                12500, 18800, 32100, 22100, 27800,
                14100, 20100, 35400, 24500, 30100,
            ] * 5,
            "score_relacionamento": [72, 88, 91, 77, 84, 69, 86, 94, 81, 89] * 5,
            "consentimento_lgpd": [True, True, True, False, True, True, False, True, True, True] * 5,
            "regiao": ["Sul", "Sudeste", "Nordeste", "Centro-Oeste", "Norte"] * 10,
        }
    )


def load_uploaded_dataset(uploaded_file) -> pd.DataFrame:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(uploaded_file)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(uploaded_file)
    if suffix == ".json":
        return pd.read_json(uploaded_file)
    raise ValueError("Formato não suportado. Envie CSV, XLSX, XLS ou JSON.")


def calculate_dataset_metrics(df: pd.DataFrame) -> DatasetMetrics:
    rows, columns = df.shape
    total_cells = max(rows * columns, 1)
    missing_cells = int(df.isna().sum().sum())
    completeness = 100 * (1 - missing_cells / total_cells)
    duplicates = int(df.duplicated().sum())
    numeric_columns = len(df.select_dtypes(include="number").columns)
    categorical_columns = columns - numeric_columns
    estimated_size_mb = max(df.memory_usage(deep=True).sum() / 1_000_000, 0.01)

    return DatasetMetrics(
        rows=rows,
        columns=columns,
        completeness=completeness,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        duplicates=duplicates,
        estimated_size_mb=estimated_size_mb,
    )


def normalize(value: float, lower: float, upper: float) -> float:
    clipped = max(lower, min(value, upper))
    return 100 * (clipped - lower) / (upper - lower)


def calculate_scores(metrics: DatasetMetrics, sector: str, governance_level: int) -> dict[str, float]:
    profile = SECTOR_PROFILES[sector]
    volume_score = normalize(metrics.rows * metrics.columns, 100, 250_000)
    quality_score = metrics.completeness - min(metrics.duplicates / max(metrics.rows, 1) * 45, 25)
    diversity_score = normalize(metrics.columns + metrics.numeric_columns * 1.5, 3, 60)
    governance_score = governance_level
    demand_score = profile["market_demand"]
    privacy_penalty = profile["privacy_risk"] * (1 - governance_level / 100)

    asset_score = (
        volume_score * 0.22
        + quality_score * 0.24
        + diversity_score * 0.16
        + governance_score * 0.18
        + demand_score * 0.20
        - privacy_penalty * 0.12
    )

    return {
        "Score de volume": round(volume_score, 1),
        "Score de qualidade": round(max(0, quality_score), 1),
        "Score de diversidade": round(diversity_score, 1),
        "Score de governança": round(governance_score, 1),
        "Demanda de mercado": round(demand_score, 1),
        "Risco residual LGPD": round(max(0, privacy_penalty), 1),
        "Data Asset Score": round(max(0, min(asset_score, 100)), 1),
    }


def estimate_valuation(metrics: DatasetMetrics, scores: dict[str, float], sector: str, revenue_potential: float) -> dict[str, float]:
    profile = SECTOR_PROFILES[sector]
    density_factor = max(metrics.numeric_columns + metrics.categorical_columns * 0.55, 1)
    base_value = metrics.rows * density_factor * profile["base_multiplier"] * 2.85
    quality_premium = 1 + scores["Data Asset Score"] / 100
    revenue_signal = revenue_potential * 0.018
    fair_value = base_value * quality_premium + revenue_signal
    tokenizable_value = fair_value * 0.62
    credit_limit = fair_value * (0.18 + scores["Score de governança"] / 500)

    return {
        "valuation": round(fair_value, 2),
        "tokenizable_value": round(tokenizable_value, 2),
        "credit_limit": round(credit_limit, 2),
    }


def render_score_radar(scores: dict[str, float]) -> None:
    radar_rows = [
        {"Dimensão": key, "Score": value}
        for key, value in scores.items()
        if key not in ("Data Asset Score", "Risco residual LGPD")
    ]
    chart = (
        alt.Chart(pd.DataFrame(radar_rows))
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Dimensão:N", sort=None, axis=alt.Axis(labelAngle=-25)),
            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Dimensão:N", legend=None),
            tooltip=["Dimensão", alt.Tooltip("Score:Q", format=".1f")],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def render_revenue_projection(valuation: float, months: int) -> None:
    rows = []
    for month in range(1, months + 1):
        maturity = min(1, 0.18 + month / months)
        for line, share in REVENUE_LINES.items():
            rows.append(
                {
                    "Mês": month,
                    "Fonte": line,
                    "Receita projetada": valuation * share * maturity / 12,
                }
            )

    chart = (
        alt.Chart(pd.DataFrame(rows))
        .mark_area(opacity=0.82)
        .encode(
            x=alt.X("Mês:O"),
            y=alt.Y("Receita projetada:Q", stack="zero", title="Receita mensal projetada (R$)"),
            color=alt.Color("Fonte:N"),
            tooltip=["Mês", "Fonte", alt.Tooltip("Receita projetada:Q", format=",.2f")],
        )
        .properties(height=330)
    )
    st.altair_chart(chart, use_container_width=True)


def render_compliance_checklist(scores: dict[str, float], sector: str) -> None:
    risk = scores["Risco residual LGPD"]
    checklist = pd.DataFrame(
        [
            {
                "Controle": "Consentimento e base legal documentados",
                "Status": "Atenção" if risk > 30 else "OK",
                "Prioridade": "Alta" if sector in {"Saúde", "Financeiro"} else "Média",
            },
            {
                "Controle": "Pseudonimização de dados sensíveis",
                "Status": "Atenção" if risk > 25 else "OK",
                "Prioridade": "Alta",
            },
            {
                "Controle": "Logs de auditoria e trilhas de custódia",
                "Status": "OK" if scores["Score de governança"] >= 70 else "Atenção",
                "Prioridade": "Média",
            },
            {
                "Controle": "Política de retenção e descarte",
                "Status": "OK" if scores["Score de qualidade"] >= 75 else "Atenção",
                "Prioridade": "Média",
            },
        ]
    )
    st.dataframe(checklist, use_container_width=True, hide_index=True)


@st.cache_data(ttl=3600, show_spinner="Coletando dados reais das APIs...")
def coletar_vetores_reais():
    """Coleta (ou lê do cache) todos os 41 vetores do catálogo."""
    ingestor = IngestorReal()
    resultados = ingestor.coletar_todos(usar_cache=True, max_age_hours=24)
    resumo = ingestor.resumo(resultados)
    return resultados, resumo


def render_vetores_reais():
    st.subheader("Vetores do catálogo com fontes reais")
    st.caption(
        "Cada linha mostra o valor mais recente, a fonte real e a última atualização. "
        "Vetores sem API gratuita aparecem como 'Fonte pendente'."
    )

    resultados, resumo = coletar_vetores_reais()

    total = resumo["total_vetores"]
    reais = resumo["com_dados_reais"]
    pendentes = resumo["pendentes"]

    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        st.metric("Total de vetores", total)
    with kpi_cols[1]:
        st.metric("Com dados reais", reais)
    with kpi_cols[2]:
        st.metric("Pendentes", pendentes)

    st.progress(reais / total, text=f"{reais} de {total} vetores com dados reais")

    for campo_enum, lista in resultados.items():
        with st.expander(f"{campo_enum.name} ({sum(1 for s in lista if s.disponivel)}/{len(lista)} reais)"):
            for sr in lista:
                cols = st.columns([2, 1.2, 1.5, 1.5])
                with cols[0]:
                    st.markdown(f"**{sr.nome}**  `<{sr.vetor_id}>`")
                with cols[1]:
                    if sr.disponivel:
                        ultimo = sr.serie.iloc[-1]
                        st.metric(label="Valor atual", value=f"{ultimo:,.4f}")
                    else:
                        st.markdown(":gray[Fonte pendente]")
                with cols[2]:
                    if sr.disponivel:
                        fonte = sr.fonte or "—"
                        st.markdown(f"Fonte: `{fonte}`")
                        if sr.cache:
                            st.caption(f"_:orange[cache: {sr.atualizado_em}]_")
                        else:
                            st.caption(f"_:green[atualizado: {sr.atualizado_em}]_")
                    else:
                        st.caption(f"_:red[{sr.erro or 'sem fonte gratuita'}]_")
                with cols[3]:
                    if sr.disponivel:
                        df = pd.DataFrame({"Data": sr.serie.index, "Valor": sr.serie.values})
                        chart = (
                            alt.Chart(df)
                            .mark_line()
                            .encode(x="Data:T", y="Valor:Q", tooltip=["Data", alt.Tooltip("Valor:Q", format=",.4f")])
                            .properties(height=120)
                        )
                        st.altair_chart(chart, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🏦", layout="wide")

    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=130)
        st.title("Data Bank")
        st.caption("Protótipo Streamlit para valuation, score, monetização e crédito de dados.")

        uploaded_file = st.file_uploader(
            "Carregue um dataset",
            type=["csv", "xlsx", "xls", "json"],
            help="Se nenhum arquivo for enviado, o app usa uma base demonstrativa.",
        )
        sector = st.selectbox("Setor do dataset", list(SECTOR_PROFILES.keys()), index=4)
        governance_level = st.slider("Maturidade de governança / LGPD", 0, 100, 72)
        revenue_potential = st.number_input(
            "Potencial econômico anual estimado (R$)",
            min_value=0.0,
            value=450_000.0,
            step=25_000.0,
        )
        projection_months = st.slider("Horizonte de projeção", 6, 36, 18)

    st.title("🏦 Data Bank – Dashboard de Vetores Reais")
    st.markdown(
        "Painel de honestidade radical: cada vetor do catálogo mostra sua **fonte real**, "
        "**valor atual** e **última atualização**. Sem simulações mascaradas."
    )

    tab_vetores, tab_overview, tab_score, tab_finance, tab_compliance, tab_data = st.tabs(
        ["Vetores Reais", "Visão geral", "Score", "Monetização", "Governança", "Dataset"]
    )

    with tab_vetores:
        render_vetores_reais()

    # Aba de valuation/simulação mantida com avisos claros
    if uploaded_file is not None:
        df = load_uploaded_dataset(uploaded_file)
        dataset_source = f"Dataset carregado: {uploaded_file.name}"
    else:
        df = build_demo_dataset()
        dataset_source = "Dataset demonstrativo do Data Bank"

    metrics = calculate_dataset_metrics(df)
    scores = calculate_scores(metrics, sector, governance_level)
    valuation = estimate_valuation(metrics, scores, sector, revenue_potential)

    with tab_overview:
        st.info(dataset_source)
        st.warning(
            "As métricas abaixo são uma **simulação de valuation** baseada em regras arbitrárias. "
            "Não representam laudo financeiro, jurídico ou contábil."
        )

        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.metric("Data Asset Score", f"{scores['Data Asset Score']:.1f}/100")
        with kpi_cols[1]:
            st.metric("Valuation estimado", f"R$ {valuation['valuation']:,.2f}")
        with kpi_cols[2]:
            st.metric("Valor tokenizável", f"R$ {valuation['tokenizable_value']:,.2f}")
        with kpi_cols[3]:
            st.metric("Limite de crédito", f"R$ {valuation['credit_limit']:,.2f}")

        st.subheader("Resumo operacional")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Linhas", f"{metrics.rows:,}")
        with c2:
            st.metric("Colunas", f"{metrics.columns:,}")
        with c3:
            st.metric("Completude", f"{metrics.completeness:.1f}%")
        with c4:
            st.metric("Tamanho estimado", f"{metrics.estimated_size_mb:.2f} MB")

    with tab_score:
        st.subheader("Score proprietário de ativos de dados")
        left, right = st.columns([2, 1])
        with left:
            render_score_radar(scores)
        with right:
            st.metric("Risco residual LGPD", f"{scores['Risco residual LGPD']:.1f}/100")
            st.metric("Demanda de mercado", f"{scores['Demanda de mercado']:.1f}/100")
            st.metric("Duplicidades", f"{metrics.duplicates:,}")
            st.caption("Pontuação simulada para pré-MVP.")

    with tab_finance:
        st.subheader("Projeção de monetização")
        render_revenue_projection(valuation["valuation"], projection_months)
        st.subheader("Fontes de receita simuladas")
        revenue_table = pd.DataFrame(
            [
                {"Fonte": line, "Participação estimada": f"{share * 100:.0f}%"}
                for line, share in REVENUE_LINES.items()
            ]
        )
        st.dataframe(revenue_table, use_container_width=True, hide_index=True)

    with tab_compliance:
        st.subheader("Governança, custódia e conformidade")
        render_compliance_checklist(scores, sector)
        st.warning(
            "Este painel é uma simulação para descoberta de produto. A análise LGPD definitiva exige "
            "inventário de dados, base legal, DPO/jurídico e trilhas de auditoria reais."
        )

    with tab_data:
        st.subheader("Prévia do dataset")
        st.dataframe(df.head(100), use_container_width=True)
        st.subheader("Perfil de colunas")
        profile = pd.DataFrame(
            {
                "Coluna": df.columns,
                "Tipo": [str(dtype) for dtype in df.dtypes],
                "Nulos": [int(df[column].isna().sum()) for column in df.columns],
                "Valores únicos": [int(df[column].nunique(dropna=True)) for column in df.columns],
            }
        )
        st.dataframe(profile, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
