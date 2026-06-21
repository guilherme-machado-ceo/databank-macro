"""
Cache local SQLite para séries temporais do DataBank.

Evita rate limits das APIs e mantém o dashboard funcional mesmo quando
uma fonte está offline, desde que já tenha havido uma coleta anterior.
"""
from __future__ import annotations

import io
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict

import pandas as pd

logger = logging.getLogger(__name__)


class DataCache:
    """Cache SQLite simples para séries temporais com metadados de coleta."""

    def __init__(self, db_path: Optional[str | Path] = None):
        if db_path is None:
            db_path = Path("data/cache/databank_cache.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS serie_temporal (
                    vetor_id TEXT PRIMARY KEY,
                    campo TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    fonte TEXT,
                    ultima_atualizacao TEXT NOT NULL,
                    df_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS coleta_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vetor_id TEXT NOT NULL,
                    fonte TEXT,
                    status TEXT NOT NULL,
                    mensagem TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def get(
        self, vetor_id: str, max_age_hours: int = 24
    ) -> Optional[Dict]:
        """
        Retorna série cacheada se existir e for mais recente que max_age_hours.
        Retorna dict com: serie (pd.Series), fonte, ultima_atualizacao, stale.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT campo, nome, fonte, ultima_atualizacao, df_json FROM serie_temporal WHERE vetor_id = ?",
                    (vetor_id,),
                ).fetchone()
            if not row:
                return None

            campo, nome, fonte, ultima_atualizacao, df_json = row
            try:
                serie = pd.read_json(io.StringIO(df_json), typ="series")
            except Exception:
                # fallback para formato antigo
                serie = pd.read_json(io.StringIO(df_json), typ="series", orient="split")

            ultima = datetime.fromisoformat(ultima_atualizacao.replace(" UTC", "+00:00"))
            agora = datetime.now(timezone.utc)
            horas = (agora - ultima).total_seconds() / 3600

            return {
                "vetor_id": vetor_id,
                "campo": campo,
                "nome": nome,
                "fonte": fonte,
                "ultima_atualizacao": ultima_atualizacao,
                "serie": serie,
                "stale": horas > max_age_hours,
                "horas_desde_atualizacao": horas,
            }
        except Exception as e:
            logger.warning(f"Erro ao ler cache de {vetor_id}: {e}")
            return None

    def put(
        self,
        vetor_id: str,
        campo: str,
        nome: str,
        fonte: Optional[str],
        serie: pd.Series,
    ) -> None:
        """Armazena ou atualiza uma série no cache."""
        try:
            df_json = serie.to_json(date_format="iso")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO serie_temporal (vetor_id, campo, nome, fonte, ultima_atualizacao, df_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(vetor_id) DO UPDATE SET
                        campo=excluded.campo,
                        nome=excluded.nome,
                        fonte=excluded.fonte,
                        ultima_atualizacao=excluded.ultima_atualizacao,
                        df_json=excluded.df_json
                    """,
                    (vetor_id, campo, nome, fonte, self._now(), df_json),
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Erro ao salvar cache de {vetor_id}: {e}")

    def log(self, vetor_id: str, fonte: Optional[str], status: str, mensagem: str = "") -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO coleta_log (vetor_id, fonte, status, mensagem, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (vetor_id, fonte or "", status, mensagem, self._now()),
                )
                conn.commit()
        except Exception:
            pass

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM serie_temporal")
            conn.execute("DELETE FROM coleta_log")
            conn.commit()
