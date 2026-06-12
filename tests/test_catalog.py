from pathlib import Path

import pytest

from agent_guidance_mcp.catalog import build_catalog, find_standards_root


ROOT = Path(__file__).resolve().parents[1]


def test_find_standards_root_detects_parent_checkout():
    assert find_standards_root(ROOT) == ROOT


def test_build_catalog_uses_standalone_repo_by_default():
    catalog = build_catalog()

    assert catalog.root == ROOT


def test_catalog_indexes_core_surfaces():
    catalog = build_catalog(ROOT)
    identifiers = {entry["identifier"] for entry in catalog.list_entries()}

    assert "karpathy-principles" in identifiers
    assert "skill-reference" in identifiers
    assert "codebase-onboarding" in identifiers
    assert "codex" not in identifiers
    assert all(entry["kind"] != "agent" for entry in catalog.list_entries())


def test_catalog_reads_skill_by_name():
    catalog = build_catalog(ROOT)

    content = catalog.read_entry("codebase-onboarding")

    assert "# Codebase Onboarding" in content
    assert "Reconnaissance" in content


def test_catalog_search_returns_ranked_snippets():
    catalog = build_catalog(ROOT)

    results = catalog.search_entries("security auth secrets", limit=3)

    assert results
    assert all("snippet" in result for result in results)
    assert any("security" in result["path"].lower() for result in results)


def test_recommend_context_includes_essentials_and_task_matches():
    catalog = build_catalog(ROOT)

    result = catalog.recommend_context("Build a secure API with tests", limit=6)
    paths = [item["path"] for item in result["recommendations"]]

    assert "karpathy/principles.md" in paths
    assert "SKILL-REFERENCE.md" in paths
    assert any("security" in path.lower() for path in paths)
    assert any("test" in path.lower() or "api" in path.lower() for path in paths)


def test_missing_entry_raises_key_error():
    catalog = build_catalog(ROOT)

    with pytest.raises(KeyError):
        catalog.read_entry("does-not-exist")


def test_read_bounded_text_handles_invalid_utf8():
    import os
    import tempfile
    from pathlib import Path
    from agent_guidance_mcp.project_scan import read_bounded_text

    fd, path_str = tempfile.mkstemp()
    try:
        os.write(fd, b"Hello \xff World")
        os.close(fd)

        content, truncated = read_bounded_text(Path(path_str), 100)
        assert content is not None
        assert "Hello" in content
        assert "World" in content
        assert "\ufffd" in content
        assert truncated is False
    finally:
        try:
            os.remove(path_str)
        except OSError:
            pass
