from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Sequence

SENTENCE_SPLIT_RE = re.compile(r"[.!?。！？\n]+")
TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)

EN_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "she",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "with",
    "you",
}

ZH_STOPWORDS = {
    "的",
    "了",
    "在",
    "是",
    "我",
    "有",
    "和",
    "就",
    "不",
    "人",
    "都",
    "一",
    "一个",
    "上",
    "也",
    "很",
    "到",
    "说",
    "要",
    "去",
    "你",
    "会",
    "着",
    "没有",
    "看",
    "好",
    "自己",
    "这",
}


@dataclass(frozen=True)
class GlossaryRequest:
    texts: Sequence[str]
    top_k: int = 30
    window_size: int = 4
    min_term_length: int = 2
    stopwords: Sequence[str] | None = None


@dataclass(frozen=True)
class GlossaryEntry:
    term: str
    score: float


@dataclass(frozen=True)
class GlossaryResult:
    entries: List[GlossaryEntry]


class GlossaryError(RuntimeError):
    pass


def generate_glossary(request: GlossaryRequest) -> GlossaryResult:
    if not request.texts:
        raise GlossaryError("Glossary generation requires at least one text input.")

    stopwords = _build_stopwords(request.stopwords)
    sentences = _split_sentences("\n".join(request.texts))
    tokenized = [_tokenize(sentence, stopwords) for sentence in sentences]

    graph = _build_graph(tokenized, request.window_size)
    if not graph:
        return GlossaryResult(entries=[])

    scores = _pagerank(graph)
    phrases = _extract_phrases(sentences, scores, stopwords, request.min_term_length)

    ranked = sorted(
        (GlossaryEntry(term=term, score=score) for term, score in phrases.items()),
        key=lambda entry: entry.score,
        reverse=True,
    )
    return GlossaryResult(entries=ranked[: request.top_k])


def _build_stopwords(extra: Sequence[str] | None) -> set[str]:
    stopwords = set(word.lower() for word in EN_STOPWORDS)
    stopwords.update(ZH_STOPWORDS)
    if extra:
        stopwords.update(word.lower() for word in extra)
    return stopwords


def _split_sentences(text: str) -> List[str]:
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(text)]
    return [part for part in parts if part]


def _tokenize(sentence: str, stopwords: set[str]) -> List[str]:
    tokens = []
    for match in TOKEN_RE.finditer(sentence.lower()):
        token = match.group(0)
        if token in stopwords:
            continue
        tokens.append(token)
    return tokens


def _build_graph(tokenized: Iterable[List[str]], window_size: int) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for tokens in tokenized:
        for index, token in enumerate(tokens):
            window_end = min(index + window_size, len(tokens))
            for neighbor in tokens[index + 1 : window_end]:
                if token == neighbor:
                    continue
                graph[token].add(neighbor)
                graph[neighbor].add(token)
    return graph


def _pagerank(graph: dict[str, set[str]], damping: float = 0.85, steps: int = 30) -> dict[str, float]:
    scores = {node: 1.0 for node in graph}
    for _ in range(steps):
        next_scores: dict[str, float] = {}
        for node, neighbors in graph.items():
            if not neighbors:
                next_scores[node] = 1.0 - damping
                continue
            neighbor_sum = 0.0
            for neighbor in neighbors:
                neighbor_degree = len(graph[neighbor]) or 1
                neighbor_sum += scores[neighbor] / neighbor_degree
            next_scores[node] = (1.0 - damping) + damping * neighbor_sum
        scores = next_scores
    max_score = max(scores.values(), default=1.0)
    return {node: score / max_score for node, score in scores.items()}


def _extract_phrases(
    sentences: Iterable[str],
    scores: dict[str, float],
    stopwords: set[str],
    min_term_length: int,
) -> dict[str, float]:
    phrases: dict[str, float] = {}
    for sentence in sentences:
        tokens = []
        for match in TOKEN_RE.finditer(sentence.lower()):
            token = match.group(0)
            if token in stopwords:
                if tokens:
                    _update_phrase(tokens, scores, phrases, min_term_length)
                    tokens = []
                continue
            tokens.append(token)
        if tokens:
            _update_phrase(tokens, scores, phrases, min_term_length)

    return phrases


def _update_phrase(
    tokens: List[str],
    scores: dict[str, float],
    phrases: dict[str, float],
    min_term_length: int,
) -> None:
    term = " ".join(tokens).strip()
    if len(term) < min_term_length:
        return
    score = sum(scores.get(token, 0.0) for token in tokens)
    phrases[term] = max(score, phrases.get(term, 0.0))