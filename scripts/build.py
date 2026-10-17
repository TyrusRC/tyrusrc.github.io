"""Build the static site into _site/: python3 scripts/build.py"""

import shutil
import sys
import tomllib
from pathlib import Path

import github
import model
import render

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    cfg = tomllib.loads((ROOT / "site.toml").read_text(encoding="utf-8"))
    user, profile = cfg["github_user"], cfg["profile"]

    repos = model.visible(github.public_repos(user), user)
    groups = model.group(repos, cfg.get("category", []))
    by_name = {r["name"]: r for r in repos}

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    write(OUT / ".nojekyll", "")

    page = lambda title, current, body: render.layout(title, profile, groups, current, body)
    write(OUT / "index.html", page(f"{profile['name']} · {profile['handle']}", "home",
                                   render.home(cfg, by_name)))
    write(OUT / "experience" / "index.html", page("Experience", "experience", render.experience(cfg)))

    for cat, members in groups:
        for r in members:
            readme = model.fix_links(github.readme_html(user, r["name"]), user, r["name"])
            write(OUT / "wiki" / r["name"] / "index.html",
                  page(f"{r['name']} · wiki", r["name"], render.repo_page(user, cat["slug"], r, readme)))

    print(f"built {len(repos)} repo pages into {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
