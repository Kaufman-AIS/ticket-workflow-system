"""Minimal Markdown → BlockNote conversion for Paca API bodies."""

from __future__ import annotations


def markdown_to_blocknote(text: str) -> list[dict]:
    """Convert plain/markdown text into a BlockNote document (array of blocks).

    Paca rejects free-form strings for description/content; it expects a
    BlockNote JSON array. This helper is intentionally small: one paragraph
    per non-empty line. Good enough for intake summaries and smoke tests.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    paragraphs = [ln for ln in lines if ln]
    if not paragraphs:
        paragraphs = [text.strip() or ""]
    blocks: list[dict] = []
    for i, paragraph in enumerate(paragraphs, start=1):
        blocks.append(
            {
                "id": str(i),
                "type": "paragraph",
                "props": {
                    "textColor": "default",
                    "backgroundColor": "default",
                    "textAlignment": "left",
                },
                "content": [{"type": "text", "text": paragraph, "styles": {}}],
                "children": [],
            }
        )
    return blocks
