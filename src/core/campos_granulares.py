from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum

class CampoGranular(Enum):
    CLIMA = "clima_eventos"
    INFRAESTRUTURA = "infraestrutura"
    CHIPS = "chips_semicondutores"
    TERRAS_RARAS = "terras_raras_desdolarizacao"
    CARBONO = "carbono_mercados"
    GEOPOLITICA = "geopolitica_risco"

class ModoCampo(Enum):
    PARALELO = "paralelo"
    SERIE = "serie"

@dataclass
class VetorConfig:
    nome: str
    descricao: str
    unidade: str
    fonte: str
    frequencia: str
    peso: float
    campo: CampoGranular
    sensibilidade_inflexao: float = 0.05

@dataclass
class CampoConfig:
    nome: CampoGranular
    descricao: str
    modo: ModoCampo
    conecta_com: List[CampoGranular]
    vetores: Dict[str, VetorConfig]

CAMPO_CLIMA = CampoConfig(
    nome=CampoGranular.CLIMA,
    descricao="Impacto de eventos climaticos na economia global",
    modo=ModoCampo.PARALELO,
    conecta_com=[CampoGranular.INFRAESTRUTURA, CampoGranular.TERRAS_RARAS, CampoGranular.CARBONO],
    vetores={
        "temperatura_media_global": VetorConfig("temperatura_media_global", "Anomalia C", "C", "NASA GISS", "mensal", 0.15, CampoGranular.CLIMA, 0.05),
        "frequencia_eventos_extremos": VetorConfig("frequencia_eventos_extremos", "Eventos extremos/mes", "eventos", "EM-DAT", "mensal", 0.20, CampoGranular.CLIMA, 0.05),
        "indice_transicao_energetica": VetorConfig("indice_transicao_energetica", "Velocidade transicao limpa", "indice", "IRENA", "trimestral", 0.15, CampoGranular.CLIMA, 0.05),
        "demanda_minerais_renovaveis": VetorConfig("demanda_minerais_renovaveis", "Demanda minerais renovaveis", "kt", "USGS/IEA", "mensal", 0.25, CampoGranular.CLIMA, 0.05),
        "preco_carbono_eu": VetorConfig("preco_carbono_eu", "Carbono EU ETS", "EUR/t", "ICE", "diario", 0.15, CampoGranular.CLIMA, 0.05),
        "capacidade_renovavel_gw": VetorConfig("capacidade_renovavel_gw", "Renovaveis instaladas", "GW", "IRENA", "trimestral", 0.10, CampoGranular.CLIMA, 0.05),
    }
)

CAMPO_INFRAESTRUTURA = CampoConfig(
    nome=CampoGranular.INFRAESTRUTURA,
    descricao="Data centers, redes, 5G",
    modo=ModoCampo.PARALELO,
    conecta_com=[CampoGranular.CHIPS, CampoGranular.TERRAS_RARAS, CampoGranular.CLIMA],
    vetores={
        "investimento_data_centers_usd": VetorConfig("investimento_data_centers_usd", "Investimento DC global", "USD bi", "Synergy", "trimestral", 0.20, CampoGranular.INFRAESTRUTURA, 0.03),
        "capacidade_data_centers_mw": VetorConfig("capacidade_data_centers_mw", "Capacidade DC", "MW", "Uptime", "trimestral", 0.15, CampoGranular.INFRAESTRUTURA, 0.03),
        "demanda_cobre_global": VetorConfig("demanda_cobre_global", "Demanda cobre", "kt", "ICSG", "mensal", 0.15, CampoGranular.INFRAESTRUTURA, 0.03),
        "demanda_aluminio_dc": VetorConfig("demanda_aluminio_dc", "Aluminio DC", "kt", "IAI", "mensal", 0.10, CampoGranular.INFRAESTRUTURA, 0.03),
        "expansao_5g_torres": VetorConfig("expansao_5g_torres", "Novas torres 5G", "torres", "GSMA", "trimestral", 0.15, CampoGranular.INFRAESTRUTURA, 0.03),
        "fibra_otica_novos_km": VetorConfig("fibra_otica_novos_km", "Fibra nova", "km", "FTTH", "trimestral", 0.10, CampoGranular.INFRAESTRUTURA, 0.03),
        "indice_infra_digital": VetorConfig("indice_infra_digital", "Infra digital", "indice", "ITU", "anual", 0.15, CampoGranular.INFRAESTRUTURA, 0.03),
    }
)

CAMPO_CHIPS = CampoConfig(
    nome=CampoGranular.CHIPS,
    descricao="Galio, germanio, silicio",
    modo=ModoCampo.SERIE,
    conecta_com=[CampoGranular.TERRAS_RARAS, CampoGranular.INFRAESTRUTURA],
    vetores={
        "producao_gallium_t": VetorConfig("producao_gallium_t", "Producao galio", "t", "USGS", "anual", 0.20, CampoGranular.CHIPS, 0.07),
        "producao_germanium_t": VetorConfig("producao_germanium_t", "Producao germanio", "t", "USGS", "anual", 0.15, CampoGranular.CHIPS, 0.07),
        "preco_gallium_usd_kg": VetorConfig("preco_gallium_usd_kg", "Preco galio", "USD/kg", "Fastmarkets", "semanal", 0.15, CampoGranular.CHIPS, 0.07),
        "preco_germanium_usd_kg": VetorConfig("preco_germanium_usd_kg", "Preco germanio", "USD/kg", "Metal Bulletin", "semanal", 0.10, CampoGranular.CHIPS, 0.07),
        "producao_gpus_m": VetorConfig("producao_gpus_m", "Producao GPUs", "mi un", "JPR", "trimestral", 0.15, CampoGranular.CHIPS, 0.07),
        "controle_exportacao_china": VetorConfig("controle_exportacao_china", "Controle exportacao", "indice", "CSIS", "mensal", 0.10, CampoGranular.CHIPS, 0.07),
        "investimento_fabs_usd": VetorConfig("investimento_fabs_usd", "Investimento fabs", "USD bi", "SEMI", "trimestral", 0.10, CampoGranular.CHIPS, 0.07),
        "lead_time_chips_dias": VetorConfig("lead_time_chips_dias", "Lead time chips", "dias", "Susquehanna", "mensal", 0.05, CampoGranular.CHIPS, 0.07),
    }
)

CAMPO_TERRAS_RARAS = CampoConfig(
    nome=CampoGranular.TERRAS_RARAS,
    descricao="REEs + desdolarizacao + vetores classicos",
    modo=ModoCampo.PARALELO,
    conecta_com=[CampoGranular.CHIPS, CampoGranular.INFRAESTRUTURA, CampoGranular.CLIMA, CampoGranular.GEOPOLITICA],
    vetores={
        "producao_global_ree_t": VetorConfig("producao_global_ree_t", "Producao REE", "t", "USGS", "anual", 0.06, CampoGranular.TERRAS_RARAS, 0.04),
        "producao_china_ree_pct": VetorConfig("producao_china_ree_pct", "China REE %", "%", "USGS", "anual", 0.06, CampoGranular.TERRAS_RARAS, 0.04),
        "preco_neodimio_usd_kg": VetorConfig("preco_neodimio_usd_kg", "Neodimio", "USD/kg", "Argus", "semanal", 0.05, CampoGranular.TERRAS_RARAS, 0.04),
        "preco_disprosio_usd_kg": VetorConfig("preco_disprosio_usd_kg", "Disprosio", "USD/kg", "Argus", "semanal", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "reservas_brasil_ree_t": VetorConfig("reservas_brasil_ree_t", "Reservas BR REE", "t", "CPRM", "anual", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "dolar_reservas_pct": VetorConfig("dolar_reservas_pct", "USD reservas globais", "%", "IMF", "trimestral", 0.06, CampoGranular.TERRAS_RARAS, 0.04),
        "comercio_nao_dolar_pct": VetorConfig("comercio_nao_dolar_pct", "Comercio nao-USD", "%", "BIS", "trimestral", 0.06, CampoGranular.TERRAS_RARAS, 0.04),
        "contratos_yuan_petroleo": VetorConfig("contratos_yuan_petroleo", "Petroleo em yuan", "bi barris", "INE", "mensal", 0.05, CampoGranular.TERRAS_RARAS, 0.04),
        "comercio_intra_brics_usd": VetorConfig("comercio_intra_brics_usd", "Comercio BRICS", "USD tri", "IMF", "anual", 0.05, CampoGranular.TERRAS_RARAS, 0.04),
        "usd_brl": VetorConfig("usd_brl", "Cambio USD/BRL", "BRL", "BCB", "diario", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "dxy_index": VetorConfig("dxy_index", "DXY", "pontos", "ICE", "diario", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "ouro_usd_oz": VetorConfig("ouro_usd_oz", "Ouro", "USD/oz", "LBMA", "diario", 0.06, CampoGranular.TERRAS_RARAS, 0.04),
        "brent_usd": VetorConfig("brent_usd", "Brent", "USD/bbl", "ICE", "diario", 0.05, CampoGranular.TERRAS_RARAS, 0.04),
        "btc_usd": VetorConfig("btc_usd", "Bitcoin", "USD", "CoinGecko", "diario", 0.05, CampoGranular.TERRAS_RARAS, 0.04),
        "reservas_ouro_china_t": VetorConfig("reservas_ouro_china_t", "Ouro China", "t", "PBoC", "mensal", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "producao_petroleo_opec": VetorConfig("producao_petroleo_opec", "Producao OPEC", "mbpd", "OPEC", "mensal", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "preco_cobre_usd_t": VetorConfig("preco_cobre_usd_t", "Cobre", "USD/t", "LME", "diario", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
        "preco_litio_usd_kg": VetorConfig("preco_litio_usd_kg", "Litio", "USD/kg", "Benchmark", "semanal", 0.04, CampoGranular.TERRAS_RARAS, 0.04),
    }
)

CAMPO_CARBONO = CampoConfig(
    nome=CampoGranular.CARBONO,
    descricao="Mercados de carbono compliance e voluntario",
    modo=ModoCampo.PARALELO,
    conecta_com=[CampoGranular.CLIMA, CampoGranular.INFRAESTRUTURA],
    vetores={
        "preco_carbono_eu": VetorConfig("preco_carbono_eu", "Carbono EU ETS", "EUR/t", "ICE / KraneShares (proxy ETF)", "diario", 0.25, CampoGranular.CARBONO, 0.05),
        "preco_carbono_eua": VetorConfig("preco_carbono_eua", "Carbono EUA (RGGI/WCI proxy ETF)", "USD/t", "Yahoo Finance (GRN)", "diario", 0.25, CampoGranular.CARBONO, 0.05),
        "preco_carbono_china": VetorConfig("preco_carbono_china", "Carbono China ETS (proxy ETF)", "USD/t", "Yahoo Finance (KGRN)", "diario", 0.20, CampoGranular.CARBONO, 0.05),
        "creditos_voluntarios_usd": VetorConfig("creditos_voluntarios_usd", "Creditos carbono voluntario (proxy ETF)", "USD/t", "Yahoo Finance (NETZ)", "diario", 0.15, CampoGranular.CARBONO, 0.05),
        "intensidade_carbono_setorial": VetorConfig("intensidade_carbono_setorial", "Intensidade de carbono do PIB mundial", "kg CO2e/USD", "World Bank", "anual", 0.15, CampoGranular.CARBONO, 0.05),
    }
)

CAMPO_GEOPOLITICA = CampoConfig(
    nome=CampoGranular.GEOPOLITICA,
    descricao="Risco geopolitico, conflitos e fragilidade estadual",
    modo=ModoCampo.PARALELO,
    conecta_com=[CampoGranular.TERRAS_RARAS, CampoGranular.CLIMA, CampoGranular.CARBONO],
    vetores={
        "geopolitical_risk_idx": VetorConfig("geopolitical_risk_idx", "Risco geopolitico global", "indice", "FRED (Caldara & Iacoviello)", "mensal", 0.25, CampoGranular.GEOPOLITICA, 0.04),
        "fragile_states_index": VetorConfig("fragile_states_index", "Indice de Estados Frageis", "indice", "Fund for Peace", "anual", 0.20, CampoGranular.GEOPOLITICA, 0.04),
        "conflitos_ativos": VetorConfig("conflitos_ativos", "Conflitos ativos", "numero", "ACLED", "mensal", 0.25, CampoGranular.GEOPOLITICA, 0.04),
        "indice_risco_pais": VetorConfig("indice_risco_pais", "Indice de risco pais", "indice", "PRS Group", "mensal", 0.15, CampoGranular.GEOPOLITICA, 0.04),
        "geopolitical_risk_vix": VetorConfig("geopolitical_risk_vix", "Proxy de risco geopolitico (VIX)", "pontos", "Yahoo Finance (^VIX)", "diario", 0.15, CampoGranular.GEOPOLITICA, 0.04),
    }
)

REGISTRO_CAMPOS = {
    CampoGranular.CLIMA: CAMPO_CLIMA,
    CampoGranular.INFRAESTRUTURA: CAMPO_INFRAESTRUTURA,
    CampoGranular.CHIPS: CAMPO_CHIPS,
    CampoGranular.TERRAS_RARAS: CAMPO_TERRAS_RARAS,
    CampoGranular.CARBONO: CAMPO_CARBONO,
    CampoGranular.GEOPOLITICA: CAMPO_GEOPOLITICA,
}

MAPA_CASCATA = {
    CampoGranular.TERRAS_RARAS: [CampoGranular.CHIPS, CampoGranular.INFRAESTRUTURA, CampoGranular.GEOPOLITICA],
    CampoGranular.CHIPS: [CampoGranular.INFRAESTRUTURA, CampoGranular.TERRAS_RARAS],
    CampoGranular.CLIMA: [CampoGranular.INFRAESTRUTURA, CampoGranular.TERRAS_RARAS, CampoGranular.CARBONO],
    CampoGranular.INFRAESTRUTURA: [CampoGranular.CHIPS, CampoGranular.TERRAS_RARAS, CampoGranular.CARBONO],
    CampoGranular.CARBONO: [CampoGranular.CLIMA, CampoGranular.INFRAESTRUTURA],
    CampoGranular.GEOPOLITICA: [CampoGranular.TERRAS_RARAS, CampoGranular.CLIMA, CampoGranular.CARBONO],
}

VALIDADE_ANOS = {"publico": 30, "interno": 20, "confidencial": 10, "restrito": 5}

def total_vetores() -> int:
    return sum(len(c.vetores) for c in REGISTRO_CAMPOS.values())

def get_sensibilidade(campo: CampoGranular) -> float:
    return {CampoGranular.CLIMA: 0.05, CampoGranular.INFRAESTRUTURA: 0.03,
            CampoGranular.CHIPS: 0.07, CampoGranular.TERRAS_RARAS: 0.04,
            CampoGranular.CARBONO: 0.05, CampoGranular.GEOPOLITICA: 0.04}.get(campo, 0.05)
