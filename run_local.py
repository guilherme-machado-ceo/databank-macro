#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging, time, json
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

import numpy as np
import pandas as pd
from datetime import datetime, timezone

from core.campos_granulares import REGISTRO_CAMPOS, total_vetores, CampoGranular
from core.vetor import VetorEconomico, EscopoEspacial, Granularidade, CarteiraVetores
from core.inflex import INFLEx
from core.anamorf import ANAMORF
from core.fluxus import FLUXUS
from pcq.custodia import CustodiaPCQ
from mining.pcq_miner import PCQMiner

# =========================================================
# APIs REAIS
# =========================================================
import requests

def fetch_bcb_usd_brl(dias=120):
    try:
        from datetime import datetime, timedelta
        end = datetime.now().strftime("%d/%m/%Y")
        start = (datetime.now() - timedelta(days=dias)).strftime("%d/%m/%Y")
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial={start}&dataFinal={end}"
        r = requests.get(url, timeout=30)
        df = pd.DataFrame(r.json())
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        return df.set_index("data")["valor"].astype(float).sort_index()
    except Exception as e:
        logging.warning(f"BCB falhou: {e}")
        return None

def fetch_yahoo(ticker, period="6mo"):
    try:
        import yfinance as yf
        import time as tm
        tm.sleep(0.5)
        data = yf.Ticker(ticker).history(period=period)
        return data["Close"] if not data.empty else None
    except Exception as e:
        logging.warning(f"Yahoo {ticker} falhou: {e}")
        return None

def fetch_coingecko(coin="bitcoin", dias=120):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
        r = requests.get(url, params={"vs_currency":"usd","days":str(dias)}, timeout=30)
        prices = r.json()["prices"]
        df = pd.DataFrame(prices, columns=["ts","price"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        return df.set_index("ts")["price"].sort_index()
    except Exception as e:
        logging.warning(f"CoinGecko {coin} falhou: {e}")
        return None

def fetch_meteo(lat, lon, days=120):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        r = requests.get(url, params={"latitude":lat,"longitude":lon,"daily":["temperature_2m_max"],"past_days":days,"timezone":"auto"}, timeout=30)
        df = pd.DataFrame(r.json()["daily"])
        df["time"] = pd.to_datetime(df["time"])
        return df.set_index("time")["temperature_2m_max"].sort_index()
    except Exception as e:
        logging.warning(f"Open-Meteo falhou: {e}")
        return None

# =========================================================
# MAIN
# =========================================================
def main():
    print("\n" + "=" * 70)
    print("  DATABANK PCQ v3 — Fusion Edition [DADOS REAIS]")
    print("  Post-Quantum Custody · Harvest Now, Decrypt Later")
    print("=" * 70 + "\n")

    print("  Coletando dados REAIS das APIs...\n")

    # Coleta real
    series_reais = {}

    # BCB
    usd_brl = fetch_bcb_usd_brl(120)
    if usd_brl is not None:
        series_reais["usd_brl"] = ("BCB", usd_brl)
        print(f"  [OK] BCB USD/BRL: {len(usd_brl)} pontos")

    # Yahoo Finance
    for nome, tick in [("ouro","GC=F"),("brent","BZ=F"),("cobre","HG=F"),("nvda","NVDA"),("amd","AMD"),("sp500","^GSPC"),("ibovespa","^BVSP")]:
        s = fetch_yahoo(tick)
        if s is not None:
            series_reais[nome] = ("Yahoo", s)
            print(f"  [OK] Yahoo {nome.upper()}: {len(s)} pontos")

    # CoinGecko
    btc = fetch_coingecko("bitcoin", 120)
    if btc is not None:
        series_reais["btc"] = ("CoinGecko", btc)
        print(f"  [OK] CoinGecko BTC: {len(btc)} pontos")

    # Open-Meteo
    temp_sp = fetch_meteo(-23.55, -46.63, 120)
    if temp_sp is not None:
        series_reais["temp_sp"] = ("Open-Meteo", temp_sp)
        print(f"  [OK] Open-Meteo SP: {len(temp_sp)} pontos")

    total_reais = len(series_reais)
    print(f"\n  TOTAL: {total_reais} series REAIS coletadas\n")

    # Converter para VetorEconomico
    campo_map = {
        "usd_brl": CampoGranular.TERRAS_RARAS, "ouro": CampoGranular.TERRAS_RARAS,
        "brent": CampoGranular.TERRAS_RARAS, "cobre": CampoGranular.TERRAS_RARAS,
        "btc": CampoGranular.TERRAS_RARAS, "nvda": CampoGranular.CHIPS,
        "amd": CampoGranular.CHIPS, "sp500": CampoGranular.TERRAS_RARAS,
        "ibovespa": CampoGranular.TERRAS_RARAS, "temp_sp": CampoGranular.CLIMA,
    }

    vetores = []
    for nome, (fonte, serie) in series_reais.items():
        campo = campo_map.get(nome, CampoGranular.TERRAS_RARAS)
        v = VetorEconomico(nome=nome.upper(), simbolo=nome, dimensao_categoria=campo,
                          dimensao_espacial=EscopoEspacial.GLOBAL, dimensao_granularidade=Granularidade.MACRO,
                          valor_bruto=float(serie.iloc[-1]), fonte=fonte, lgpd_compliant=True)
        v.serie_historica = serie
        v.calcular_volatilidade(); v.calcular_sentimento(serie.mean()); v.calcular_risco_pcq()
        vetores.append(v)

    # Carteira
    carteira = CarteiraVetores("Carteira_Real")
    for v in vetores: carteira.adicionar(v)
    print(f"  Carteira: {len(carteira.vetores)} vetores REAIS")
    print(f"  Indice Glocal: {carteira.indice_glocal():.4f}\n")

    # FLUXUS
    inicio = time.time()
    inflex = INFLEx(carteira)
    anamorf = ANAMORF(carteira)
    fluxus = FLUXUS(carteira, inflex, anamorf, prob_min_inflexao=0.05, confianca_min=0.1)
    resultado = fluxus.ciclo()

    print(f"{'=' * 70}")
    print("  RESULTADO COM DADOS REAIS")
    print(f"{'=' * 70}")
    print(f"  Fase 1 — Pesquisa:     {resultado.n_novos_vetores} novos")
    print(f"  Fase 2 — Estudo:       {resultado.n_estudos} analisados")
    print(f"  Fase 3 — Criacao:      {resultado.n_ativos_criados} ativos")
    print(f"  Fase 4 — Ensino:       {resultado.metricas_memoria['total']} eventos")
    print(f"  Fase 5 — Producao:     R$ {resultado.receita_gerada:,.2f}")
    print(f"  Indice Glocal:         {resultado.indice_glocal:.4f}")
    print(f"  Tempo:                 {time.time() - inicio:.2f}s")
    print(f"{'=' * 70}")

    if fluxus._ativos_emitidos:
        print("\n  TOP ATIVOS:")
        for a in fluxus._ativos_emitidos[:5]:
            print(f"    • {a.nome} (Valuation: R$ {a.valuation():,.2f})")

    # PCQ
    print(f"\n{'=' * 70}")
    print("  PROTECAO PCQ")
    print(f"{'=' * 70}")
    custodia = CustodiaPCQ(modo="classico")
    for a in fluxus._ativos_emitidos[:3]:
        rel = custodia.proteger(a.id, json.dumps(a.to_dict()).encode(), {"sensibilidade": "confidencial"})
        print(f"    {a.id}: {rel.algoritmo_kem} | {rel.validade_anos} anos | HNDL={rel.hndl_safe}")

    # Mineracao
    print(f"\n{'=' * 70}")
    print("  MINERACAO PCQ")
    print(f"{'=' * 70}")
    miner = PCQMiner()
    mercado = {"bitcoin_reward": 150, "bitcoin_custo": 80, "ethereum_reward": 120, "ethereum_custo": 70, "algorand_reward": 80, "algorand_custo": 30, "qrl_reward": 60, "qrl_custo": 20, "solana_reward": 100, "solana_custo": 50}
    for i, r in enumerate(miner.decidir(mercado), 1):
        print(f"    #{i} {r['chain_name']:20s} score={r['score']:>8.2f} risco_q={r['risco_quantico']:.2f}")

    print(f"\n{'=' * 70}")
    print("  DataBank PCQ v3 com DADOS REAIS: OK")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    main()
