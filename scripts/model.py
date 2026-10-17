"""Pure data shaping: which repos are shown, how they're grouped, README link fixing."""

import re

OTHER = {"slug": "other", "repos": [], "collapsed": False}


def visible(repos, user):
    """Public, non-fork repos, minus this site and the profile-README repo. Fails closed on anything not explicitly public."""
    meta = {f"{user}.github.io".lower(), user.lower()}
    return [r for r in repos
            if r.get("private") is False
            and r.get("visibility", "public") == "public"
            and not r.get("fork")
            and r["name"].lower() not in meta]


def group(repos, categories):
    """[(category, [repo, ...]), ...] in config order; unlisted repos go to "other"."""
    by_name = {r["name"]: r for r in repos}
    placed, groups = set(), []
    for cat in categories:
        members = [by_name[n] for n in cat["repos"] if n in by_name]
        placed.update(r["name"] for r in members)
        if members:
            groups.append((cat, members))
    rest = sorted((r for r in repos if r["name"] not in placed),
                  key=lambda r: r.get("pushed_at") or "", reverse=True)
    if rest:
        groups.append((OTHER, rest))
    return groups


_ATTR = re.compile(r'\b(href|src)="([^"]*)"')
_ABSOLUTE = re.compile(r"^([a-z][a-z0-9+.-]*:|//)", re.I)


def fix_links(html, user, repo):
    """Point README-relative links at GitHub, and in-page anchors at GitHub's prefixed ids."""
    def sub(m):
        attr, url = m.groups()
        if not url or _ABSOLUTE.match(url):
            return m.group(0)
        if url.startswith("#"):
            if url.startswith("#user-content-"):
                return m.group(0)
            return f'{attr}="#user-content-{url[1:]}"'
        path = url.lstrip("/")
        if path.startswith("./"):
            path = path[2:]
        base = (f"https://raw.githubusercontent.com/{user}/{repo}/HEAD/" if attr == "src"
                else f"https://github.com/{user}/{repo}/blob/HEAD/")
        return f'{attr}="{base}{path}"'
    return _ATTR.sub(sub, html)
