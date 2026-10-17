"""Plain-assert checks for the logic that can actually break: python3 scripts/test_build.py"""

import model
import render


def test_visible_fails_closed_on_private_forks_and_self():
    repos = [
        {"name": "ok", "private": False, "visibility": "public", "fork": False},
        {"name": "secret", "private": True, "visibility": "private", "fork": False},
        {"name": "no-flag", "fork": False},  # missing "private" -> hidden
        {"name": "internal", "private": False, "visibility": "internal", "fork": False},
        {"name": "forked", "private": False, "visibility": "public", "fork": True},
        {"name": "TyrusRC.github.io", "private": False, "visibility": "public", "fork": False},
    ]
    assert [r["name"] for r in model.visible(repos, "tyrusrc")] == ["ok"]


def test_group_keeps_config_order_and_collects_unlisted_into_other():
    repos = [{"name": n, "pushed_at": p} for n, p in
             [("a", "1"), ("b", "2"), ("new", "9"), ("old", "0")]]
    cats = [{"slug": "x", "repos": ["b", "a", "gone"]}, {"slug": "empty", "repos": ["gone"]}]
    groups = model.group(repos, cats)
    assert [(c["slug"], [r["name"] for r in rs]) for c, rs in groups] == [
        ("x", ["b", "a"]), ("other", ["new", "old"])]


def test_fix_links_rewrites_only_relative_urls():
    html = ('<a href="LICENSE">l</a><img src="./docs/a.png"><a href="/x/y.md">r</a>'
            '<a href="#install">i</a><a href="#user-content-x">u</a>'
            '<a href="https://ex.com">e</a><img src="//cdn/x.png"><a href="mailto:a@b">m</a>')
    out = model.fix_links(html, "U", "R")
    assert 'href="https://github.com/U/R/blob/HEAD/LICENSE"' in out
    assert 'src="https://raw.githubusercontent.com/U/R/HEAD/docs/a.png"' in out
    assert 'href="https://github.com/U/R/blob/HEAD/x/y.md"' in out
    assert 'href="#user-content-install"' in out
    assert 'href="#user-content-x"' in out
    assert 'href="https://ex.com"' in out and 'src="//cdn/x.png"' in out and 'href="mailto:a@b"' in out


def test_repo_metadata_is_escaped_and_unsafe_homepage_dropped():
    repo = {"name": "r", "description": "<script>x</script>", "topics": ['"><b>'],
            "homepage": "javascript:alert(1)", "language": None}
    page = render.repo_page("U", "cat", repo, "")
    assert "<script>" not in page and '"><b>' not in page
    assert "javascript:" not in page


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
