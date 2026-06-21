from __future__ import annotations
from typing import List, Dict, Optional
from enum import Enum
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

class TipoAnalogia(Enum):
    HEURISTICA = "heuristica"
    FUNCIONAL = "funcional"
    HOMOLOGIA = "homologia"

class ANAMORF:
    def __init__(self, carteira, dim_embedding=8, n_neighbors=5):
        self.carteira = carteira; self.dim_embedding = dim_embedding
        self.n_neighbors = n_neighbors; self.scaler = StandardScaler()
        self.pca = PCA(n_components=dim_embedding); self.nn = None
        self._embeddings = {}; self._vetor_ids = []; self._is_fitted = False

    def fit(self):
        vetores_validos = [v for v in self.carteira.vetores.values() if v.serie_historica is not None and len(v.serie_historica) >= 20]
        if len(vetores_validos) < 5: self._is_fitted = False; return
        self._vetor_ids = [v.id for v in vetores_validos]
        features = np.array([self._extrair_features(v) for v in vetores_validos])
        features_scaled = self.scaler.fit_transform(features)
        n_comp = min(self.dim_embedding, features.shape[1], len(vetores_validos) - 1)
        self.pca = PCA(n_components=n_comp); embeddings = self.pca.fit_transform(features_scaled)
        self._embeddings = {vid: emb for vid, emb in zip(self._vetor_ids, embeddings)}
        self.nn = NearestNeighbors(n_neighbors=min(self.n_neighbors, len(vetores_validos)), metric="euclidean")
        self.nn.fit(embeddings); self._is_fitted = True

    def _extrair_features(self, vetor):
        serie = vetor.serie_historica.dropna().values
        if len(serie) < 10: return np.zeros(20)
        log_ret = np.diff(np.log(serie + 1e-9))
        feat = [np.mean(serie), np.std(serie), np.min(serie), np.max(serie), np.percentile(serie, 25), np.percentile(serie, 75), np.mean(log_ret), np.std(log_ret), np.max(log_ret), np.min(log_ret)]
        feat.extend([float((np.mean(serie) - np.median(serie)) / (np.std(serie) + 1e-9)), float(np.percentile(serie, 90) / (np.percentile(serie, 10) + 1e-9))])
        if len(serie) >= 32:
            fft = np.abs(np.fft.rfft(serie)); dom_freq = np.argmax(fft[1:]) + 1 if len(fft) > 1 else 0
            feat.extend([float(dom_freq / len(serie)), float(np.sum(fft[:5]) / (np.sum(fft) + 1e-9))])
        else: feat.extend([0.0, 0.0])
        feat.extend([vetor.sentimento, vetor.risco_pcq, vetor.volatilidade_20d, vetor.confiabilidade_fonte, float(vetor.lgpd_compliant), float(vetor.criptografado)])
        return np.array(feat, dtype=np.float64)

    def operar(self, confianca_minima=0.3):
        if not self._is_fitted: return []
        pares = [(v.dimensao_categoria.name if hasattr(v.dimensao_categoria, 'name') else str(v.dimensao_categoria), v.nome, v.serie_historica.values) for v in self.carteira.vetores.values() if v.serie_historica is not None and len(v.serie_historica) >= 20]
        resultados = []
        for i, (c1, v1, s1) in enumerate(pares):
            for c2, v2, s2 in pares[i+1:]:
                if c1 == c2: continue
                n = min(len(s1), len(s2))
                if n < 10: continue
                a, b = s1[-n:], s2[-n:]
                if np.std(a) < 1e-10 or np.std(b) < 1e-10: continue
                corr = float(np.corrcoef(a, b)[0, 1])
                if abs(corr) >= 0.3:
                    confianca = abs(corr) * 0.7
                    if confianca >= confianca_minima:
                        resultados.append({"tipo": TipoAnalogia.HEURISTICA.value, "campo_fonte": c1, "vetor_fonte": v1, "campo_alvo": c2, "vetor_alvo": v2, "correlacao": round(corr, 4), "confianca": round(confianca, 4)})
        resultados.sort(key=lambda x: x["confianca"], reverse=True)
        return resultados
