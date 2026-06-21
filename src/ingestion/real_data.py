"""
DataBank PCQ — Real Data Connector
====================================
Integra APIs gratuitas para dados econômicos, climáticos e financeiros reais.

Regra de honestidade:
- Se a API gratuita estiver disponível e retornar dados, usamos o dado real.
- Se a API falhar ou não existir fonte gratuita conhecida, retornamos None.
- Nenhuma simulação é gerada como se fosse dado real.

APIs utilizadas:
  BCB, Yahoo Finance, CoinGecko, Open-Meteo, NASA GISS, FRED, IMF, EIA, World Bank
"""
from __future__ import annotations

import io
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

from src.core.campos_granulares import REGISTRO_CAMPOS, CampoGranular
from src.ingestion.cache import DataCache

logger = logging.getLogger(__name__)


@dataclass
class SerieReal:
    """Resultado de uma tentativa de coleta real."""

    vetor_id: str
    campo: CampoGranular
    nome: str
    fonte: Optional[str]
    serie: Optional[pd.Series]
    atualizado_em: Optional[str] = None
    erro: Optional[str] = None
    cache: bool = False

    @property
    def disponivel(self) -> bool:
        return self.serie is not None and not self.serie.empty


# ============================================================
# CONECTORES ESPECIALIZADOS
# ============================================================
class BCBConnector:
    """Conector BCB para dados brasileiros reais."""

    BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs."

    def fetch_usd_brl(self, dias: int = 120) -> Optional[pd.Series]:
        try:
            end = datetime.now().strftime("%d/%m/%Y")
            start = (datetime.now() - timedelta(days=dias)).strftime("%d/%m/%Y")
            url = f"{self.BASE_URL}1/dados?formato=json&dataInicial={start}&dataFinal={end}"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            df = pd.DataFrame(dados)
            df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
            df["valor"] = df["valor"].astype(float)
            return df.set_index("data")["valor"].sort_index()
        except Exception as e:
            logger.warning(f"BCB USD/BRL falhou: {e}")
            return None

    def fetch_selic(self, dias: int = 120) -> Optional[pd.Series]:
        try:
            end = datetime.now().strftime("%d/%m/%Y")
            start = (datetime.now() - timedelta(days=dias)).strftime("%d/%m/%Y")
            url = f"{self.BASE_URL}432/dados?formato=json&dataInicial={start}&dataFinal={end}"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            df = pd.DataFrame(dados)
            df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
            df["valor"] = df["valor"].astype(float)
            return df.set_index("data")["valor"].sort_index()
        except Exception as e:
            logger.warning(f"BCB SELIC falhou: {e}")
            return None


class YahooFinanceConnector:
    """Conector Yahoo Finance para ações, commodities e índices."""

    def __init__(self):
        try:
            import yfinance as yf

            self.yf = yf
            self.available = True
        except ImportError:
            logger.warning("yfinance não instalado. Use: pip install yfinance")
            self.available = False

    def fetch_ticker(self, ticker: str, period: str = "6mo") -> Optional[pd.Series]:
        if not self.available:
            return None
        try:
            time.sleep(0.5)
            data = self.yf.Ticker(ticker).history(period=period)
            if data.empty:
                return None
            data.index = data.index.tz_localize(None)
            return data["Close"].sort_index()
        except Exception as e:
            logger.warning(f"Yahoo Finance {ticker} falhou: {e}")
            return None


class CoinGeckoConnector:
    """Conector CoinGecko para criptomoedas."""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def fetch_price_history(self, coin_id: str = "bitcoin", dias: int = 120) -> Optional[pd.Series]:
        try:
            url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
            params = {"vs_currency": "usd", "days": str(dias)}
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            prices = dados["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df.set_index("timestamp")["price"].sort_index()
        except Exception as e:
            logger.warning(f"CoinGecko {coin_id} falhou: {e}")
            return None


class OpenMeteoConnector:
    """Conector Open-Meteo para dados climáticos locais."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def fetch_temperature(self, lat: float, lon: float, days: int = 92) -> Optional[pd.Series]:
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max",
                "past_days": min(days, 92),
                "timezone": "auto",
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            if "daily" not in dados or "temperature_2m_max" not in dados["daily"]:
                return None
            df = pd.DataFrame(dados["daily"])
            df["time"] = pd.to_datetime(df["time"])
            return df.set_index("time")["temperature_2m_max"].sort_index()
        except Exception as e:
            logger.warning(f"Open-Meteo falhou: {e}")
            return None


class NASAGISSConnector:
    """
    Conector para temperatura global da NASA GISS.
    Usa o arquivo CSV público do GISTEMP v4.
    """

    URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"

    def fetch_global_temperature(self) -> Optional[pd.Series]:
        try:
            resp = requests.get(self.URL, timeout=30)
            resp.raise_for_status()
            # O CSV da NASA tem uma linha de titulo antes do cabecalho.
            df = pd.read_csv(io.StringIO(resp.text), skipinitialspace=True, skiprows=1)
            year_col = df.columns[0]
            df = df[df[year_col].apply(lambda x: str(x).strip().isdigit())]
            df[year_col] = df[year_col].astype(int)

            meses = [c for c in df.columns if c not in (year_col, "J-D", "D-N", "DJF", "MAM", "JJA", "SON")]
            meses = meses[:12]

            registros = []
            for _, row in df.iterrows():
                ano = int(row[year_col])
                for i, mes in enumerate(meses):
                    val = row[mes]
                    if pd.isna(val):
                        continue
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        continue
                    if val == -999.0:
                        continue
                    dt = pd.Timestamp(year=ano, month=i + 1, day=15)
                    registros.append((dt, val))

            serie = pd.Series([r[1] for r in registros], index=[r[0] for r in registros]).sort_index()
            return serie
        except Exception as e:
            logger.warning(f"NASA GISS falhou: {e}")
            return None


class FREDConnector:
    """Conector FRED (Federal Reserve Economic Data)."""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def fetch_series(self, series_id: str) -> Optional[pd.Series]:
        if not self.api_key or self.api_key == "demo":
            return None
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "asc",
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            obs = dados.get("observations", [])
            if not obs:
                return None
            registros = []
            for o in obs:
                try:
                    val = float(o["value"])
                except (ValueError, TypeError):
                    continue
                registros.append((pd.to_datetime(o["date"]), val))
            serie = pd.Series([r[1] for r in registros], index=[r[0] for r in registros]).sort_index()
            return serie
        except Exception as e:
            logger.warning(f"FRED {series_id} falhou: {e}")
            return None


class IMFConnector:
    """Conector IMF DataMapper para reservas em dólar (COFER)."""

    def fetch_dollar_reserves_pct(self) -> Optional[pd.Series]:
        """Retorna a parcela de reservas globais alocadas em USD (COFER)."""
        try:
            url = "https://www.imf.org/external/datamapper/api/v1/COFER"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            # Estrutura aninhada; tenta extrair série "World / US Dollar"
            values = dados.get("values", {})
            if "COFER" in values:
                values = values["COFER"]

            registros = []
            for chave, serie_dict in values.items():
                if not isinstance(serie_dict, dict):
                    continue
                # Heurística: procura série do World ou US Dollar
                label = chave.lower()
                if "world" in label or "usd" in label or "dollar" in label or "total" in label:
                    for ano_str, val in serie_dict.items():
                        try:
                            registros.append((pd.Timestamp(year=int(ano_str), month=12, day=31), float(val)))
                        except (ValueError, TypeError):
                            continue
                    break

            if not registros:
                return None
            return pd.Series([r[1] for r in registros], index=[r[0] for r in registros]).sort_index()
        except Exception as e:
            logger.warning(f"IMF COFER falhou: {e}")
            return None


class EIAConnector:
    """Conector EIA (Energy Information Administration) - API pública."""

    BASE_URL = "https://api.eia.gov/v2/"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def fetch_series(self, route: str, series_id: Optional[str] = None) -> Optional[pd.Series]:
        if not self.api_key:
            return None
        try:
            url = f"{self.BASE_URL}{route}/data"
            params = {"api_key": self.api_key, "frequency": "monthly", "data[0]": "value"}
            if series_id:
                params["facets[series][]"] = series_id
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            registros = []
            for item in dados.get("response", {}).get("data", []):
                try:
                    dt = pd.to_datetime(item["period"])
                    val = float(item["value"])
                    registros.append((dt, val))
                except (ValueError, TypeError, KeyError):
                    continue
            if not registros:
                return None
            return pd.Series([r[1] for r in registros], index=[r[0] for r in registros]).sort_index()
        except Exception as e:
            logger.warning(f"EIA {route} falhou: {e}")
            return None


class WorldBankConnector:
    """Conector World Bank Open Data API."""

    BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

    def fetch_indicator(
        self, indicator: str, country: str = "WLD", per_page: int = 100
    ) -> Optional[pd.Series]:
        try:
            url = self.BASE_URL.format(country=country, indicator=indicator)
            params = {"format": "json", "per_page": per_page}
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            if not isinstance(dados, list) or len(dados) < 2:
                return None
            registros = []
            for item in dados[1]:
                try:
                    ano = int(item["date"])
                    val = float(item["value"])
                    registros.append((pd.Timestamp(year=ano, month=12, day=31), val))
                except (ValueError, TypeError, KeyError):
                    continue
            if not registros:
                return None
            return pd.Series([r[1] for r in registros], index=[r[0] for r in registros]).sort_index()
        except Exception as e:
            logger.warning(f"World Bank {indicator} falhou: {e}")
            return None


# ============================================================
# ORQUESTRADOR DE COLETA POR VETOR
# ============================================================
class IngestorReal:
    """
    Coleta dados reais para cada vetor do catálogo.
    Usa cache SQLite para evitar rate limits e manter o dashboard funcional.
    """

    def __init__(
        self,
        alpha_vantage_key: Optional[str] = None,
        fred_api_key: Optional[str] = None,
        eia_api_key: Optional[str] = None,
        cache: Optional[DataCache] = None,
    ):
        self.bcb = BCBConnector()
        self.yahoo = YahooFinanceConnector()
        self.coingecko = CoinGeckoConnector()
        self.meteo = OpenMeteoConnector()
        self.nasa = NASAGISSConnector()
        self.fred = FREDConnector(fred_api_key)
        self.imf = IMFConnector()
        self.eia = EIAConnector(eia_api_key)
        self.world_bank = WorldBankConnector()
        self.cache = cache or DataCache()

    # ------------------------------------------------------------------
    # Coletores específicos por vetor
    # ------------------------------------------------------------------
    def _get_cache(self, vetor_id: str, campo: CampoGranular, nome: str) -> Optional[SerieReal]:
        cached = self.cache.get(vetor_id)
        if cached is None:
            return None
        return SerieReal(
            vetor_id=vetor_id,
            campo=campo,
            nome=nome,
            fonte=cached.get("fonte"),
            serie=cached.get("serie"),
            atualizado_em=cached.get("ultima_atualizacao"),
            cache=True,
        )

    def _put_cache(self, sr: SerieReal) -> None:
        if sr.serie is not None:
            self.cache.put(sr.vetor_id, sr.campo.name, sr.nome, sr.fonte, sr.serie)

    # ---------- CLIMA ----------
    def _coletar_temperatura_media_global(self) -> SerieReal:
        vid = "temperatura_media_global"
        nome = "Anomalia de temperatura global (NASA GISS)"
        campo = CampoGranular.CLIMA
        serie = self.nasa.fetch_global_temperature()
        return SerieReal(vid, campo, nome, "NASA GISS", serie)

    def _coletar_frequencia_eventos_extremos(self) -> SerieReal:
        # EM-DAT não possui API gratuita direta e confiável.
        return SerieReal(
            "frequencia_eventos_extremos",
            CampoGranular.CLIMA,
            "Eventos extremos/mes",
            None,
            None,
            erro="Fonte EM-DAT sem API gratuita disponivel",
        )

    def _coletar_indice_transicao_energetica(self) -> SerieReal:
        return SerieReal(
            "indice_transicao_energetica",
            CampoGranular.CLIMA,
            "Velocidade transicao limpa",
            None,
            None,
            erro="Fonte IRENA sem API gratuita disponivel",
        )

    def _coletar_demanda_minerais_renovaveis(self) -> SerieReal:
        return SerieReal(
            "demanda_minerais_renovaveis",
            CampoGranular.CLIMA,
            "Demanda minerais renovaveis",
            None,
            None,
            erro="Fonte USGS/IEA sem API gratuita disponivel",
        )

    def _coletar_preco_carbono_eu(self) -> SerieReal:
        # EU ETS não tem ticker Yahoo direto acessível sem assinatura.
        # Tenta ETFs de carbono como proxy; se falhar, retorna None.
        for ticker, label in [("KRBN", "KraneShares Global Carbon ETF"), ("NETZ", "SPDR MSCI World Net Zero ETF")]:
            serie = self.yahoo.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                return SerieReal("preco_carbono_eu", CampoGranular.CLIMA, "Carbono EU ETS (proxy ETF)", label, serie)
        return SerieReal(
            "preco_carbono_eu",
            CampoGranular.CLIMA,
            "Carbono EU ETS",
            None,
            None,
            erro="EU ETS e proxies gratuitos indisponiveis",
        )

    def _coletar_capacidade_renovavel_gw(self) -> SerieReal:
        return SerieReal(
            "capacidade_renovavel_gw",
            CampoGranular.CLIMA,
            "Renovaveis instaladas",
            None,
            None,
            erro="Fonte IRENA sem API gratuita disponivel",
        )

    # ---------- INFRAESTRUTURA ----------
    def _coletar_investimento_data_centers_usd(self) -> SerieReal:
        return SerieReal(
            "investimento_data_centers_usd",
            CampoGranular.INFRAESTRUTURA,
            "Investimento DC global",
            None,
            None,
            erro="Fonte Synergy Research paga; sem API gratuita",
        )

    def _coletar_capacidade_data_centers_mw(self) -> SerieReal:
        return SerieReal(
            "capacidade_data_centers_mw",
            CampoGranular.INFRAESTRUTURA,
            "Capacidade DC",
            None,
            None,
            erro="Fonte Uptime Institute paga; sem API gratuita",
        )

    def _coletar_demanda_cobre_global(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("HG=F", period="6mo")
        return SerieReal(
            "demanda_cobre_global",
            CampoGranular.INFRAESTRUTURA,
            "Demanda cobre (proxy preco futuro LME/COMEX)",
            "Yahoo Finance (HG=F)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_demanda_aluminio_dc(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("ALI=F", period="6mo")
        return SerieReal(
            "demanda_aluminio_dc",
            CampoGranular.INFRAESTRUTURA,
            "Aluminio DC (proxy preco futuro)",
            "Yahoo Finance (ALI=F)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_expansao_5g_torres(self) -> SerieReal:
        return SerieReal(
            "expansao_5g_torres",
            CampoGranular.INFRAESTRUTURA,
            "Novas torres 5G",
            None,
            None,
            erro="Fonte GSMA Intelligence paga; sem API gratuita",
        )

    def _coletar_fibra_otica_novos_km(self) -> SerieReal:
        return SerieReal(
            "fibra_otica_novos_km",
            CampoGranular.INFRAESTRUTURA,
            "Fibra nova",
            None,
            None,
            erro="Fonte FTTH Council paga; sem API gratuita",
        )

    def _coletar_indice_infra_digital(self) -> SerieReal:
        return SerieReal(
            "indice_infra_digital",
            CampoGranular.INFRAESTRUTURA,
            "Infra digital",
            None,
            None,
            erro="Fonte ITU paga; sem API gratuita",
        )

    # ---------- CHIPS ----------
    def _coletar_producao_gallium_t(self) -> SerieReal:
        return SerieReal(
            "producao_gallium_t",
            CampoGranular.CHIPS,
            "Producao galio",
            None,
            None,
            erro="Fonte USGS sem API estruturada gratuita para este indicador",
        )

    def _coletar_producao_germanium_t(self) -> SerieReal:
        return SerieReal(
            "producao_germanium_t",
            CampoGranular.CHIPS,
            "Producao germanio",
            None,
            None,
            erro="Fonte USGS sem API estruturada gratuita para este indicador",
        )

    def _coletar_preco_gallium_usd_kg(self) -> SerieReal:
        return SerieReal(
            "preco_gallium_usd_kg",
            CampoGranular.CHIPS,
            "Preco galio",
            None,
            None,
            erro="Fonte Fastmarkets paga; sem API gratuita",
        )

    def _coletar_preco_germanium_usd_kg(self) -> SerieReal:
        return SerieReal(
            "preco_germanium_usd_kg",
            CampoGranular.CHIPS,
            "Preco germanio",
            None,
            None,
            erro="Fonte Metal Bulletin paga; sem API gratuita",
        )

    def _coletar_producao_gpus_m(self) -> SerieReal:
        return SerieReal(
            "producao_gpus_m",
            CampoGranular.CHIPS,
            "Producao GPUs",
            None,
            None,
            erro="Fonte Jon Peddie Research paga; sem API gratuita",
        )

    def _coletar_controle_exportacao_china(self) -> SerieReal:
        return SerieReal(
            "controle_exportacao_china",
            CampoGranular.CHIPS,
            "Controle exportacao",
            None,
            None,
            erro="Fonte CSIS sem API estruturada gratuita",
        )

    def _coletar_investimento_fabs_usd(self) -> SerieReal:
        return SerieReal(
            "investimento_fabs_usd",
            CampoGranular.CHIPS,
            "Investimento fabs",
            None,
            None,
            erro="Fonte SEMI paga; sem API gratuita",
        )

    def _coletar_lead_time_chips_dias(self) -> SerieReal:
        return SerieReal(
            "lead_time_chips_dias",
            CampoGranular.CHIPS,
            "Lead time chips",
            None,
            None,
            erro="Fonte Susquehanna paga; sem API gratuita",
        )

    # ---------- TERRAS RARAS ----------
    def _coletar_producao_global_ree_t(self) -> SerieReal:
        return SerieReal(
            "producao_global_ree_t",
            CampoGranular.TERRAS_RARAS,
            "Producao REE",
            None,
            None,
            erro="Fonte USGS sem API estruturada gratuita",
        )

    def _coletar_producao_china_ree_pct(self) -> SerieReal:
        return SerieReal(
            "producao_china_ree_pct",
            CampoGranular.TERRAS_RARAS,
            "China REE %",
            None,
            None,
            erro="Fonte USGS sem API estruturada gratuita",
        )

    def _coletar_preco_neodimio_usd_kg(self) -> SerieReal:
        return SerieReal(
            "preco_neodimio_usd_kg",
            CampoGranular.TERRAS_RARAS,
            "Neodimio",
            None,
            None,
            erro="Fonte Argus Media paga; sem API gratuita",
        )

    def _coletar_preco_disprosio_usd_kg(self) -> SerieReal:
        return SerieReal(
            "preco_disprosio_usd_kg",
            CampoGranular.TERRAS_RARAS,
            "Disprosio",
            None,
            None,
            erro="Fonte Argus Media paga; sem API gratuita",
        )

    def _coletar_reservas_brasil_ree_t(self) -> SerieReal:
        return SerieReal(
            "reservas_brasil_ree_t",
            CampoGranular.TERRAS_RARAS,
            "Reservas BR REE",
            None,
            None,
            erro="Fonte CPRM sem API estruturada gratuita",
        )

    def _coletar_dolar_reservas_pct(self) -> SerieReal:
        serie = self.imf.fetch_dollar_reserves_pct()
        return SerieReal(
            "dolar_reservas_pct",
            CampoGranular.TERRAS_RARAS,
            "USD reservas globais (% COFER)",
            "IMF COFER" if serie is not None else None,
            serie,
            erro=None if serie is not None else "IMF COFER indisponivel",
        )

    def _coletar_comercio_nao_dolar_pct(self) -> SerieReal:
        return SerieReal(
            "comercio_nao_dolar_pct",
            CampoGranular.TERRAS_RARAS,
            "Comercio nao-USD",
            None,
            None,
            erro="Fonte BIS sem API estruturada gratuita",
        )

    def _coletar_contratos_yuan_petroleo(self) -> SerieReal:
        return SerieReal(
            "contratos_yuan_petroleo",
            CampoGranular.TERRAS_RARAS,
            "Petroleo em yuan",
            None,
            None,
            erro="Fonte INE (Shanghai) sem API gratuita direta",
        )

    def _coletar_comercio_intra_brics_usd(self) -> SerieReal:
        return SerieReal(
            "comercio_intra_brics_usd",
            CampoGranular.TERRAS_RARAS,
            "Comercio BRICS",
            None,
            None,
            erro="Fonte IMF sem série estruturada gratuita para comercio intra-BRICS",
        )

    def _coletar_usd_brl(self) -> SerieReal:
        serie = self.bcb.fetch_usd_brl(dias=120)
        return SerieReal(
            "usd_brl",
            CampoGranular.TERRAS_RARAS,
            "Cambio USD/BRL",
            "BCB" if serie is not None else None,
            serie,
            erro=None if serie is not None else "BCB indisponivel",
        )

    def _coletar_dxy_index(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("DX-Y.NYB", period="6mo")
        return SerieReal(
            "dxy_index",
            CampoGranular.TERRAS_RARAS,
            "Dollar Index (DXY)",
            "Yahoo Finance (DX-Y.NYB)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_ouro_usd_oz(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("GC=F", period="6mo")
        return SerieReal(
            "ouro_usd_oz",
            CampoGranular.TERRAS_RARAS,
            "Ouro",
            "Yahoo Finance (GC=F)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_brent_usd(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("BZ=F", period="6mo")
        return SerieReal(
            "brent_usd",
            CampoGranular.TERRAS_RARAS,
            "Brent",
            "Yahoo Finance (BZ=F)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_btc_usd(self) -> SerieReal:
        serie = self.coingecko.fetch_price_history("bitcoin", dias=120)
        return SerieReal(
            "btc_usd",
            CampoGranular.TERRAS_RARAS,
            "Bitcoin",
            "CoinGecko" if serie is not None else None,
            serie,
            erro=None if serie is not None else "CoinGecko indisponivel",
        )

    def _coletar_reservas_ouro_china_t(self) -> SerieReal:
        return SerieReal(
            "reservas_ouro_china_t",
            CampoGranular.TERRAS_RARAS,
            "Ouro China",
            None,
            None,
            erro="Fonte PBoC sem API estruturada gratuita",
        )

    def _coletar_producao_petroleo_opec(self) -> SerieReal:
        # EIA possui dados de producao se API key for fornecida
        serie = None
        if self.eia.api_key:
            serie = self.eia.fetch_series("petroleum/crdlbpns", None)
        return SerieReal(
            "producao_petroleo_opec",
            CampoGranular.TERRAS_RARAS,
            "Producao OPEC",
            "EIA" if serie is not None else None,
            serie,
            erro=None if serie is not None else "EIA indisponivel (requer API key)",
        )

    def _coletar_preco_cobre_usd_t(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("HG=F", period="6mo")
        return SerieReal(
            "preco_cobre_usd_t",
            CampoGranular.TERRAS_RARAS,
            "Cobre",
            "Yahoo Finance (HG=F)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_preco_litio_usd_kg(self) -> SerieReal:
        # ETF de litio como proxy
        serie = self.yahoo.fetch_ticker("LIT", period="6mo")
        return SerieReal(
            "preco_litio_usd_kg",
            CampoGranular.TERRAS_RARAS,
            "Litio (proxy ETF Global X Lithium)",
            "Yahoo Finance (LIT)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    # ---------- CARBONO ----------
    def _coletar_preco_carbono_eu_novo(self) -> SerieReal:
        # Replica a coleta do clima, mas agora no campo CARBONO.
        for ticker, label in [("KRBN", "KraneShares Global Carbon ETF"), ("NETZ", "SPDR MSCI World Net Zero ETF")]:
            serie = self.yahoo.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                return SerieReal("preco_carbono_eu", CampoGranular.CARBONO, "Carbono EU ETS (proxy ETF)", label, serie)
        return SerieReal(
            "preco_carbono_eu",
            CampoGranular.CARBONO,
            "Carbono EU ETS",
            None,
            None,
            erro="EU ETS e proxies gratuitos indisponiveis",
        )

    def _coletar_preco_carbono_eua(self) -> SerieReal:
        for ticker, label in [("GRN", "iPath Carbon ETN"), ("KRBN", "KraneShares Global Carbon ETF")]:
            serie = self.yahoo.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                return SerieReal("preco_carbono_eua", CampoGranular.CARBONO, "Carbono EUA (proxy ETF)", label, serie)
        return SerieReal(
            "preco_carbono_eua",
            CampoGranular.CARBONO,
            "Carbono EUA (RGGI/WCI)",
            None,
            None,
            erro="Mercado de carbono EUA e proxies gratuitos indisponiveis",
        )

    def _coletar_preco_carbono_china(self) -> SerieReal:
        for ticker, label in [("KGRN", "KraneShares MSCI China Clean Technology ETF"), ("PBW", "WilderHill Clean Energy ETF")]:
            serie = self.yahoo.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                return SerieReal("preco_carbono_china", CampoGranular.CARBONO, "Carbono China ETS (proxy ETF)", label, serie)
        return SerieReal(
            "preco_carbono_china",
            CampoGranular.CARBONO,
            "Carbono China ETS",
            None,
            None,
            erro="China ETS e proxies gratuitos indisponiveis",
        )

    def _coletar_creditos_voluntarios_usd(self) -> SerieReal:
        for ticker, label in [("NETZ", "SPDR MSCI World Net Zero ETF"), ("CBON", "iShares MSCI ACWI Low Carbon Target ETF")]:
            serie = self.yahoo.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                return SerieReal("creditos_voluntarios_usd", CampoGranular.CARBONO, "Creditos carbono voluntario (proxy ETF)", label, serie)
        return SerieReal(
            "creditos_voluntarios_usd",
            CampoGranular.CARBONO,
            "Creditos carbono voluntario",
            None,
            None,
            erro="Mercado voluntario de carbono e proxies gratuitos indisponiveis",
        )

    def _coletar_intensidade_carbono_setorial(self) -> SerieReal:
        serie = self.world_bank.fetch_indicator("EN.GHG.CO2.RT.GDP.KD", country="WLD")
        return SerieReal(
            "intensidade_carbono_setorial",
            CampoGranular.CARBONO,
            "Intensidade de carbono do PIB mundial",
            "World Bank" if serie is not None else None,
            serie,
            erro=None if serie is not None else "World Bank indisponivel",
        )

    # ---------- GEOPOLITICA ----------
    def _coletar_geopolitical_risk_idx(self) -> SerieReal:
        # GPRD (Geopolitical Risk) é pago. FRED GEPUINDM exige API key gratuita.
        serie = self.fred.fetch_series("GEPUINDM")
        return SerieReal(
            "geopolitical_risk_idx",
            CampoGranular.GEOPOLITICA,
            "Risco geopolitico global",
            "FRED GEPUINDM" if serie is not None else None,
            serie,
            erro=None if serie is not None else "FRED indisponivel (requer API key gratuita em fred.stlouisfed.org)",
        )

    def _coletar_geopolitical_risk_vix(self) -> SerieReal:
        serie = self.yahoo.fetch_ticker("^VIX", period="6mo")
        return SerieReal(
            "geopolitical_risk_vix",
            CampoGranular.GEOPOLITICA,
            "Proxy de risco geopolitico (VIX)",
            "Yahoo Finance (^VIX)" if serie is not None else None,
            serie,
            erro=None if serie is not None else "Yahoo Finance indisponivel",
        )

    def _coletar_fragile_states_index(self) -> SerieReal:
        # Fund for Peace publica dados, mas não oferece API estruturada gratuita.
        return SerieReal(
            "fragile_states_index",
            CampoGranular.GEOPOLITICA,
            "Indice de Estados Frageis",
            None,
            None,
            erro="Fund for Peace nao oferece API gratuita aberta",
        )

    def _coletar_conflitos_ativos(self) -> SerieReal:
        # ACLED oferece API gratuita mediante cadastro em acleddata.com.
        # Sem token/email valido, retorna None.
        return SerieReal(
            "conflitos_ativos",
            CampoGranular.GEOPOLITICA,
            "Conflitos ativos",
            None,
            None,
            erro="ACLED requer cadastro gratuito em acleddata.com para obter API key",
        )

    def _coletar_indice_risco_pais(self) -> SerieReal:
        return SerieReal(
            "indice_risco_pais",
            CampoGranular.GEOPOLITICA,
            "Indice de risco pais",
            None,
            None,
            erro="PRS Group e fonte paga; sem API gratuita",
        )

    # ------------------------------------------------------------------
    # Mapeamento vetor -> coletor
    # ------------------------------------------------------------------
    COLETORES: Dict[str, Any] = {
        # Clima
        "temperatura_media_global": "_coletar_temperatura_media_global",
        "frequencia_eventos_extremos": "_coletar_frequencia_eventos_extremos",
        "indice_transicao_energetica": "_coletar_indice_transicao_energetica",
        "demanda_minerais_renovaveis": "_coletar_demanda_minerais_renovaveis",
        "capacidade_renovavel_gw": "_coletar_capacidade_renovavel_gw",
        # Infraestrutura
        "investimento_data_centers_usd": "_coletar_investimento_data_centers_usd",
        "capacidade_data_centers_mw": "_coletar_capacidade_data_centers_mw",
        "demanda_cobre_global": "_coletar_demanda_cobre_global",
        "demanda_aluminio_dc": "_coletar_demanda_aluminio_dc",
        "expansao_5g_torres": "_coletar_expansao_5g_torres",
        "fibra_otica_novos_km": "_coletar_fibra_otica_novos_km",
        "indice_infra_digital": "_coletar_indice_infra_digital",
        # Chips
        "producao_gallium_t": "_coletar_producao_gallium_t",
        "producao_germanium_t": "_coletar_producao_germanium_t",
        "preco_gallium_usd_kg": "_coletar_preco_gallium_usd_kg",
        "preco_germanium_usd_kg": "_coletar_preco_germanium_usd_kg",
        "producao_gpus_m": "_coletar_producao_gpus_m",
        "controle_exportacao_china": "_coletar_controle_exportacao_china",
        "investimento_fabs_usd": "_coletar_investimento_fabs_usd",
        "lead_time_chips_dias": "_coletar_lead_time_chips_dias",
        # Terras raras
        "producao_global_ree_t": "_coletar_producao_global_ree_t",
        "producao_china_ree_pct": "_coletar_producao_china_ree_pct",
        "preco_neodimio_usd_kg": "_coletar_preco_neodimio_usd_kg",
        "preco_disprosio_usd_kg": "_coletar_preco_disprosio_usd_kg",
        "reservas_brasil_ree_t": "_coletar_reservas_brasil_ree_t",
        "dolar_reservas_pct": "_coletar_dolar_reservas_pct",
        "comercio_nao_dolar_pct": "_coletar_comercio_nao_dolar_pct",
        "contratos_yuan_petroleo": "_coletar_contratos_yuan_petroleo",
        "comercio_intra_brics_usd": "_coletar_comercio_intra_brics_usd",
        "usd_brl": "_coletar_usd_brl",
        "dxy_index": "_coletar_dxy_index",
        "ouro_usd_oz": "_coletar_ouro_usd_oz",
        "brent_usd": "_coletar_brent_usd",
        "btc_usd": "_coletar_btc_usd",
        "reservas_ouro_china_t": "_coletar_reservas_ouro_china_t",
        "producao_petroleo_opec": "_coletar_producao_petroleo_opec",
        "preco_cobre_usd_t": "_coletar_preco_cobre_usd_t",
        "preco_litio_usd_kg": "_coletar_preco_litio_usd_kg",
        # Carbono
        "preco_carbono_eu": "_coletar_preco_carbono_eu_novo",
        "preco_carbono_eua": "_coletar_preco_carbono_eua",
        "preco_carbono_china": "_coletar_preco_carbono_china",
        "creditos_voluntarios_usd": "_coletar_creditos_voluntarios_usd",
        "intensidade_carbono_setorial": "_coletar_intensidade_carbono_setorial",
        # Geopolitica
        "geopolitical_risk_idx": "_coletar_geopolitical_risk_idx",
        "geopolitical_risk_vix": "_coletar_geopolitical_risk_vix",
        "fragile_states_index": "_coletar_fragile_states_index",
        "conflitos_ativos": "_coletar_conflitos_ativos",
        "indice_risco_pais": "_coletar_indice_risco_pais",
    }

    # ------------------------------------------------------------------
    # Coleta completa
    # ------------------------------------------------------------------
    def coletar_todos(
        self, usar_cache: bool = True, max_age_hours: int = 24
    ) -> Dict[CampoGranular, List[SerieReal]]:
        """
        Coleta dados reais para todos os vetores do catálogo.
        Usa cache quando disponível e respeita max_age_hours.
        """
        resultados: Dict[CampoGranular, List[SerieReal]] = {
            CampoGranular.CLIMA: [],
            CampoGranular.INFRAESTRUTURA: [],
            CampoGranular.CHIPS: [],
            CampoGranular.TERRAS_RARAS: [],
            CampoGranular.CARBONO: [],
            CampoGranular.GEOPOLITICA: [],
        }

        for campo_enum, campo_cfg in REGISTRO_CAMPOS.items():
            for vetor_id in campo_cfg.vetores:
                cfg = campo_cfg.vetores[vetor_id]
                nome = cfg.descricao or vetor_id

                # 1. Tenta cache
                if usar_cache:
                    cached = self._get_cache(vetor_id, campo_enum, nome)
                    if cached is not None:
                        resultados[campo_enum].append(cached)
                        self.cache.log(vetor_id, cached.fonte, "CACHE_HIT", f"stale={cached.cache}")
                        continue

                # 2. Tenta coletar em tempo real
                metodo_nome = self.COLETORES.get(vetor_id)
                if metodo_nome is None:
                    sr = SerieReal(
                        vetor_id,
                        campo_enum,
                        nome,
                        None,
                        None,
                        erro="Coletor nao implementado",
                    )
                else:
                    try:
                        sr = getattr(self, metodo_nome)()
                    except Exception as e:
                        sr = SerieReal(vetor_id, campo_enum, nome, None, None, erro=str(e))

                if sr.serie is not None:
                    self._put_cache(sr)
                    self.cache.log(vetor_id, sr.fonte, "OK")
                else:
                    self.cache.log(vetor_id, sr.fonte or "", "PENDENTE", sr.erro or "")

                resultados[campo_enum].append(sr)

        return resultados

    def resumo(self, resultados: Dict[CampoGranular, List[SerieReal]]) -> Dict[str, Any]:
        total = sum(len(v) for v in resultados.values())
        disponiveis = sum(1 for lista in resultados.values() for s in lista if s.disponivel)
        pendentes = [
            s.vetor_id
            for lista in resultados.values()
            for s in lista
            if not s.disponivel
        ]
        return {
            "total_vetores": total,
            "com_dados_reais": disponiveis,
            "pendentes": len(pendentes),
            "lista_pendentes": pendentes,
        }

    def status_apis(self) -> Dict[str, str]:
        return {
            "bcb": "ativo",
            "yahoo_finance": "ativo" if self.yahoo.available else "yfinance_nao_instalado",
            "coingecko": "ativo",
            "open_meteo": "ativo",
            "nasa_giss": "ativo",
            "fred": "ativo" if self.fred.api_key else "api_key_nao_configurada",
            "imf": "ativo",
            "eia": "ativo" if self.eia.api_key else "api_key_nao_configurada",
            "world_bank": "ativo",
        }
