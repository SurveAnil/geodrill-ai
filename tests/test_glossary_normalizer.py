"""
test_glossary_normalizer.py
===========================
Unit tests for drilling domain acronym expansion.
"""

from src.layer4_knowledge_graph.glossary_normalizer import GlossaryNormalizer, normalize_query


def test_glossary_normalizer_npt_expansion():
    normalizer = GlossaryNormalizer()
    query = "Were there any NPT events near 2400m?"
    expanded = normalizer.normalize_query(query)
    assert "non-productive time (NPT)" in expanded
    assert "2400m" in expanded


def test_glossary_normalizer_case_insensitivity():
    normalizer = GlossaryNormalizer()
    query = "did the driller pump lcm pill or check bop?"
    expanded = normalizer.normalize_query(query)
    assert "lost circulation material (LCM)" in expanded
    assert "blowout preventer (BOP)" in expanded


def test_glossary_normalizer_multiple_terms():
    query = "Check ROP and WOB while drilling to TD"
    expanded = normalize_query(query)
    assert "rate of penetration (ROP)" in expanded
    assert "weight on bit (WOB)" in expanded
    assert "total depth (TD)" in expanded


def test_glossary_normalizer_empty_and_whitespace():
    assert normalize_query("") == ""
    assert normalize_query("   ") == "   "
    assert normalize_query("plain drilling report") == "plain drilling report"
