from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict
from datetime import datetime
from src.core.campos_granulares import REGISTRO_CAMPOS
from src.core.vetor import VetorEconomico, EscopoEspacial, Granularidade

def gerar_dados_correlacionados(dias: int = 120, seed: int = 42) -> Dict[str, Dict[str, np.ndarray]]:
    rng = np.random.default_rng(seed)
    dados = {}
    choque = np.cumsum(rng.normal(0, 0.5, dias))
    for campo_enum, campo_cfg in REGISTRO_CAMPOS.items():
        dados[campo_enum.name] = {}
        for i, (vetor_nome, cfg) in enumerate(campo_cfg.vetores.items()):
            base = 50 + rng.uniform(0, 150)
            tendencia = rng.uniform(-0.1, 0.1)
            ruido = rng.normal(0, 1.0, dias)
            if i % 3 == 0:
                serie = base + tendencia * np.arange(dias) + choque * 2 + ruido
            elif i % 3 == 1:
                serie = base + tendencia * np.arange(dias) - np.roll(choque, 10) * 1.5 + ruido
            else:
                serie = base + tendencia * np.arange(dias) + np.cumsum(ruido) * 0.3
            dados[campo_enum.name][vetor_nome] = serie
    return dados

def dados_para_vetores(dados: Dict[str, Dict[str, np.ndarray]]) -> list:
    vetores = []
    for campo_enum, campo_cfg in REGISTRO_CAMPOS.items():
        campo_nome = campo_enum.name
        if campo_nome not in dados:
            continue
        for vnome, serie in dados[campo_nome].items():
            cfg = campo_cfg.vetores.get(vnome)
            if not cfg:
                continue
            datas = pd.date_range(end=datetime.now(), periods=len(serie), freq="D")
            serie_pd = pd.Series(serie, index=datas, name=vnome)
            v = VetorEconomico(
                nome=cfg.descricao or vnome,
                simbolo=vnome,
                dimensao_categoria=campo_enum,
                dimensao_espacial=EscopoEspacial.GLOBAL,
                dimensao_granularidade=Granularidade.MACRO,
                valor_bruto=float(serie[-1]),
                fonte=cfg.fonte,
                lgpd_compliant=True,
            )
            v.serie_historica = serie_pd
            v.calcular_volatilidade()
            v.calcular_sentimento(serie_pd.mean())
            v.calcular_risco_pcq()
            vetores.append(v)
    return vetores
