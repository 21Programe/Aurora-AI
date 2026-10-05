"""Subsistema RAG do Aurora IA.

Mantém ingestão, embeddings e recuperação vetorial fora do arquivo legado.
Dependências pesadas são opcionais no import para manter o projeto testável.
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

from aurora.config import settings
from aurora.database import AuroraDatabase
from aurora.logger import logger

try:
    import faiss
except ImportError:  # pragma: no cover
    faiss = None

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover
    SentenceTransformer = None


class RAGSubsystem:
    """Indexa documentos e recupera contexto semântico."""

    def __init__(self, database: Optional[AuroraDatabase] = None) -> None:
        self.database = database or AuroraDatabase()
        self.database.initialize()
        self.index = None
        self.mapping: Dict[int, str] = {}
        self.metadata: Dict[int, Dict[str, object]] = {}
        self.encoder = None
        self.initialized = False

    def _get_encoder(self):
        if self.encoder is None and SentenceTransformer is not None:
            self.encoder = SentenceTransformer(
                settings.RAG_ENCODER_MODEL,
                cache_folder=str(settings.RAG_CACHE_DIR),
            )
        return self.encoder

    def embed(self, text: str) -> Optional[np.ndarray]:
        if not text or not text.strip():
            return None
        encoder = self._get_encoder()
        if encoder is None:
            return None
        try:
            vector = encoder.encode(text, normalize_embeddings=True)
            return np.asarray(vector, dtype="float32")
        except Exception:
            logger.exception("Falha ao gerar embedding.")
            return None

    def load_index(self) -> None:
        """Reconstrói o índice a partir do SQLite."""
        self.index = None
        self.mapping = {}
        self.metadata = {}

        if faiss is None:
            self.initialized = True
            return

        with self.database.connect() as conn:
            rows = conn.execute(
                "SELECT id_chunk, conteudo_texto, vetor_json, origem, source_hash, chunk_index "
                "FROM base_conhecimento_rag ORDER BY id_chunk"
            ).fetchall()

        vectors: List[np.ndarray] = []
        for row_index, (chunk_id, text, vector_json, origem, source_hash, chunk_index) in enumerate(rows):
            try:
                vector = np.asarray(json.loads(vector_json), dtype="float32")
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if vector.ndim == 1:
                vectors.append(vector)
                position = len(vectors) - 1
                self.mapping[position] = text
                self.metadata[position] = {
                    "chunk_id": chunk_id,
                    "source": origem,
                    "source_hash": source_hash,
                    "chunk_index": chunk_index,
                }

        if vectors:
            matrix = np.vstack(vectors)
            self.index = faiss.IndexFlatIP(int(matrix.shape[1]))
            self.index.add(matrix)

        self.initialized = True

    def delete_source(self, source_hash: str) -> int:
        """Exclui todos os chunks de uma fonte e remove sua cópia local."""
        if not source_hash or len(source_hash) != 64:
            raise ValueError("source_hash deve ser um SHA-256 hexadecimal.")
        with self.database.connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT origem FROM base_conhecimento_rag WHERE source_hash = ?",
                (source_hash,),
            ).fetchall()
            cursor = conn.execute(
                "DELETE FROM base_conhecimento_rag WHERE source_hash = ?",
                (source_hash,),
            )
        for (source_name,) in rows:
            candidate = settings.RAG_DIR / Path(source_name).name
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                logger.warning("Não foi possível remover a cópia RAG: %s", candidate)
        self.load_index()
        return cursor.rowcount

    def retrieve_with_metadata(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, object]]:
        if not self.initialized:
            self.load_index()
        if self.index is None or self.index.ntotal == 0:
            return []
        vector = self.embed(query)
        if vector is None:
            return []
        k = min(int(top_k or settings.RAG_TOP_K), int(self.index.ntotal))
        distances, indices = self.index.search(np.asarray([vector], dtype="float32"), k)
        results = []
        for score, index in zip(distances[0], indices[0]):
            position = int(index)
            if position in self.mapping:
                item = dict(self.metadata.get(position, {}))
                item["score"] = float(score)
                item["text"] = self.mapping[position]
                results.append(item)
        return results

    def retrieve(self, query: str, top_k: Optional[int] = None) -> str:
        if not self.initialized:
            self.load_index()
        if self.index is None or self.index.ntotal == 0:
            return ""

        vector = self.embed(query)
        if vector is None:
            return ""

        k = min(int(top_k or settings.RAG_TOP_K), int(self.index.ntotal))
        distances, indices = self.index.search(
            np.asarray([vector], dtype="float32"), k
        )

        blocks = [
            self.mapping[int(index)]
            for index in indices[0]
            if int(index) in self.mapping
        ]
        return "\n---\n".join(blocks)

    # Compatibilidade com a API legada durante a migração.
    def gerar_vetor_embedding(self, texto: str):
        return self.embed(texto)

    def recuperar_contexto(self, pergunta: str, limiar_top_k: int = 3) -> str:
        return self.retrieve(pergunta, limiar_top_k)

    def ingerir_pdf(self, caminho_arquivo: str, callback_interface=None) -> int:
        return self.ingest_pdf(caminho_arquivo, callback_interface)

    @property
    def indice_faiss(self):
        return self.index

    @indice_faiss.setter
    def indice_faiss(self, value):
        self.index = value

    @property
    def mapeamento_ids(self):
        return self.mapping

    @mapeamento_ids.setter
    def mapeamento_ids(self, value):
        self.mapping = value

    def ingest_pdf(self,
        file_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """Extrai um PDF, gera embeddings e grava os chunks no SQLite."""
        if fitz is None:
            raise RuntimeError("PyMuPDF não está instalado.")

        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(source)
        if source.suffix.lower() != ".pdf":
            raise ValueError("A ingestão atual aceita somente arquivos PDF.")

        max_bytes = settings.RAG_MAX_FILE_BYTES
        if source.stat().st_size > max_bytes:
            raise ValueError(f"PDF excede o limite de {max_bytes} bytes.")
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        with self.database.connect() as conn:
            existing = conn.execute(
                "SELECT 1 FROM base_conhecimento_rag WHERE source_hash = ? LIMIT 1",
                (source_hash,),
            ).fetchone()
        if existing:
            logger.info("RAG: fonte já indexada, ignorando duplicata: %s", source.name)
            return 0

        destination = settings.RAG_DIR / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        with fitz.open(destination) as document:
            if document.page_count > settings.RAG_MAX_PAGES:
                raise ValueError(f"PDF excede o limite de {settings.RAG_MAX_PAGES} páginas.")
            raw_text = "\n".join(page.get_text("text") for page in document)

        chunks: List[str] = []
        current = ""
        for fragment in raw_text.split("\n\n"):
            fragment = fragment.strip()
            if not fragment:
                continue
            if len(current) + len(fragment) <= settings.RAG_CHUNK_SIZE:
                current = f"{current} {fragment}".strip()
            else:
                if current:
                    chunks.append(current)
                current = fragment
        if current:
            chunks.append(current)

        inserted = 0
        for chunk_index, chunk in enumerate(chunks):
            if len(chunk) < 20:
                continue
            vector = self.embed(chunk)
            if vector is None:
                continue
            self.database.insert(
                "base_conhecimento_rag",
                ("origem", "conteudo_texto", "vetor_json", "source_hash", "chunk_index"),
                (source.name, chunk, json.dumps(vector.tolist()), source_hash, chunk_index),
            )
            inserted += 1

        self.load_index()
        if callback:
            callback(f"RAG: {inserted} blocos indexados.")
        return inserted
