"""
Shakespeare Character Network Builder
======================================
Scrapes plays from https://shakespeare.mit.edu/ and builds character co-presence
networks where:
  - Nodes  = characters
  - Edges  = two characters share at least one scene together
  - Weight = total lines spoken by both characters across all shared scenes

Usage
-----
    python shakespeare_network.py                          # interactive menu
    python shakespeare_network.py --play hamlet            # single play by slug
    python shakespeare_network.py --all                    # every play
    python shakespeare_network.py --play hamlet --viz      # show network plot
    python shakespeare_network.py --play hamlet --export   # save edges CSV + GEXF

Requirements
------------
    pip install requests beautifulsoup4 networkx matplotlib
"""

import re
import sys
import time
import argparse
import itertools
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

import requests
from bs4 import BeautifulSoup
import networkx as nx

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

BASE_URL = "https://shakespeare.mit.edu"
HEADERS = {"User-Agent": "ShakespeareNetworkBot/1.0 (research; non-commercial)"}
SLEEP_BETWEEN_REQUESTS = 0.4   # seconds – be polite to the server

# Full catalogue of plays (slug → display title)
PLAYS: Dict[str, str] = {
    # Comedies
    "allswell":          "All's Well That Ends Well",
    "asyoulikeit":       "As You Like It",
    "comedy_errors":     "The Comedy of Errors",
    "cymbeline":         "Cymbeline",
    "lll":               "Love's Labours Lost",
    "measure":           "Measure for Measure",
    "merry_wives":       "The Merry Wives of Windsor",
    "merchant":          "The Merchant of Venice",
    "midsummer":         "A Midsummer Night's Dream",
    "much_ado":          "Much Ado About Nothing",
    "pericles":          "Pericles, Prince of Tyre",
    "taming_shrew":      "Taming of the Shrew",
    "tempest":           "The Tempest",
    "troilus_cressida":  "Troilus and Cressida",
    "twelfth_night":     "Twelfth Night",
    "two_gentlemen":     "Two Gentlemen of Verona",
    "winters_tale":      "Winter's Tale",
    # Histories
    "1henryiv":          "Henry IV, Part 1",
    "2henryiv":          "Henry IV, Part 2",
    "henryv":            "Henry V",
    "1henryvi":          "Henry VI, Part 1",
    "2henryvi":          "Henry VI, Part 2",
    "3henryvi":          "Henry VI, Part 3",
    "henryviii":         "Henry VIII",
    "john":              "King John",
    "richardii":         "Richard II",
    "richardiii":        "Richard III",
    # Tragedies
    "cleopatra":         "Antony and Cleopatra",
    "coriolanus":        "Coriolanus",
    "hamlet":            "Hamlet",
    "julius_caesar":     "Julius Caesar",
    "lear":              "King Lear",
    "macbeth":           "Macbeth",
    "othello":           "Othello",
    "romeo_juliet":      "Romeo and Juliet",
    "timon":             "Timon of Athens",
    "titus":             "Titus Andronicus",
}

# Characters to ignore – stage directions or non-speaking roles
IGNORED_SPEAKERS = {
    "ALL", "BOTH", "OMNES", "CHORUS", "PROLOGUE", "EPILOGUE",
    "ATTENDANTS", "SOLDIERS", "LORDS", "CITIZENS", "SERVANTS",
    "MUSICIANS", "PLAYERS",
}


# ──────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────

@dataclass
class SceneData:
    play: str
    act: int
    scene: int
    # character → number of lines spoken in this scene
    line_counts: Dict[str, int] = field(default_factory=dict)


# ──────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────

def _get(url: str) -> Optional[BeautifulSoup]:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException as exc:
        print(f"  [WARN] Failed to fetch {url}: {exc}")
        return None


# ──────────────────────────────────────────────
# Scraping helpers
# ──────────────────────────────────────────────

def _scene_urls_from_index(slug: str) -> List[Tuple[int, int, str]]:
    """
    Scrape the play's index page and return a list of
    (act_number, scene_number, url) tuples.
    """
    index_url = f"{BASE_URL}/{slug}/index.html"
    soup = _get(index_url)
    if soup is None:
        return []

    results: List[Tuple[int, int, str]] = []
    # Links look like:  /hamlet/hamlet.1.1.html
    pattern = re.compile(rf"/{re.escape(slug)}/{re.escape(slug)}\.(\d+)\.(\d+)\.html")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Normalise relative → absolute
        if href.startswith("/"):
            href = BASE_URL + href
        m = pattern.search(href)
        if m:
            act, scene = int(m.group(1)), int(m.group(2))
            results.append((act, scene, href))

    # De-duplicate (some pages list each scene twice)
    seen = set()
    unique = []
    for item in results:
        key = (item[0], item[1])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return sorted(unique)


def _count_lines_in_speech(speech_tag) -> int:
    """
    Count the number of spoken lines in a <blockquote> speech block.
    Each <br/> tag or newline-terminated text node counts as one line.
    Stage directions (italicised <i> inside blockquote) are excluded.
    """
    # Remove stage direction italics
    for i_tag in speech_tag.find_all("i"):
        i_tag.decompose()

    text = speech_tag.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return len(lines)


def parse_scene(slug: str, act: int, scene: int, url: str) -> SceneData:
    """
    Download one scene page and return a SceneData with per-character line counts.

    HTML structure (simplified):
        <b>CHARACTER_NAME</b>          ← speaker
        <blockquote>...</blockquote>   ← their speech
        <i>*stage direction*</i>       ← directions (inside or outside blockquote)

    Characters present in the scene are those who have at least one <b> speaker tag.
    """
    data = SceneData(play=slug, act=act, scene=scene)
    soup = _get(url)
    if soup is None:
        return data

    # The play text lives inside the main table cell
    # We walk through <b> tags (speakers) followed by <blockquote> (speech)
    body = soup.find("body")
    if body is None:
        return data

    current_speaker: Optional[str] = None
    for tag in body.find_all(["b", "blockquote"]):
        if tag.name == "b":
            raw = tag.get_text(separator=" ").strip()
            # Speaker names are ALL-CAPS (possibly with spaces / periods)
            if raw and raw == raw.upper() and len(raw) > 1:
                name = re.sub(r"\s+", " ", raw).strip().rstrip(".")
                if name not in IGNORED_SPEAKERS:
                    current_speaker = name
                    # Ensure the character is registered even if speech block is missing
                    if current_speaker not in data.line_counts:
                        data.line_counts[current_speaker] = 0
                else:
                    current_speaker = None
        elif tag.name == "blockquote" and current_speaker:
            n = _count_lines_in_speech(tag)
            data.line_counts[current_speaker] = data.line_counts.get(current_speaker, 0) + n

    return data


# ──────────────────────────────────────────────
# Network builder
# ──────────────────────────────────────────────

def build_network(scenes: List[SceneData]) -> nx.Graph:
    """
    Build a weighted undirected character co-presence network.

    Edge weight = total lines spoken by BOTH characters summed over every
    scene they share together.
    """
    G = nx.Graph()

    for scene in scenes:
        characters = list(scene.line_counts.keys())
        total_lines_in_scene = sum(scene.line_counts.values())

        # Add / update nodes with cumulative line counts
        for char in characters:
            if G.has_node(char):
                G.nodes[char]["total_lines"] += scene.line_counts[char]
                G.nodes[char]["scenes"] += 1
            else:
                G.add_node(char,
                           total_lines=scene.line_counts[char],
                           scenes=1)

        # Add / update edges
        for c1, c2 in itertools.combinations(characters, 2):
            # Weight = lines spoken by BOTH characters in this scene combined
            shared_lines = scene.line_counts[c1] + scene.line_counts[c2]
            scene_label = f"{scene.play} {scene.act}.{scene.scene}"

            if G.has_edge(c1, c2):
                G[c1][c2]["weight"] += shared_lines
                G[c1][c2]["scenes"] += 1
                G[c1][c2]["scene_list"].append(scene_label)
            else:
                G.add_edge(c1, c2,
                           weight=shared_lines,
                           scenes=1,
                           scene_list=[scene_label])

    return G


# ──────────────────────────────────────────────
# I/O helpers
# ──────────────────────────────────────────────

def print_network_summary(G: nx.Graph, title: str) -> None:
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")
    print(f"  Nodes (characters) : {G.number_of_nodes()}")
    print(f"  Edges (co-scenes)  : {G.number_of_edges()}")

    if G.number_of_edges() == 0:
        print("  (No edges found – check scraping.)")
        return

    # Top characters by total lines
    top_nodes = sorted(G.nodes(data=True),
                       key=lambda x: x[1].get("total_lines", 0),
                       reverse=True)[:10]
    print("\n  Top 10 characters by lines spoken:")
    for name, attrs in top_nodes:
        print(f"    {name:<30} {attrs.get('total_lines', 0):>5} lines  "
              f"({attrs.get('scenes', 0)} scenes)")

    # Top edges by weight
    top_edges = sorted(G.edges(data=True),
                       key=lambda x: x[2].get("weight", 0),
                       reverse=True)[:10]
    print("\n  Top 10 character pairings by shared-line weight:")
    for u, v, attrs in top_edges:
        print(f"    {u:<22} ↔  {v:<22}  weight={attrs['weight']:>5}  "
              f"({attrs['scenes']} shared scene(s))")

    # Basic network metrics
    if G.number_of_nodes() > 1:
        largest_cc = max(nx.connected_components(G), key=len)
        sub = G.subgraph(largest_cc)
        try:
            avg_path = nx.average_shortest_path_length(sub)
            print(f"\n  Avg. shortest path (largest component): {avg_path:.3f}")
        except Exception:
            pass
        density = nx.density(G)
        print(f"  Graph density                          : {density:.4f}")


def export_graph(G: nx.Graph, slug: str) -> None:
    """Save edges as CSV and the full graph as GEXF (Gephi-compatible)."""
    csv_path = f"{slug}_edges.csv"
    gexf_path = f"{slug}_network.gexf"

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("source,target,weight,shared_scenes\n")
        for u, v, d in sorted(G.edges(data=True),
                               key=lambda x: x[2].get("weight", 0),
                               reverse=True):
            f.write(f"{u},{v},{d['weight']},{d['scenes']}\n")

    nx.write_gexf(G, gexf_path)
    print(f"\n  ✓ Edges CSV  → {csv_path}")
    print(f"  ✓ GEXF graph → {gexf_path}  (open with Gephi for full exploration)")


def visualize_network(G: nx.Graph, title: str) -> None:
    """Draw the network with matplotlib. Requires matplotlib."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import numpy as np
    except ImportError:
        print("  [WARN] matplotlib not installed – skipping visualisation.")
        return

    if G.number_of_nodes() == 0:
        print("  [WARN] Empty graph – nothing to draw.")
        return

    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    # Layout – spring layout weighted by inverse weight (closer = more connected)
    pos = nx.spring_layout(G, weight="weight", k=2.5, seed=42, iterations=80)

    # Node sizes proportional to total lines spoken
    node_sizes = [max(100, G.nodes[n].get("total_lines", 0) * 3)
                  for n in G.nodes()]

    # Edge widths and colours proportional to weight
    weights = [d["weight"] for _, _, d in G.edges(data=True)]
    max_w = max(weights) if weights else 1
    edge_widths = [0.5 + 4.0 * w / max_w for w in weights]

    # Degree-based node colouring
    degrees = dict(G.degree())
    node_colours = [degrees[n] for n in G.nodes()]

    nx.draw_networkx_edges(G, pos, ax=ax,
                           width=edge_widths,
                           alpha=0.35,
                           edge_color=weights,
                           edge_cmap=cm.plasma)

    nc = nx.draw_networkx_nodes(G, pos, ax=ax,
                                node_size=node_sizes,
                                node_color=node_colours,
                                cmap=cm.cool,
                                alpha=0.9)

    # Only label the most prominent characters
    threshold = sorted(node_sizes, reverse=True)[min(20, len(node_sizes) - 1)]
    labels = {n: n for n, s in zip(G.nodes(), node_sizes) if s >= threshold}
    nx.draw_networkx_labels(G, pos, labels, ax=ax,
                            font_size=8, font_color="white",
                            font_weight="bold")

    plt.colorbar(nc, ax=ax, label="Node degree", shrink=0.6)
    ax.set_title(title, color="white", fontsize=14, pad=20)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


# ──────────────────────────────────────────────
# Main pipeline
# ──────────────────────────────────────────────

def process_play(slug: str, visualise: bool = False,
                 export: bool = False) -> nx.Graph:
    title = PLAYS.get(slug, slug)
    print(f"\n► Scraping «{title}» …")

    scene_urls = _scene_urls_from_index(slug)
    if not scene_urls:
        print(f"  [ERROR] Could not find scene list for slug '{slug}'.")
        return nx.Graph()

    print(f"  Found {len(scene_urls)} scenes.")
    scenes: List[SceneData] = []

    for act, scene_num, url in scene_urls:
        print(f"  Parsing Act {act}, Scene {scene_num} … ", end="", flush=True)
        sd = parse_scene(slug, act, scene_num, url)
        scenes.append(sd)
        chars = len(sd.line_counts)
        total = sum(sd.line_counts.values())
        print(f"{chars} characters, {total} lines")

    G = build_network(scenes)
    print_network_summary(G, f"Character Network – {title}")

    if export:
        export_graph(G, slug)

    if visualise:
        visualize_network(G, f"Character Co-Presence Network\n{title}")

    return G


def interactive_menu() -> None:
    print("\n╔══════════════════════════════════════════════╗")
    print("║   Shakespeare Character Network Builder      ║")
    print("╚══════════════════════════════════════════════╝")
    print("\nAvailable plays:")

    slugs = list(PLAYS.keys())
    for i, slug in enumerate(slugs):
        print(f"  [{i+1:2d}] {PLAYS[slug]}")

    print("\nEnter a number (or comma-separated numbers), 'all', or 'q' to quit:")
    choice = input("  > ").strip().lower()

    if choice in ("q", "quit", "exit"):
        return

    viz = input("  Show visualisation? [y/N]: ").strip().lower() == "y"
    exp = input("  Export CSV + GEXF?  [y/N]: ").strip().lower() == "y"

    if choice == "all":
        selected = slugs
    else:
        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
        selected = [slugs[i] for i in indices if 0 <= i < len(slugs)]

    if not selected:
        print("  No valid selection made.")
        return

    graphs: Dict[str, nx.Graph] = {}
    for slug in selected:
        graphs[slug] = process_play(slug, visualise=viz, export=exp)

    print(f"\n✓ Done. Processed {len(graphs)} play(s).")
    return graphs


# ──────────────────────────────────────────────
# CLI entry-point
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build Shakespeare character co-presence networks.")
    parser.add_argument("--play",   help="Play slug (e.g. hamlet, macbeth)")
    parser.add_argument("--all",    action="store_true",
                        help="Process every play")
    parser.add_argument("--viz",    action="store_true",
                        help="Show network visualisation (requires matplotlib)")
    parser.add_argument("--export", action="store_true",
                        help="Export edges CSV and GEXF file")
    parser.add_argument("--list",   action="store_true",
                        help="Print available play slugs and exit")
    args = parser.parse_args()

    if args.list:
        for slug, title in PLAYS.items():
            print(f"  {slug:<20} {title}")
        return

    if args.all:
        for slug in PLAYS:
            process_play(slug, visualise=args.viz, export=args.export)
    elif args.play:
        slug = args.play.lower()
        if slug not in PLAYS:
            print(f"Unknown play '{slug}'. Use --list to see valid slugs.")
            sys.exit(1)
        process_play(slug, visualise=args.viz, export=args.export)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
