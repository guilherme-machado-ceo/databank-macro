"""
DataBank PCQ — Real Data Connector
====================================
Integra APIs gratuitas para dados econômicos reais.
Fallback para simulação apenas se API falhar.

APIs: BCB (BR), yfinance (global), CoinGecko (crypto), Open-Meteo (clima)

Autor: Guilherme Gonçalves Machado | Hubstry Deep Tech
"""
from __future__ import annotations

import logging
import time
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import requests
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================
# BCB - BANCO CENTRAL DO BRASIL (API Oficial, Gratuita)
# ============================================================
class BCBConnector:
    """Conector BCB para dados brasileiros reais."""
    BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs."

    def fetch_usd_brl(self, dias: int = 120) -> Optional[pd.Series]:
        """Taxa de câmbio USD/BRL (série 1 do BCB)."""
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
            df = df.set_index("data").sort_index()
            return df["valor"]
        except Exception as e:
            logger.warning(f"BCB USD/BRL falhou: {e}")
            return None

    def fetch_selic(self, dias: int = 120) -> Optional[pd.Series]:
        """Taxa SELIC (série 432)."""
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


# ============================================================
# YAHOO FINANCE (via yfinance)
# ============================================================
class YahooFinanceConnector:
    """Conector Yahoo Finance para ações, commodities, índices."""

    def __init__(self):
        try:
            import yfinance as yf
            self.yf = yf
            self.available = True
        except ImportError:
            logger.warning("yfinance não instalado. Use: pip install yfinance")
            self.available = False

    def fetch_ticker(self, ticker: str, period: str = "6mo") -> Optional[pd.Series]:
        """Busca série temporal de um ticker."""
        if not self.available:
            return None
        try:
            time.sleep(0.5)  # Rate limit gentil
            data = self.yf.Ticker(ticker).history(period=period)
            if data.empty:
                return None
            return data["Close"]
        except Exception as e:
            logger.warning(f"Yahoo Finance {ticker} falhou: {e}")
            return None

    def fetch_commodities(self) -> Dict[str, pd.Series]:
        """Busca commodities principais."""
        tickers = {
            "ouro": "GC=F",      # Gold Futures
            "brent": "BZ=F",     # Brent Oil Futures
            "cobre": "HG=F",     # Copper Futures
            "prata": "SI=F",     # Silver Futures
        }
        resultados = {}
        for nome, ticker in tickers.items():
            serie = self.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                resultados[nome] = serie
        return resultados

    def fetch_indices(self) -> Dict[str, pd.Series]:
        """Busca índices globais."""
        tickers = {
            "sp500": "^GSPC",
            "ibovespa": "^BVSP",
            "dxy": "DX-Y.NYB",  # Dollar Index
            "nasdaq": "^IXIC",
        }
        resultados = {}
        for nome, ticker in tickers.items():
            serie = self.fetch_ticker(ticker, period="6mo")
            if serie is not None:
                resultados[nome] = serie
        return resultados


# ============================================================
# COINGECKO (Crypto - API gratuita)
# ============================================================
class CoinGeckoConnector:
    """Conector CoinGecko para criptomoedas."""
    BASE_URL = "https://api.coingecko.com/api/v3"

    def fetch_price_history(self, coin_id: str = "bitcoin", dias: int = 120) -> Optional[pd.Series]:
        """Histórico de preço de uma criptomoeda."""
        try:
            url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
            params = {"vs_currency": "usd", "days": str(dias)}
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            prices = dados["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("timestamp").sort_index()
            return df["price"]
        except Exception as e:
            logger.warning(f"CoinGecko {coin_id} falhou: {e}")
            return None

    def fetch_multiple(self, coins: List[str] = None) -> Dict[str, pd.Series]:
        """Busca múltiplas criptomoedas."""
        if coins is None:
            coins = ["bitcoin", "ethereum", "solana"]
        resultados = {}
        for coin in coins:
            serie = self.fetch_price_history(coin, dias=120)
            if serie is not None:
                resultados[coin] = serie
            time.sleep(1.5)  # Rate limit CoinGecko gratuito
        return resultados


# ============================================================
# OPEN-METEO (Clima - 100% gratuito)
# ============================================================
class OpenMeteoConnector:
    """Conector Open-Meteo para dados climáticos."""
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def fetch_climate(self, lat: float, lon: float, days: int = 120) -> Optional[pd.DataFrame]:
        """Busca dados climáticos (temperatura, precipitação)."""
        try:
            params = {
                "latitude": lat, "longitude": lon,
                "daily": ["temperature_2m_max", "precipitation_sum"],
                "past_days": days, "timezone": "auto",
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            if "daily" not in dados:
                return None
            df = pd.DataFrame(dados["daily"])
            df["time"] = pd.to_datetime(df["time"])
            return df.set_index("time")
        except Exception as e:
            logger.warning(f"Open-Meteo falhou: {e}")
            return None


# ============================================================
# ALPHA VANTAGE (Forex, commodities - 25 calls/dia)
# ============================================================
class AlphaVantageConnector:
    """Conector Alpha Vantage (requer API key)."""
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo"

    def fetch_forex(self, from_sym: str = "USD", to_sym: str = "BRL") -> Optional[pd.Series]:
        """Par de moedas forex."""
        try:
            params = {
                "function": "FX_DAILY", "from_symbol": from_sym,
                "to_symbol": to_sym, "apikey": self.api_key, "outputsize": "compact",
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            if "Time Series FX (Daily)" not in dados:
                return None
            ts = dados["Time Series FX (Daily)"]
            df = pd.DataFrame(ts).T
            df.index = pd.to_datetime(df.index)
            return df["4. close"].astype(float).sort_index()
        except Exception as e:
            logger.warning(f"Alpha Vantage {from_sym}/{to_sym} falhou: {e}")
            return None


# ============================================================
# ORQUESTRADOR - Dados Reais para os 4 Campos
# ============================================================
class IngestorReal:
    """
    Orquestrador de ingestão de dados REAIS para os 4 Campos Granulares.
    Se API falhar, retorna None (não simula - o pipeline deve lidar com isso).
    """

    def __init__(self, alpha_vantage_key: Optional[str] = None):
        self.bcb = BCBConnector()
        self.yahoo = YahooFinanceConnector()
        self.coingecko = CoinGeckoConnector()
        self.meteo = OpenMeteoConnector()
        self.alpha = AlphaVantageConnector(alpha_vantage_key)

    def coletar_campo_classico(self) -> Dict[str, pd.Series]:
        """CAMPO I: Dados clássicos reais (câmbio, commodities, índices)."""
        dados = {}

        # USD/BRL via BCB (prioridade - dados oficiais brasileiros)
        usd_brl = self.bcb.fetch_usd_brl(dias=120)
        if usd_brl is not None:
            dados["usd_brl"] = usd_brl
            logger.info(f"BCB USD/BRL: {len(usd_brl)} pontos")

        # SELIC via BCB
        selic = self.bcb.fetch_selic(dias=120)
        if selic is not None:
            dados["selic"] = selic

        # Commodities via Yahoo Finance
        commodities = self.yahoo.fetch_commodities()
        for nome, serie in commodities.items():
            dados[nome] = serie
            logger.info(f"Yahoo {nome}: {len(serie)} pontos")

        # Índices via Yahoo Finance
        indices = self.yahoo.fetch_indices()
        for nome, serie in indices.items():
            dados[nome] = serie
            logger.info(f"Yahoo {nome}: {len(serie)} pontos")

        # DXY via Alpha Vantage (se tiver key)
        if self.alpha.api_key != "demo":
            dxy = self.alpha.fetch_forex("USD", "BRL")
            if dxy is not None:
                dados["dxy_proxy"] = dxy

        return dados

    def coletar_campo_tecnologico(self) -> Dict[str, pd.Series]:
        """CAMPO II: Dados tecnológicos reais (semicondutores, chips)."""
        dados = {}

        # NVIDIA como proxy para semicondutores/IA
        nvda = self.yahoo.fetch_ticker("NVDA", period="6mo")
        if nvda is not None:
            dados["nvidia_proxy_chips"] = nvda
            logger.info(f"Yahoo NVDA: {len(nvda)} pontos")

        # AMD
        amd = self.yahoo.fetch_ticker("AMD", period="6mo")
        if amd is not None:
            dados["amd_proxy_chips"] = amd

        # TSMC (ADR)
        tsm = self.yahoo.fetch_ticker("TSM", period="6mo")
        if tsm is not None:
            dados["tsmc_proxy_chips"] = tsm

        # VanEck Semiconductor ETF (SMH) como índice de chips
        smh = self.yahoo.fetch_ticker("SMH", period="6mo")
        if smh is not None:
            dados["smh_etf_chips"] = smh
            logger.info(f"Yahoo SMH (semiconductor ETF): {len(smh)} pontos")

        return dados

    def coletar_campo_geopolitico(self) -> Dict[str, pd.Series]:
        """CAMPO III: Dados geopolíticos e monetários reais."""
        dados = {}

        # Bitcoin como proxy para desdolarização/ativos alternativos
        cryptos = self.coingecko.fetch_multiple(["bitcoin", "ethereum"])
        for nome, serie in cryptos.items():
            dados[f"crypto_{nome}"] = serie
            logger.info(f"CoinGecko {nome}: {len(serie)} pontos")

        # Ouro como reserva de valor
        ouro = self.yahoo.fetch_ticker("GC=F", period="6mo")
        if ouro is not None:
            dados["ouro_futuros"] = ouro

        return dados

    def coletar_campo_climatico(self) -> Dict[str, pd.Series]:
        """CAMPO IV: Dados climáticos reais."""
        dados = {}

        # São Paulo (lat=-23.55, lon=-46.63)
        clima_sp = self.meteo.fetch_climate(-23.55, -46.63, days=120)
        if clima_sp is not None and "temperature_2m_max" in clima_sp.columns:
            dados["temperatura_max_sp"] = clima_sp["temperature_2m_max"]
            logger.info(f"Open-Meteo SP: {len(clima_sp)} pontos")

        # Cuiabá (agricultura, centro-oeste)
        clima_cba = self.meteo.fetch_climate(-15.60, -56.10, days=120)
        if clima_cba is not None and "temperature_2m_max" in clima_cba.columns:
            dados["temperatura_max_cuiaba"] = clima_cba["temperature_2m_max"]

        return dados

    def coletar_todos(self) -> Dict[str, Dict[str, pd.Series]]:
        """Coleta dados reais de todos os 4 campos."""
        logger.info("=" * 60)
        logger.info("INICIANDO COLETA DE DADOS REAIS")
        logger.info("=" * 60)

        dados = {
            "classicos": self.coletar_campo_classico(),
            "tecnologicos": self.coletar_campo_tecnologico(),
            "geopoliticos": self.coletar_campo_geopolitico(),
            "climaticos": self.coletar_campo_climatico(),
        }

        total = sum(len(v) for v in dados.values())
        logger.info(f"=" * 60)
        logger.info(f"COLETA CONCLUÍDA: {total} séries reais coletadas")
        logger.info(f"=" * 60)

        return dados

    def status(self) -> Dict[str, Any]:
        """Status das conexões de APIs."""
        return {
            "bcb": "ativo",
            "yahoo_finance": "ativo" if self.yahoo.available else "yfinance_nao_instalado",
            "coingecko": "ativo",
            "open_meteo": "ativo",
            "alpha_vantage": "ativo" if self.alpha.api_key != "demo" else "demo_mode",
        }
