#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import json
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from core.campos_granulares import REGISTRO_CAMPOS, total_vetores, CampoGranular
from core.vetor import CarteiraVetores, EscopoEspacial, Granularidade, VetorEconomico
from core.inflex import INFLEx
from core.anamorf import ANAMORF
from core.fluxus import FLUXUS
from ingestion.real_data import IngestorReal
from pcq.custodia import CustodiaPCQ
from mining.pcq_miner import PCQMiner


def serie_para_vetor(sr) -> VetorEconomico:
    """Converte SerieReal em VetorEconomico para o pipeline."""
    if sr.serie is None or sr.serie.empty:
        raise ValueError("Serie vazia nao pode virar vetor")
    v = VetorEconomico(
        nome=sr.nome,
        simbolo=sr.vetor_id,
        dimensao_categoria=sr.campo,
        dimensao_espacial=EscopoEspacial.GLOBAL,
        dimensao_granularidade=Granularidade.MACRO,
        valor_bruto=float(sr.serie.iloc[-1]),
        fonte=sr.fonte or "Fonte pendente",
        lgpd_compliant=True,
    )
    v.serie_historica = sr.serie
    v.calcular_volatilidade()
    v.calcular_sentimento(sr.serie.mean())
    v.calcular_risco_pcq()
    return v


def main():
    print("\n" + "=" * 70)
    print("  DATABANK PCQ — Coleta de Dados Reais")
    print("=" * 70 + "\n")

    ingestor = IngestorReal()
    print("Status das APIs:")
    for api, status in ingestor.status_apis().items():
        print(f"  • {api}: {status}")
    print()

    print("Coletando dados reais (e lendo cache quando disponivel)...\n")
    resultados = ingestor.coletar_todos(usar_cache=True, max_age_hours=24)
    resumo = ingestor.resumo(resultados)

    print(f"Total de vetores no catalogo: {resumo['total_vetores']}")
    print(f"Vetores com dados reais:      {resumo['com_dados_reais']}")
    print(f"Vetores pendentes:            {resumo['pendentes']}")
    print()

    # Detalhamento por campo
    for campo_enum, lista in resultados.items():
        disponiveis = [s for s in lista if s.disponivel]
        print(f"  {campo_enum.name}: {len(disponiveis)}/{len(lista)} com dados reais")
        for s in disponiveis:
            ultimo = s.serie.iloc[-1]
            print(f"    [OK] {s.vetor_id}: {ultimo:.4f} ({s.fonte})")
        for s in lista:
            if not s.disponivel:
                print(f"    [--] {s.vetor_id}: Fonte pendente — {s.erro}")
    print()

    # Apenas vetores reais entram no pipeline
    vetores = []
    for lista in resultados.values():
        for sr in lista:
            if sr.disponivel:
                try:
                    vetores.append(serie_para_vetor(sr))
                except Exception as e:
                    logging.warning(f"Erro ao converter {sr.vetor_id}: {e}")

    if not vetores:
        print("Nenhum vetor real disponivel. Rode novamente mais tarde ou verifique as APIs.")
        return

    print(f"\n{len(vetores)} vetores reais carregados no pipeline.\n")

    carteira = CarteiraVetores("Carteira_Real")
    for v in vetores:
        carteira.adicionar(v)
    print(f"Carteira: {len(carteira.vetores)} vetores REAIS")
    print(f"Indice Glocal: {carteira.indice_glocal():.4f}\n")

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
    mercado = {
        "bitcoin_reward": 150,
        "bitcoin_custo": 80,
        "ethereum_reward": 120,
        "ethereum_custo": 70,
        "algorand_reward": 80,
        "algorand_custo": 30,
        "qrl_reward": 60,
        "qrl_custo": 20,
        "solana_reward": 100,
        "solana_custo": 50,
    }
    for i, r in enumerate(miner.decidir(mercado), 1):
        print(f"    #{i} {r['chain_name']:20s} score={r['score']:>8.2f} risco_q={r['risco_quantico']:.2f}")

    print(f"\n{'=' * 70}")
    print("  DataBank Macro com DADOS REAIS: OK")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
