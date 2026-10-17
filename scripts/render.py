"""HTML templates. Everything from config or the API is escaped except README HTML,
which GitHub has already sanitized."""

from html import escape as e

CSP = ("default-src 'none'; style-src 'self'; script-src 'self'; img-src https: data:; "
       "base-uri 'none'; form-action 'none'")


def _repo_url(user, name):
    return f"https://github.com/{user}/{name}"


def sidebar(profile, groups, current):
    def link(href, label, key):
        on = ' class="on" aria-current="page"' if key == current else ""
        return f'<li><a href="{href}"{on}>{e(label)}</a></li>'

    parts = [
        f'<a class="brand" href="/">~/{e(profile["handle"])}</a>',
        '<input id="search" type="search" placeholder="/ search repos" aria-label="Search repos" hidden>',
        '<h2># profile</h2><ul>',
        link("/", "whoami", "home"),
        link("/experience/", "experience", "experience"),
        "</ul>",
    ]
    for cat, repos in groups:
        items = "".join(link(f"/wiki/{e(r['name'])}/", r["name"], r["name"]) for r in repos)
        if cat.get("collapsed"):
            is_open = " open" if any(r["name"] == current for r in repos) else ""
            parts.append(f'<details{is_open}><summary># {e(cat["slug"])} '
                         f'<span class="dim">({len(repos)})</span></summary><ul>{items}</ul></details>')
        else:
            parts.append(f'<h2># {e(cat["slug"])}</h2><ul>{items}</ul>')
    return "\n".join(parts)


def layout(title, profile, groups, current, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{e(title)}</title>
<meta name="description" content="{e(profile['name'])} — {e(profile['headline'])}">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<button id="menu" type="button" aria-controls="side" aria-expanded="false" hidden>☰ menu</button>
<nav id="side" aria-label="Site">
{sidebar(profile, groups, current)}
</nav>
<main>
{body}
</main>
<script src="/assets/site.js"></script>
</body>
</html>
"""


def card(user, repo):
    stars = f' <span class="dim">★{repo["stargazers_count"]}</span>' if repo.get("stargazers_count") else ""
    return (f'<a class="card" href="/wiki/{e(repo["name"])}/"><span><span class="acc">{e(repo["name"])}/</span>{stars}</span>'
            f'<span class="dim">{e(repo.get("description") or "")}</span></a>')


def home(cfg, repos_by_name):
    p, user = cfg["profile"], cfg["github_user"]
    featured = "".join(card(user, repos_by_name[n]) for n in cfg.get("featured", []) if n in repos_by_name)
    recent = "".join(
        f'<li><span class="acc">{e(x["start"][-4:])}–{e("now" if x["end"] == "Present" else x["end"][-4:])}</span> '
        f'{e(x["role"])}{" · " + e(x["org"]) if x["org"] else ""}</li>'
        for x in cfg["experience"][:3])
    return f"""<p class="prompt">$ whoami</p>
<header class="who">
  <img src="https://github.com/{e(user)}.png?size=192" alt="{e(p['name'])}" width="96" height="96">
  <div>
    <h1>{e(p['name'])}</h1>
    <p>{e(p['headline'])}</p>
    <p class="dim">{e(p['location'])} · <a href="{_repo_url(user, '')}">github</a> · <a href="{e(p['linkedin'])}">linkedin</a></p>
  </div>
</header>
<p>{e(" ".join(p['bio'].split()))}</p>
<p class="dim ai-note"># {e(" ".join(p['ai_note'].split()))}</p>
<p class="prompt">$ ls ./featured</p>
<div class="grid">{featured}</div>
<p class="prompt">$ cat experience.log | head -3</p>
<ul class="timeline">{recent}<li><a href="/experience/">… full log →</a></li></ul>
"""


def experience(cfg):
    items = []
    for x in cfg["experience"]:
        org = f' · {e(x["org"])}' if x["org"] else ""
        points = "".join(f"<li>{e(pt)}</li>" for pt in x["points"])
        items.append(f"""<li>
  <p><span class="acc">{e(x['start'])} – {e(x['end'])}</span></p>
  <h2>{e(x['role'])}{org}</h2>
  <p class="dim">{e(x['kind'])}</p>
  {f'<ul>{points}</ul>' if points else ''}
</li>""")
    return f'<p class="prompt">$ cat experience.log</p>\n<h1>Experience</h1>\n<ol class="timeline">{"".join(items)}</ol>\n'


def repo_page(user, cat_slug, repo, readme):
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in
                   ([repo["language"]] if repo.get("language") else []) + repo.get("topics", []))
    stars = f' <span class="tag">★ {repo["stargazers_count"]}</span>' if repo.get("stargazers_count") else ""
    archived = ' <span class="tag warn">archived</span>' if repo.get("archived") else ""
    site = (f' · <a href="{e(repo["homepage"])}">live site ↗</a>'
            if (repo.get("homepage") or "").startswith("https://") else "")
    updated = (repo.get("pushed_at") or "")[:10]
    body = readme or '<p class="dim">No README yet.</p>'
    return f"""<p class="dim crumb">wiki / {e(cat_slug)} / {e(repo['name'])}</p>
<h1 class="acc">{e(repo['name'])}{stars}{archived}</h1>
<p>{e(repo.get('description') or '')}</p>
<p>{tags}</p>
<p class="dim">updated {e(updated)} · <a href="{_repo_url(user, e(repo['name']))}">view on github ↗</a>{site}</p>
<hr>
<article class="readme">{body}</article>
"""
