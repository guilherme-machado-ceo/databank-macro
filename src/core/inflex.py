from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)

@dataclass
class ResultadoINFLEx:
    vetor_id: str
    prob_inflexao: float
    direcao: int
    confianca: float
    vetores_paralelo: List[Dict]
    analogias_historicas: List[Dict]
    regime_atual: str = "unknown"
    campos_cascata: List[str] = field(default_factory=list)

class INFLEx:
    def __init__(self, carteira, threshold_cusum=2.0, threshold_fase=0.3, min_analogias=3):
        self.carteira = carteira
        self.threshold_cusum = threshold_cusum
        self.threshold_fase = threshold_fase
        self.min_analogias = min_analogias
        self.memoria_analogica = []
        self._cache_fase = {}

    def detectar_inflexao(self, vetor_alvo, janela=60):
        from .campos_granulares import get_sensibilidade, MAPA_CASCATA
        if vetor_alvo.serie_historica is None or len(vetor_alvo.serie_historica) < janela:
            return ResultadoINFLEx(vetor_id=vetor_alvo.id, prob_inflexao=0.0, direcao=0, confianca=0.0, vetores_paralelo=[], analogias_historicas=[], regime_atual="dados_insuficientes")

        serie = vetor_alvo.serie_historica.tail(janela).dropna().values
        if len(serie) < 20:
            return ResultadoINFLEx(vetor_id=vetor_alvo.id, prob_inflexao=0.0, direcao=0, confianca=0.0, vetores_paralelo=[], analogias_historicas=[], regime_atual="insuficiente")

        log_ret = np.diff(np.log(serie))
        mu = np.mean(log_ret[:-10]); sigma = np.std(log_ret[:-10]) + 1e-9
        cusum_pos = np.zeros(len(log_ret[-10:])); cusum_neg = np.zeros(len(log_ret[-10:]))
        for i in range(1, len(log_ret[-10:])):
            cusum_pos[i] = max(0, cusum_pos[i-1] + log_ret[-10:][i] - mu - 0.5 * sigma)
            cusum_neg[i] = max(0, cusum_neg[i-1] - (log_ret[-10:][i] - mu) - 0.5 * sigma)
        zscore = max(np.max(cusum_pos), np.max(cusum_neg)) / (sigma * np.sqrt(len(log_ret[-10:])))

        threshold_campo = get_sensibilidade(vetor_alvo.dimensao_categoria)
        if zscore > self.threshold_cusum: regime = "transicao"
        elif np.mean(log_ret[-10:]) > mu + threshold_campo * sigma: regime = "tendencia_alta"
        elif np.mean(log_ret[-10:]) < mu - threshold_campo * sigma: regime = "tendencia_baixa"
        else: regime = "estavel"

        prob = min(zscore / 5.0, 1.0) if regime == "transicao" else 0.1
        direcao = 1 if regime == "tendencia_alta" else (-1 if regime == "tendencia_baixa" else 0)
        confianca = min(prob + 0.3, 1.0)

        campos_cascata = [c.name for c in MAPA_CASCATA.get(vetor_alvo.dimensao_categoria, [])]

        return ResultadoINFLEx(vetor_id=vetor_alvo.id, prob_inflexao=prob, direcao=direcao, confianca=confianca, vetores_paralelo=[], analogias_historicas=[], regime_atual=regime, campos_cascata=campos_cascata)

    def registrar_evento(self, vetor, resultado_inflexao, delta_t, magnitude):
        self.memoria_analogica.append({"vetor_id": vetor.id, "resultado": resultado_inflexao, "magnitude": magnitude})
