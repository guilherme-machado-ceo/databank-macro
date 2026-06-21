from __future__ import annotations
import uuid, hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
import numpy as np, pandas as pd

class EscopoEspacial(Enum):
    GLOBAL = "global"
    REGIONAL = "regional"
    NACIONAL = "national"
    LOCAL = "local"

class Granularidade(Enum):
    MACRO = "macro"
    MICRO = "micro"
    NANO = "nano"

@dataclass
class VetorEconomico:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    nome: str = ""
    simbolo: str = ""
    dimensao_temporal: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dimensao_espacial: EscopoEspacial = EscopoEspacial.GLOBAL
    dimensao_categoria: Any = None
    dimensao_granularidade: Granularidade = Granularidade.MACRO
    valor_bruto: float = 0.0
    valor_normalizado: float = 0.0
    volatilidade_20d: float = 0.0
    retorno_1d: float = 0.0
    sentimento: float = 0.0
    risco_pcq: float = 0.0
    confiabilidade_fonte: float = 0.8
    fonte: str = ""
    hash_provenance: str = ""
    lgpd_compliant: bool = False
    criptografado: bool = False
    id_custodia: Optional[str] = None
    _serie_historica: Optional[pd.Series] = field(default=None, repr=False)

    def __post_init__(self):
        if not self.nome: self.nome = self.simbolo or f"VETOR_{self.id}"
        if not self.hash_provenance and self._serie_historica is not None:
            self._calcular_hash()

    def _calcular_hash(self):
        if self._serie_historica is not None:
            self.hash_provenance = hashlib.sha3_256(self._serie_historica.to_json().encode()).hexdigest()

    @property
    def serie_historica(self): return self._serie_historica
    @serie_historica.setter
    def serie_historica(self, serie: pd.Series):
        self._serie_historica = serie; self._calcular_hash()

    def calcular_volatilidade(self, janela=20):
        if self._serie_historica is None or len(self._serie_historica) < janela: return 0.0
        lr = np.log(self._serie_historica / self._serie_historica.shift(1)).dropna()
        self.volatilidade_20d = float(lr.tail(janela).std() * np.sqrt(252))
        return self.volatilidade_20d

    def calcular_sentimento(self, referencia: float):
        if self.valor_bruto == 0 or referencia == 0: self.sentimento = 0.0; return 0.0
        self.sentimento = float(np.tanh(((self.valor_bruto - referencia) / referencia) * 5))
        return self.sentimento

    def calcular_risco_pcq(self, sensibilidade_cripto=0.5):
        from .campos_granulares import CampoGranular
        base = {CampoGranular.CHIPS: 0.7, CampoGranular.TERRAS_RARAS: 0.5,
                CampoGranular.INFRAESTRUTURA: 0.4, CampoGranular.CLIMA: 0.2}.get(self.dimensao_categoria, 0.3)
        self.risco_pcq = min(1.0, base + sensibilidade_cripto * self.volatilidade_20d)
        return self.risco_pcq

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "simbolo": self.simbolo,
                "valor_bruto": self.valor_bruto, "volatilidade_20d": self.volatilidade_20d,
                "sentimento": self.sentimento, "risco_pcq": self.risco_pcq,
                "fonte": self.fonte, "criptografado": self.criptografado,
                "id_custodia": self.id_custodia}

class CarteiraVetores:
    def __init__(self, nome="Carteira_Global"):
        self.nome = nome; self.vetores = {}; self._matriz_correlacao = None
    def adicionar(self, v): self.vetores[v.id] = v; self._matriz_correlacao = None
    def por_campo(self, campo): return [v for v in self.vetores.values() if v.dimensao_categoria == campo]
    def calcular_correlacao(self):
        series = {v.simbolo or v.id: v.serie_historica for v in self.vetores.values() if v.serie_historica is not None and len(v.serie_historica) > 10}
        if not series: return pd.DataFrame()
        self._matriz_correlacao = pd.DataFrame(series).corr(); return self._matriz_correlacao
    def indice_glocal(self):
        if not self.vetores: return 0.0
        return np.mean([v.valor_normalizado * (1 + v.sentimento) for v in self.vetores.values()])
    def to_dataframe(self): return pd.DataFrame([v.to_dict() for v in self.vetores.values()])
