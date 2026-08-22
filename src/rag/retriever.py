import re
from pathlib import Path
from typing import List, Dict, Any


class PolicyRetriever:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.docs = []
        self._load_docs()

    def _find_kb_path(self) -> Path:
        candidates = [
            Path.cwd() / "knowledge-base",
            Path(__file__).resolve().parent.parent.parent / "knowledge-base",
            Path(__file__).resolve().parent.parent / "knowledge-base",
            Path(__file__).resolve().parent / "knowledge-base",
        ]
        for path in candidates:
            if path.exists() and path.is_dir():
                return path
        return Path("knowledge-base")

    def _load_docs(self):
        kb_path = self._find_kb_path()
        if not kb_path.exists():
            return

        for file_path in kb_path.glob("*.md"):
            filename = file_path.name
            content = file_path.read_text(encoding="utf-8")

            is_superseded = any(
                term in filename.lower()
                for term in ["legacy", "superseded", "14-internal"]
            )

            sections = content.split("\n\n")
            current_heading = filename

            for section in sections:
                text = section.strip()
                if not text:
                    continue

                if text.startswith("#"):
                    lines = text.split("\n")
                    current_heading = lines[0].lstrip("#").strip()
                    text = "\n".join(lines[1:]).strip()
                    if not text:
                        continue

                self.docs.append({
                    "filename": filename,
                    "heading": current_heading,
                    "content": text,
                    "is_superseded": is_superseded,
                    "source": f"{filename} ({current_heading})",
                })

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        raw_words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]

        query_terms = set()
        for word in raw_words:
            query_terms.add(word)
            if word.endswith("s") and len(word) > 3:
                query_terms.add(word[:-1])
            else:
                query_terms.add(word + "s")

        scored_docs = []

        for doc in self.docs:
            if doc["is_superseded"] and "legacy" not in query.lower():
                continue

            doc_text = f"{doc['filename']} {doc['heading']} {doc['content']}".lower()
            matches = sum(1 for term in query_terms if term in doc_text)

            if matches > 0:
                scored_docs.append((matches, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]