from harness_cli.matchers import gitignore_matches, owners_for, parse_codeowners
from harness_cli.markdown import imports, links

CO = """
*            @org/default
/.claude/    @org/sec
**/AGENTS.md @org/harness
docs/*       @org/docs
/build/logs/ @org/ops
"""


def owner(path):
    r = owners_for(parse_codeowners(CO), path)
    return r.owners if r else None


def test_codeowners_last_match_wins():
    assert owner(".claude/settings.json") == ["@org/sec"]
    assert owner("a/b/AGENTS.md") == ["@org/harness"]
    assert owner("AGENTS.md") == ["@org/harness"]
    assert owner("src/main.py") == ["@org/default"]


def test_codeowners_star_does_not_cross_slash():
    assert owner("docs/x.md") == ["@org/docs"]
    assert owner("docs/sub/x.md") == ["@org/default"]


def test_codeowners_dir_only():
    assert owner("build/logs/a.log") == ["@org/ops"]


def test_codeowners_empty_owner_unassigns():
    rules = parse_codeowners("* @a\n/.claude/\n")
    assert owners_for(rules, ".claude/x").owners == []


def test_gitignore():
    text = "CLAUDE.local.md\n.claude/settings.local.json\n!keep.md\n"
    assert gitignore_matches(text, "CLAUDE.local.md")
    assert gitignore_matches(text, ".claude/settings.local.json")
    assert not gitignore_matches(text, ".claude/settings.json")


def test_imports_ignore_mentions_emails_and_code():
    text = "@AGENTS.md\nContacta con @org/equipo o a@b.com\n```\n@docs/x.md\n```\nVer `@docs/y.md` y @docs/z.md\n"
    assert [t for _, t in imports(text)] == ["AGENTS.md", "docs/z.md"]


def test_links_skip_urls_and_anchors():
    text = "[a](docs/a.md) [b](https://x.y) [c](#sec) [d](mailto:x@y.z) [e](docs/e.md#parte)"
    assert [t for _, t in links(text)] == ["docs/a.md", "docs/e.md"]
