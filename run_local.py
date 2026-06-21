#!/usr/bin/env python3
import sys, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.campos_granulares import REGISTRO_CAMPOS, total_vetores
from core.vetor import CarteiraVetores
from core.inflex import INFLEx
from core.anamorf import ANAMORF
from core.fluxus import FLUXUS
from pcq.custodia import CustodiaPCQ
from mining.pcq_miner import PCQMiner
from ingestion.data_generator import gerar_dados_correlacionados, dados_para_vetores

def main():
    print("\n" + "=" * 70)
    print("  DATABANK PCQ v3 — Fusion Edition")
    print("  Post-Quantum Custody · Harvest Now, Decrypt Later")
    print("=" * 70 + "\n")

    print(f"  Campos granulares: {len(REGISTRO_CAMPOS)}")
    for nome, campo in REGISTRO_CAMPOS.items():
        print(f"    {nome.name}: {len(campo.vetores)} vetores")
    print(f"  Total: {total_vetores()}\n")

    print("  Gerando dados simulados (120 dias, 41 vetores)...")
    dados = gerar_dados_correlacionados(dias=120, seed=42)
    vetores = dados_para_vetores(dados)
    print(f"  OK: {len(vetores)} vetores instanciados\n")

    carteira = CarteiraVetores("Carteira_Glocal_Fusion")
    for v in vetores: carteira.adicionar(v)
    print(f"  Carteira: {len(carteira.vetores)} vetores")
    print(f"  Indice Glocal: {carteira.indice_glocal():.4f}\n")

    inicio = time.time()
    inflex = INFLEx(carteira)
    anamorf = ANAMORF(carteira)
    fluxus = FLUXUS(carteira, inflex, anamorf)

    print("  Executando ciclo FLUXUS v3...")
    resultado = fluxus.ciclo()

    print(f"\n{'=' * 70}")
    print("  RESULTADO")
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

    print(f"\n{'=' * 70}")
    print("  PROTECAO PCQ (HNDL)")
    print(f"{'=' * 70}")
    custodia = CustodiaPCQ(modo="classico")
    for a in fluxus._ativos_emitidos[:3]:
        rel = custodia.proteger(a.id, json.dumps(a.to_dict()).encode(), {"sensibilidade": "confidencial"})
        print(f"    {a.id}: {rel.algoritmo_kem} | {rel.validade_anos} anos | HNDL={rel.hndl_safe}")

    print(f"\n{'=' * 70}")
    print("  MINERACAO PCQ")
    print(f"{'=' * 70}")
    miner = PCQMiner()
    mercado = {"bitcoin_reward": 150, "bitcoin_custo": 80, "ethereum_reward": 120, "ethereum_custo": 70, "algorand_reward": 80, "algorand_custo": 30, "qrl_reward": 60, "qrl_custo": 20, "solana_reward": 100, "solana_custo": 50}
    for i, r in enumerate(miner.decidir(mercado), 1):
        print(f"    #{i} {r['chain_name']:20s} score={r['score']:>8.2f} risco_q={r['risco_quantico']:.2f}")

    print(f"\n{'=' * 70}")
    print("  DataBank PCQ v3 Fusion: OK")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    main()
