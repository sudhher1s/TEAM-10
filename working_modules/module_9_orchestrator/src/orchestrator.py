"""
Module 9: Orchestrator
Chains Modules 4→5→6→7→8 into a single end-to-end function.
Supports OpenAI and mock grounding.
"""
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder
    _HAS_ENCODER = True
except Exception:
    QueryEncoder = None  # type: ignore
    _HAS_ENCODER = False
from working_modules.module_6_evidence_extraction.src.evidence_extractor import EvidenceExtractor
from working_modules.module_7_guardrails.src.guardrails_checker import GuardrailsChecker
from working_modules.module_8_llm_grounding.src.llm_grounder import LLMGrounder
from working_modules.module_8_2_google_grounding.src.google_grounder import GoogleGrounder

class MedicalCodingOrchestrator:
    def __init__(
        self,
        index_path: Path,
        item_metadata_path: Path,
        kb_path: Path,
        llm_model: str = "gpt-3.5-turbo",
        llm_provider: str = "openai",
    ):
        self.encoder = None
        if _HAS_ENCODER:
            try:
                self.encoder = QueryEncoder(index_path=index_path, item_metadata_path=item_metadata_path)
            except Exception:
                self.encoder = None
        # Lazy import reranker to avoid sentence-transformers hard dependency
        try:
            from working_modules.module_5_reranker.src.reranker import Reranker  # type: ignore
            self.reranker = Reranker()
        except Exception:
            self.reranker = None
        self.extractor = EvidenceExtractor(kb_path)
        self.guardrails = GuardrailsChecker()
        # Select grounder based on provider
        if llm_provider == "google":
            self.grounder = GoogleGrounder(model=llm_model, provider=llm_provider)
        else:
            self.grounder = LLMGrounder(model=llm_model, provider=llm_provider)
    
    def run(self, query: str, retrieve_k: int = 100, rerank_k: int = 10) -> Dict[str, Any]:
        # M4: Retrieve
        if self.encoder is not None:
            res = self.encoder.search(query, top_k=retrieve_k)
            candidates = [
                {"code": it.code, "title": it.title, "category": it.category, "index_id": it.index_id}
                for it in res.items
            ]
            retrieve_summary = {"elapsed_ms": res.elapsed_ms, "top_codes": [it.code for it in res.items[:5]]}
        else:
            # Fallback: minimal keyword-based candidate selection from KB titles
            kb = getattr(self.extractor, "kb", {})
            scored = []

            def _tokenize(text: str) -> set:
                return {tok for tok in text.lower().replace("/", " ").replace("-", " ").split() if tok}

            q_tokens = _tokenize(query)
            if isinstance(kb, dict):
                itr = [(code, item) for code, item in kb.items()]
            elif isinstance(kb, list):
                itr = [(item.get("code"), item) for item in kb]
            else:
                itr = []

            for code, item in itr:
                if not code or not isinstance(item, dict):
                    continue
                title = (item.get("title") or "")
                desc = (item.get("description") or "")
                aliases = " ".join(item.get("aliases", []) or [])

                title_toks = _tokenize(title)
                desc_toks = _tokenize(desc)
                alias_toks = _tokenize(aliases)

                # Simple lexical score: overlap across title/aliases/description with weights
                overlap_title = len(q_tokens & title_toks)
                overlap_alias = len(q_tokens & alias_toks)
                overlap_desc = len(q_tokens & desc_toks)
                score = 3 * overlap_title + 2 * overlap_alias + 1 * overlap_desc

                if score > 0:
                    scored.append({
                        "code": code,
                        "title": title,
                        "category": item.get("category", "unknown"),
                        "index_id": -1,
                        "score": float(score),
                    })

            scored.sort(key=lambda x: x["score"], reverse=True)
            candidates = scored[: max(rerank_k, 10)] if scored else []
            retrieve_summary = {"elapsed_ms": 0.0, "top_codes": [c["code"] for c in candidates[:5]]}
        
        # M5: Rerank
        if self.reranker is not None and candidates:
            rres = self.reranker.rerank(query, candidates, top_k=rerank_k)
        else:
            # Identity rerank fallback
            class _RItem:
                def __init__(self, code, score):
                    self.code = code
                    self.score = score
            ritems = [_RItem(c["code"], c.get("score", 0.5)) for c in candidates][:rerank_k]
            rres = type("RRes", (), {"items": ritems, "elapsed_ms": 0.0})()
        
        # M6: Evidence
        evidence_set = self.extractor.extract(
            query,
            [{"code": it.code, "score": it.score} for it in rres.items]
        )
        
        # M7: Guardrails
        guard = self.guardrails.check(
            query,
            [ev.code for ev in evidence_set.items],
            [ev.title for ev in evidence_set.items]
        )
        
        # M8: Grounding
        grounded = self.grounder.ground_with_guardrails(
            query,
            [ev.__dict__ for ev in evidence_set.items],
            {
                "violations": [v.__dict__ for v in guard.violations],
                "is_valid": guard.is_valid,
            }
        )
        
        # Convert confidence from 0-1 to 0-100 percentage
        raw_conf = grounded.llm_response.confidence or 0.0
        confidence_pct = max(0, min(100, int(raw_conf * 100)))
        
        return {
            "query": query,
            "retrieve": retrieve_summary,
            "rerank": {
                "elapsed_ms": rres.elapsed_ms,
                "top_codes": [it.code for it in rres.items[:5]],
            },
            "evidence": {
                "elapsed_ms": evidence_set.elapsed_ms,
                "items": [ev.__dict__ for ev in evidence_set.items],
            },
            "guardrails": {
                "elapsed_ms": guard.elapsed_ms,
                "is_valid": guard.is_valid,
                "violations": [v.__dict__ for v in guard.violations],
            },
            "grounded": {
                "elapsed_ms": grounded.llm_response.elapsed_ms,
                "codes": grounded.llm_response.codes,
                "confidence": confidence_pct,
                "explanation": grounded.llm_response.explanation,
                "model": grounded.llm_response.model_used,
                "is_safe": grounded.is_safe,
                "warnings": grounded.warnings,
            },
        }
