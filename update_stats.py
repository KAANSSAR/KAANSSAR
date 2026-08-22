"""
Fetches real stats (repos, stars, followers, top languages, contribution
streak) via GitHub's GraphQL API using the Action's built-in GITHUB_TOKEN,
and regenerates stats-card.svg. No external services, no extra secrets.
"""
import json
import os
import urllib.request
from datetime import datetime
from render_stats import build

USERNAME = "KAANSSAR"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliation: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""

def gql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-readme-stats-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def compute_streaks(days):
    # days: chronological list of (date_str, count)
    last_active = None
    for i in range(len(days) - 1, -1, -1):
        if days[i][1] > 0:
            last_active = i
            break
    current = 0
    current_since = None
    if last_active is not None:
        i = last_active
        while i >= 0 and days[i][1] > 0:
            current += 1
            i -= 1
        current_since = days[last_active - current + 1][0]

    longest = 0
    run = 0
    for _, c in days:
        if c > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return current, longest, current_since

def main():
    try:
        data = gql(QUERY, {"login": USERNAME})
        user = data["data"]["user"]
    except Exception as e:
        print(f"warn: GraphQL fetch failed: {e}")
        user = None

    if user is None:
        stats_data = [("Public Repos", "--"), ("Total Stars", "--"),
                       ("Followers", "--"), ("Contributions", "--")]
        langs = []
        streak_data = dict(current=0, longest=0, total=0, current_since=None, longest_range=None)
    else:
        repos = user["repositories"]["nodes"]
        total_repos = user["repositories"]["totalCount"]
        total_stars = sum(r["stargazerCount"] for r in repos)
        followers = user["followers"]["totalCount"]

        lang_sizes = {}
        lang_colors = {}
        for r in repos:
            for edge in r["languages"]["edges"]:
                name = edge["node"]["name"]
                lang_sizes[name] = lang_sizes.get(name, 0) + edge["size"]
                lang_colors[name] = edge["node"]["color"] or "#8a93a6"
        total_size = sum(lang_sizes.values()) or 1
        top_langs = sorted(lang_sizes.items(), key=lambda kv: kv[1], reverse=True)[:5]
        langs = [(name, size / total_size * 100, lang_colors[name]) for name, size in top_langs]

        cal = user["contributionsCollection"]["contributionCalendar"]
        total_contrib = cal["totalContributions"]
        days = []
        for week in cal["weeks"]:
            for d in week["contributionDays"]:
                days.append((d["date"], d["contributionCount"]))
        current, longest, current_since = compute_streaks(days)
        if current_since:
            current_since = datetime.strptime(current_since, "%Y-%m-%d").strftime("%b %-d")

        stats_data = [
            ("Public Repos", str(total_repos)),
            ("Total Stars", str(total_stars)),
            ("Followers", str(followers)),
            ("Contributions", str(total_contrib)),
        ]
        streak_data = dict(current=current, longest=longest, total=total_contrib,
                            current_since=current_since, longest_range=None)

    svg = build(stats_data, langs, streak_data)
    with open("stats-card.svg", "w") as f:
        f.write(svg)
    print("wrote stats-card.svg")

if __name__ == "__main__":
    main()
