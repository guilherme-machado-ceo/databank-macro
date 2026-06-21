import pytest
from src.core.campos_granulares import REGISTRO_CAMPOS, total_vetores, get_sensibilidade
from src.core.vetor import CarteiraVetores
from src.core.inflex import INFLEx
from src.core.anamorf import ANAMORF
from src.core.fluxus import FLUXUS
from src.pcq.custodia import CustodiaPCQ
from src.mining.pcq_miner import PCQMiner
from src.ingestion.data_generator import gerar_dados_correlacionados, dados_para_vetores

@pytest.fixture
def carteira():
    dados = gerar_dados_correlacionados(dias=120, seed=42)
    vetores = dados_para_vetores(dados)
    c = CarteiraVetores()
    for v in vetores: c.adicionar(v)
    return c

def test_41_vetores_4_campos():
    assert total_vetores() == 41
    assert len(REGISTRO_CAMPOS) == 4

def test_sensibilidade_por_campo():
    from src.core.campos_granulares import CampoGranular
    assert get_sensibilidade(CampoGranular.CHIPS) == 0.07

def test_inflexao_detecta(carteira):
    inflex = INFLEx(carteira)
    vetor = list(carteira.vetores.values())[0]
    if vetor.serie_historica is not None and len(vetor.serie_historica) >= 60:
        res = inflex.detectar_inflexao(vetor, janela=60)
        assert 0 <= res.prob_inflexao <= 1
        assert res.direcao in (-1, 0, 1)

def test_anamorf_operar(carteira):
    anamorf = ANAMORF(carteira)
    anamorf.fit()
    if anamorf._is_fitted:
        res = anamorf.operar(confianca_minima=0.3)
        assert isinstance(res, list)

def test_fluxus_ciclo(carteira):
    inflex = INFLEx(carteira)
    anamorf = ANAMORF(carteira)
    fluxus = FLUXUS(carteira, inflex, anamorf)
    res = fluxus.ciclo()
    assert res.n_estudos >= 0
    assert res.receita_gerada >= 0

def test_custodia_proteger():
    custodia = CustodiaPCQ(modo="classico")
    rel = custodia.proteger("ds-test", b"dados", {"sensibilidade": "restrito"})
    assert rel.hndl_safe is True
    assert rel.validade_anos <= 10

def test_miner_5_chains():
    miner = PCQMiner()
    assert len(miner.perfis) == 5

def test_miner_qrl_menor_risco():
    assert PCQMiner().perfis["qrl"].risco_quantico == 0.0

def test_dados_para_vetores():
    dados = gerar_dados_correlacionados(dias=60, seed=123)
    vetores = dados_para_vetores(dados)
    assert len(vetores) == 41
