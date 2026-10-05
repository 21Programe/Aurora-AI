"""Subsistema RAG do Aurora IA.

Mantém ingestão, embeddings e recuperação vetorial fora do arquivo legado.
Dependências pesadas são opcionais no import para manter o projeto testável.
"""

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

        if faiss is None:
            self.initialized = True
            return

        with self.database.connect() as conn:
            rows = conn.execute(
                "SELECT id_chunk, conteudo_texto, vetor_json "
                "FROM base_conhecimento_rag ORDER BY id_chunk"
            ).fetchall()

        vectors: List[np.ndarray] = []
        for row_index, (_, text, vector_json) in enumerate(rows):
            try:
                vector = np.asarray(json.loads(vector_json), dtype="float32")
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if vector.ndim == 1:
                vectors.append(vector)
                self.mapping[len(vectors) - 1] = text

        if vectors:
            matrix = np.vstack(vectors)
            self.index = faiss.IndexFlatIP(int(matrix.shape[1]))
            self.index.add(matrix)

        self.initialized = True

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

    def ingest_pdf(
        self,
        file_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """Extrai um PDF, gera embeddings e grava os chunks no SQLite."""
        if fitz is None:
            raise RuntimeError("PyMuPDF não está instalado.")

        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(source)

        destination = settings.RAG_DIR / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        document = fitz.open(destination)
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
        for chunk in chunks:
            if len(chunk) < 20:
                continue
            vector = self.embed(chunk)
            if vector is None:
                continue
            self.database.insert(
                "base_conhecimento_rag",
                ("origem", "conteudo_texto", "vetor_json"),
                (source.name, chunk, json.dumps(vector.tolist())),
            )
            inserted += 1

        self.load_index()
        if callback:
            callback(f"RAG: {inserted} blocos indexados.")
        return inserted
