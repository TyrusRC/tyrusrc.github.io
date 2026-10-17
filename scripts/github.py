"""Read-only GitHub API access: public repo list and rendered READMEs."""

import json
import os
import urllib.error
import urllib.request

API = "https://api.github.com"


def _get(url, accept):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "tyrusrc-site"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def public_repos(user):
    """Every repo GitHub lists publicly for `user` (paginated)."""
    repos, page = [], 1
    while True:
        batch = json.loads(_get(f"{API}/users/{user}/repos?type=owner&per_page=100&page={page}",
                                "application/vnd.github+json"))
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def readme_html(user, repo):
    """README rendered to (GitHub-sanitized) HTML, or "" when the repo has none."""
    try:
        return _get(f"{API}/repos/{user}/{repo}/readme", "application/vnd.github.html+json")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise
