from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerfilBlockchain:
    chain: str; algoritmo: str; risco_quantico: float; migracao_pqc: bool; recomendacao: str

PERFIS = {
    "bitcoin": PerfilBlockchain("Bitcoin", "ECDSA", 0.75, False, "minerar_com_precaucao"),
    "ethereum": PerfilBlockchain("Ethereum", "ECDSA", 0.70, False, "monitorar"),
    "algorand": PerfilBlockchain("Algorand", "EdDSA+FALCON", 0.30, True, "minerar"),
    "qrl": PerfilBlockchain("QRL", "XMSS (hash-based)", 0.0, True, "minerar"),
    "solana": PerfilBlockchain("Solana", "EdDSA", 0.65, False, "monitorar"),
}

class PCQMiner:
    def __init__(self): self.perfis = PERFIS

    def decidir(self, dados_mercado: dict) -> List[dict]:
        rankings = []
        for chain_id, perfil in self.perfis.items():
            reward = dados_mercado.get(f"{chain_id}_reward", 100)
            custo = dados_mercado.get(f"{chain_id}_custo", 50)
            lucro = reward - custo
            fator_q = 1.0 - (perfil.risco_quantico * 0.5)
            rankings.append({"chain": chain_id, "chain_name": perfil.chain, "score": round(lucro * fator_q, 2), "lucro_base": round(lucro, 2), "fator_quantico": round(fator_q, 3), "risco_quantico": perfil.risco_quantico, "algoritmo": perfil.algoritmo, "migracao_pqc": perfil.migracao_pqc, "recomendacao": perfil.recomendacao})
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return rankings

    def risco_carteira(self, carteira: Dict[str, float]) -> dict:
        total = sum(carteira.values())
        risco_ponderado = sum(self.perfis.get(c).risco_quantico * (v / total) for c, v in carteira.items() if c in self.perfis) if total > 0 else 0
        return {"risco_total": round(risco_ponderado, 4), "valor_total": total, "classificacao": "CRITICO" if risco_ponderado > 0.5 else "ALTO" if risco_ponderado > 0.3 else "MODERADO" if risco_ponderado > 0.15 else "BAIXO"}
