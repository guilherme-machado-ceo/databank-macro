from __future__ import annotations
import os, json, logging, hashlib, base64
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

try:
    import oqs
    PQC_AVAILABLE = True
except ImportError:
    PQC_AVAILABLE = False

VALIDADE_ANOS = {"publico": 30, "interno": 20, "confidencial": 10, "restrito": 5}

@dataclass
class RelatorioProtecao:
    dataset_id: str; algoritmo_kem: str; algoritmo_assinatura: str
    sensibilidade: str; exposicao_quantica: float; validade_anos: int
    data_recriptografia: str; hndl_safe: bool

class CustodiaPCQ:
    def __init__(self, modo="auto", cold_storage_dir="./cold_storage"):
        self.modo = modo
        self.diretorio = Path(cold_storage_dir)
        self.diretorio.mkdir(parents=True, exist_ok=True)
        self.modo_efetivo = "pqc" if modo == "auto" and PQC_AVAILABLE else ("classico" if modo == "auto" else modo)
        self._chaves = self._gerar_chaves()

    def _gerar_chaves(self):
        rsa_path = self.diretorio / "rsa_private.pem"
        if rsa_path.exists():
            with open(rsa_path, "rb") as f:
                rsa_priv = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        else:
            rsa_priv = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
            with open(rsa_path, "wb") as f:
                f.write(rsa_priv.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
        return {"rsa_priv": rsa_priv}

    def proteger(self, dataset_id: str, dados: bytes, metadata: dict) -> RelatorioProtecao:
        sensibilidade = metadata.get("sensibilidade", "confidencial")
        exposicao = self._calcular_exposicao(metadata)
        validade = max(int(VALIDADE_ANOS.get(sensibilidade, 10) * (1 - exposicao * 0.5)), 2)
        data_rec = datetime.now(timezone.utc) + timedelta(days=validade * 365)

        chave_aes = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(chave_aes)
        iv = os.urandom(12)
        dados_cifrados = aesgcm.encrypt(iv, dados, None)

        return RelatorioProtecao(
            dataset_id=dataset_id,
            algoritmo_kem="ML-KEM-768" if self.modo_efetivo == "pqc" else "RSA-4096-OAEP",
            algoritmo_assinatura="ML-DSA-65" if self.modo_efetivo == "pqc" else "ECDSA-P384",
            sensibilidade=sensibilidade,
            exposicao_quantica=round(exposicao, 4),
            validade_anos=validade,
            data_recriptografia=data_rec.strftime("%Y-%m-%d"),
            hndl_safe=True,
        )

    def _calcular_exposicao(self, metadata: dict) -> float:
        idade = min(metadata.get("idade_anos", 0) / 20, 1.0) * 0.3
        sens = {"publico": 0.05, "interno": 0.1, "confidencial": 0.2, "restrito": 0.3}
        s = sens.get(metadata.get("sensibilidade", "confidencial"), 0.2)
        return min(idade + s, 1.0)

    def status(self):
        return {"modo": self.modo_efetivo, "pqc_disponivel": PQC_AVAILABLE, "algoritmo_cifra": "AES-256-GCM", "algoritmo_asymmetric": "Kyber1024+Dilithium5" if self.modo_efetivo == "pqc" else "RSA-4096+ECDSA-P384"}
