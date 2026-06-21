from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import numpy as np

@dataclass
class AtivoDados:
    id: str; nome: str; descricao: str; composicao: List[str]; pesos: Dict[str, float]
    score_inflexao: float; score_confianca: float; valor_estimado: float
    risco_agregado: float; campo_dominante: str
    timestamp_criacao: datetime = field(default_factory=datetime.now)
    id_custodia: Optional[str] = None; tokenizado: bool = False
    def valuation(self): return self.valor_estimado * (1 + self.score_inflexao) * (1 - self.risco_agregado * 0.5)
    def to_dict(self): return {"id": self.id, "nome": self.nome, "score_inflexao": self.score_inflexao, "score_confianca": self.score_confianca, "valor_estimado": self.valor_estimado, "risco_agregado": self.risco_agregado, "valuation": self.valuation()}

@dataclass
class ResultadoCiclo:
    timestamp: datetime; n_novos_vetores: int; n_estudos: int; n_ativos_criados: int
    receita_gerada: float; ativos: List[AtivoDados]; estudos: List[Dict]; metricas_memoria: Dict; indice_glocal: float

class FLUXUS:
    def __init__(self, carteira, inflex, anamorf, prob_min_inflexao=0.6, confianca_min=0.5):
        self.carteira = carteira; self.inflex = inflex; self.anamorf = anamorf
        self.prob_min_inflexao = prob_min_inflexao; self.confianca_min = confianca_min
        self._ativos_emitidos = []; self._receita_acumulada = 0.0

    def ciclo(self, novos_dados=None):
        ts = datetime.now()
        n_novos = len(novos_dados) if novos_dados else 0
        for v in (novos_dados or []): self.carteira.adicionar(v)

        estudos = []
        for vetor in self.carteira.vetores.values():
            if vetor.serie_historica is None or len(vetor.serie_historica) < 30: continue
            res = self.inflex.detectar_inflexao(vetor, janela=60)
            estudos.append({"vetor_id": vetor.id, "nome": vetor.nome, "campo": str(vetor.dimensao_categoria), "inflexao": {"prob": res.prob_inflexao, "direcao": res.direcao, "confianca": res.confianca, "regime": res.regime_atual, "campos_cascata": res.campos_cascata}})

        ativos = []
        for estudo in estudos:
            prob = estudo["inflexao"]["prob"]; conf = estudo["inflexao"]["confianca"]; direcao = estudo["inflexao"]["direcao"]
            if prob < self.prob_min_inflexao or conf < self.confianca_min or direcao == 0: continue
            vetor = self.carteira.vetores.get(estudo["vetor_id"])
            if not vetor: continue
            ativo = AtivoDados(id=f"ATV-{vetor.id}-{ts.strftime('%Y%m%d%H%M%S')}", nome=f"Indice {vetor.nome} — Inflexao {'Alta' if direcao > 0 else 'Baixa'}", descricao=f"Ativo composto. Prob: {prob:.1%}. Conf: {conf:.1%}.", composicao=[vetor.id], pesos={vetor.id: 1.0}, score_inflexao=prob * direcao, score_confianca=conf, valor_estimado=vetor.valor_bruto, risco_agregado=vetor.risco_pcq, campo_dominante=str(vetor.dimensao_categoria))
            ativos.append(ativo); self._ativos_emitidos.append(ativo)

        receita = sum(a.valuation() * 0.15 for a in ativos)
        self._receita_acumulada += receita

        return ResultadoCiclo(timestamp=ts, n_novos_vetores=n_novos, n_estudos=len(estudos), n_ativos_criados=len(ativos), receita_gerada=receita, ativos=ativos, estudos=estudos, metricas_memoria={"total": len(self._ativos_emitidos)}, indice_glocal=self.carteira.indice_glocal())

    def estatisticas(self):
        return {"ativos_emitidos": len(self._ativos_emitidos), "receita_acumulada": self._receita_acumulada, "n_vetores_carteira": len(self.carteira.vetores)}
