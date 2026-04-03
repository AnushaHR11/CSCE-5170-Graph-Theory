"""
Shakespeare Directed Mention / Address Network
================================================
Scrapes plays from https://shakespeare.mit.edu/ and builds DIRECTED character
networks where:

  - Nodes  = characters
  - Edges  = directed arc  SPEAKER → MENTIONED/ADDRESSED character
  - Weight = number of lines spoken by SPEAKER in speeches where they
             mention / address the target character

Two detection strategies are combined:
  1. NAME / APPELLATION MENTION  – the target's name or a known alias appears
     anywhere in the speaker's speech text.
  2. DIRECT ADDRESS (vocative)   – a character is called by name or title
     in a direct-address pattern (e.g. "Good Horatio,", "My lord,", "O Romeo!").

A rich alias table covers ~250 appellations used across the canon so that
"sweet prince", "my lord", "good king", "fair Ophelia" etc. all resolve to
the correct character for the play being processed.

Usage
-----
    python shakespeare_mention_network.py                     # interactive
    python shakespeare_mention_network.py --play hamlet
    python shakespeare_mention_network.py --play hamlet --viz
    python shakespeare_mention_network.py --play hamlet --export
    python shakespeare_mention_network.py --all

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
from typing import Dict, List, Tuple, Set, Optional

import requests
from bs4 import BeautifulSoup
import networkx as nx

# ──────────────────────────────────────────────────────────────────────────────
# Play catalogue  (slug → display title)
# ──────────────────────────────────────────────────────────────────────────────

PLAYS: Dict[str, str] = {
    "allswell": "All's Well That Ends Well",
    "asyoulikeit": "As You Like It",
    "comedy_errors": "The Comedy of Errors",
    "cymbeline": "Cymbeline",
    "lll": "Love's Labours Lost",
    "measure": "Measure for Measure",
    "merry_wives": "The Merry Wives of Windsor",
    "merchant": "The Merchant of Venice",
    "midsummer": "A Midsummer Night's Dream",
    "much_ado": "Much Ado About Nothing",
    "pericles": "Pericles, Prince of Tyre",
    "taming_shrew": "Taming of the Shrew",
    "tempest": "The Tempest",
    "troilus_cressida": "Troilus and Cressida",
    "twelfth_night": "Twelfth Night",
    "two_gentlemen": "Two Gentlemen of Verona",
    "winters_tale": "Winter's Tale",
    "1henryiv": "Henry IV, Part 1",
    "2henryiv": "Henry IV, Part 2",
    "henryv": "Henry V",
    "1henryvi": "Henry VI, Part 1",
    "2henryvi": "Henry VI, Part 2",
    "3henryvi": "Henry VI, Part 3",
    "henryviii": "Henry VIII",
    "john": "King John",
    "richardii": "Richard II",
    "richardiii": "Richard III",
    "cleopatra": "Antony and Cleopatra",
    "coriolanus": "Coriolanus",
    "hamlet": "Hamlet",
    "julius_caesar": "Julius Caesar",
    "lear": "King Lear",
    "macbeth": "Macbeth",
    "othello": "Othello",
    "romeo_juliet": "Romeo and Juliet",
    "timon": "Timon of Athens",
    "titus": "Titus Andronicus",
}

BASE_URL = "https://shakespeare.mit.edu"
HEADERS = {"User-Agent": "ShakespeareNetworkBot/1.0 (research; non-commercial)"}
SLEEP = 0.4

# ──────────────────────────────────────────────────────────────────────────────
# Per-play alias tables
# Each entry:  canonical_character_name → [alias, alias, ...]
# Aliases are matched case-insensitively as whole words inside speech text.
# Longer / more specific aliases must appear BEFORE shorter ones to avoid
# false-positive sub-matches (handled by sorting by length desc at runtime).
# ──────────────────────────────────────────────────────────────────────────────

PLAY_ALIASES: Dict[str, Dict[str, List[str]]] = {

    "hamlet": {
        "HAMLET":    ["Hamlet", "sweet prince", "young Hamlet", "prince",
                      "dear Hamlet", "good Hamlet", "noble Hamlet"],
        "HORATIO":   ["Horatio", "good Horatio", "dear Horatio"],
        "OPHELIA":   ["Ophelia", "fair Ophelia", "sweet Ophelia", "dear Ophelia",
                      "the fair Ophelia"],
        "LAERTES":   ["Laertes", "good Laertes", "dear Laertes"],
        "POLONIUS":  ["Polonius", "old Polonius", "good Polonius",
                      "the old man", "my lord Polonius"],
        "GERTRUDE":  ["Gertrude", "the queen", "good queen", "dear mother",
                      "sweet queen", "mother"],
        "CLAUDIUS":  ["Claudius", "the king", "good king", "my lord king",
                      "uncle", "dear uncle", "my uncle"],
        "GHOST":     ["the ghost", "king Hamlet", "thy father", "my father",
                      "the spirit", "his father"],
        "ROSENCRANTZ":  ["Rosencrantz"],
        "GUILDENSTERN": ["Guildenstern"],
        "OSRIC":     ["Osric", "young Osric"],
        "FORTINBRAS":["Fortinbras", "young Fortinbras"],
        "MARCELLUS": ["Marcellus", "good Marcellus"],
        "BERNARDO":  ["Bernardo"],
        "FRANCISCO": ["Francisco"],
    },

    "macbeth": {
        "MACBETH":   ["Macbeth", "brave Macbeth", "valiant Macbeth",
                      "the thane of Cawdor", "noble Macbeth", "great Macbeth"],
        "LADY MACBETH": ["Lady Macbeth", "my dearest love", "dearest partner",
                         "gentle lady", "sweet remembrancer", "my wife"],
        "DUNCAN":    ["Duncan", "the king", "good king", "good Duncan",
                      "gracious Duncan", "king Duncan"],
        "MALCOLM":   ["Malcolm", "good Malcolm", "prince Malcolm",
                      "young Malcolm"],
        "DONALBAIN": ["Donalbain"],
        "BANQUO":    ["Banquo", "good Banquo", "brave Banquo", "noble Banquo"],
        "MACDUFF":   ["Macduff", "good Macduff", "brave Macduff",
                      "noble Macduff", "thane of Fife"],
        "LADY MACDUFF": ["Lady Macduff"],
        "ROSS":      ["Ross", "good Ross"],
        "LENNOX":    ["Lennox"],
        "HECATE":    ["Hecate"],
        "SIWARD":    ["Siward", "old Siward", "good Siward"],
    },

    "romeo_juliet": {
        "ROMEO":     ["Romeo", "sweet Romeo", "dear Romeo", "gentle Romeo",
                      "young Romeo", "good Romeo", "fair Romeo"],
        "JULIET":    ["Juliet", "sweet Juliet", "dear Juliet", "fair Juliet",
                      "beautiful Juliet", "gentle Juliet", "my Juliet"],
        "FRIAR LAURENCE": ["Friar Laurence", "friar", "good friar",
                           "holy friar", "dear friar", "ghostly father"],
        "NURSE":     ["Nurse", "good nurse", "sweet nurse", "dear nurse",
                      "ancient damnation"],
        "MERCUTIO":  ["Mercutio", "good Mercutio", "brave Mercutio"],
        "BENVOLIO":  ["Benvolio", "cousin Benvolio", "good Benvolio"],
        "TYBALT":    ["Tybalt", "cousin Tybalt", "King of cats",
                      "good Tybalt"],
        "CAPULET":   ["Capulet", "old Capulet", "father Capulet",
                      "good father", "my father", "dear father"],
        "LADY CAPULET": ["Lady Capulet", "my lady", "good lady mother",
                          "dear mother"],
        "MONTAGUE":  ["Montague", "old Montague"],
        "PARIS":     ["Paris", "good Paris", "young Paris", "Count Paris",
                      "the county"],
        "PRINCE":    ["Prince", "the prince", "his highness"],
        "BALTHASAR": ["Balthasar"],
        "ROSALINE":  ["Rosaline", "fair Rosaline"],
        "FRIAR JOHN":["Friar John"],
    },

    "othello": {
        "OTHELLO":   ["Othello", "the Moor", "brave Othello", "noble Othello",
                      "good Othello", "valiant Othello", "the noble Moor"],
        "DESDEMONA": ["Desdemona", "sweet Desdemona", "fair Desdemona",
                      "gentle Desdemona", "good Desdemona", "dear Desdemona",
                      "my Desdemona"],
        "IAGO":      ["Iago", "good Iago", "honest Iago", "dear Iago"],
        "CASSIO":    ["Cassio", "good Cassio", "dear Cassio", "brave Cassio",
                      "lieutenant Cassio", "the lieutenant"],
        "EMILIA":    ["Emilia", "good Emilia", "dear Emilia", "sweet Emilia"],
        "RODERIGO":  ["Roderigo", "good Roderigo", "poor Roderigo"],
        "BRABANTIO": ["Brabantio", "good Brabantio", "signior Brabantio"],
        "BIANCA":    ["Bianca"],
        "LODOVICO":  ["Lodovico"],
        "MONTANO":   ["Montano", "good Montano"],
        "DUKE":      ["the Duke", "most potent grave"],
    },

    "lear": {
        "LEAR":      ["Lear", "good king", "dear father", "old man",
                      "king Lear", "my father", "poor old man",
                      "the old king"],
        "CORDELIA":  ["Cordelia", "dear Cordelia", "sweet Cordelia",
                      "fair Cordelia", "poor Cordelia"],
        "GONERIL":   ["Goneril", "dear Goneril"],
        "REGAN":     ["Regan", "dear Regan"],
        "EDGAR":     ["Edgar", "good Edgar", "poor Edgar", "Tom o' Bedlam",
                      "poor Tom"],
        "EDMUND":    ["Edmund", "bastard Edmund", "good Edmund"],
        "KENT":      ["Kent", "good Kent", "old Kent", "dear Kent",
                      "noble Kent"],
        "GLOUCESTER":["Gloucester", "good Gloucester", "old Gloucester",
                      "earl of Gloucester"],
        "FOOL":      ["the Fool", "good fool", "my fool", "sweet fool",
                      "poor fool"],
        "ALBANY":    ["Albany", "good Albany", "dear Albany"],
        "CORNWALL":  ["Cornwall"],
        "OSWALD":    ["Oswald"],
    },

    "julius_caesar": {
        "CAESAR":    ["Caesar", "Julius Caesar", "great Caesar",
                      "noble Caesar", "brave Caesar", "the mighty Caesar"],
        "BRUTUS":    ["Brutus", "good Brutus", "noble Brutus", "brave Brutus",
                      "gentle Brutus", "dear Brutus"],
        "CASSIUS":   ["Cassius", "good Cassius", "noble Cassius",
                      "dear Cassius", "brave Cassius"],
        "ANTONY":    ["Antony", "Mark Antony", "good Antony", "noble Antony",
                      "brave Antony", "friend Antony"],
        "PORTIA":    ["Portia", "gentle Portia", "good Portia", "dear Portia"],
        "CALPURNIA": ["Calpurnia", "dear Calpurnia"],
        "OCTAVIUS":  ["Octavius", "young Octavius"],
        "CASCA":     ["Casca", "good Casca"],
        "DECIUS":    ["Decius", "good Decius"],
        "CICERO":    ["Cicero", "old Cicero"],
        "SOOTHSAYER":["the soothsayer"],
    },

    "midsummer": {
        "OBERON":    ["Oberon", "jealous Oberon", "king of shadows"],
        "TITANIA":   ["Titania", "proud Titania", "queen of fairies",
                      "fair queen", "my queen"],
        "PUCK":      ["Puck", "Robin Goodfellow", "good Robin", "sweet Puck"],
        "HERMIA":    ["Hermia", "fair Hermia", "sweet Hermia", "dear Hermia",
                      "little Hermia"],
        "HELENA":    ["Helena", "fair Helena", "sweet Helena", "dear Helena",
                      "poor Helena"],
        "LYSANDER":  ["Lysander", "sweet Lysander", "good Lysander"],
        "DEMETRIUS": ["Demetrius", "good Demetrius"],
        "BOTTOM":    ["Bottom", "bully Bottom", "sweet bully Bottom",
                      "gentle Bottom"],
        "QUINCE":    ["Quince", "Peter Quince"],
        "TITANIA":   ["Titania"],
        "EGEUS":     ["Egeus"],
        "THESEUS":   ["Theseus", "duke Theseus"],
        "HIPPOLYTA": ["Hippolyta"],
    },

    "merchant": {
        "PORTIA":    ["Portia", "fair Portia", "gentle Portia", "sweet Portia",
                      "dear Portia", "divine Portia"],
        "BASSANIO":  ["Bassanio", "sweet Bassanio", "dear Bassanio",
                      "good Bassanio"],
        "SHYLOCK":   ["Shylock", "the Jew", "old Shylock"],
        "ANTONIO":   ["Antonio", "good Antonio", "dear Antonio",
                      "noble Antonio"],
        "GRATIANO":  ["Gratiano", "good Gratiano"],
        "JESSICA":   ["Jessica", "sweet Jessica", "fair Jessica"],
        "NERISSA":   ["Nerissa", "gentle Nerissa", "sweet Nerissa",
                      "dear Nerissa"],
        "LORENZO":   ["Lorenzo", "dear Lorenzo", "sweet Lorenzo"],
        "LAUNCELOT": ["Launcelot", "good Launcelot"],
        "GOBBO":     ["Gobbo", "old Gobbo"],
    },

    "tempest": {
        "PROSPERO":  ["Prospero", "my master", "good master",
                      "dear master", "reverend master"],
        "MIRANDA":   ["Miranda", "fair Miranda", "sweet Miranda",
                      "dear Miranda", "my daughter"],
        "ARIEL":     ["Ariel", "spirit", "my Ariel", "dainty Ariel",
                      "delicate Ariel"],
        "CALIBAN":   ["Caliban", "thou earth", "savage Caliban"],
        "FERDINAND": ["Ferdinand", "good Ferdinand", "sweet Ferdinand"],
        "ALONSO":    ["Alonso", "good Alonso"],
        "GONZALO":   ["Gonzalo", "good Gonzalo", "honest Gonzalo",
                      "noble Gonzalo"],
        "STEPHANO":  ["Stephano", "good Stephano"],
        "TRINCULO":  ["Trinculo", "good Trinculo"],
        "ANTONIO":   ["Antonio", "false Antonio"],
        "SEBASTIAN": ["Sebastian"],
    },

    "twelfth_night": {
        "VIOLA":     ["Viola", "fair lady", "sweet lady"],
        "ORSINO":    ["Orsino", "good my lord", "noble duke"],
        "OLIVIA":    ["Olivia", "fair Olivia", "sweet Olivia",
                      "dear Olivia", "madam"],
        "MALVOLIO":  ["Malvolio", "good Malvolio"],
        "SIR TOBY":  ["Sir Toby", "good Sir Toby", "dear Sir Toby",
                      "cousin Toby"],
        "SIR ANDREW":["Sir Andrew", "good Sir Andrew"],
        "FESTE":     ["Feste", "clown", "good fool", "my fool"],
        "MARIA":     ["Maria", "good Maria", "sweet Maria", "gentle Maria"],
        "ANTONIO":   ["Antonio", "good Antonio"],
        "SEBASTIAN": ["Sebastian", "sweet Sebastian"],
    },

    "cleopatra": {
        "ANTONY":    ["Antony", "Mark Antony", "great Antony", "brave Antony",
                      "noble Antony", "noble lord", "Lord Antony",
                      "my lord", "my Antony"],
        "CLEOPATRA": ["Cleopatra", "great Cleopatra", "noble Cleopatra",
                      "fair Cleopatra", "my queen", "Egypt",
                      "the queen", "sweet queen"],
        "ENOBARBUS": ["Enobarbus", "good Enobarbus", "dear Enobarbus"],
        "OCTAVIUS":  ["Octavius", "Caesar", "young Caesar", "great Caesar",
                      "Octavius Caesar"],
        "CHARMIAN":  ["Charmian", "dear Charmian", "sweet Charmian"],
        "IRAS":      ["Iras", "dear Iras"],
        "LEPIDUS":   ["Lepidus", "good Lepidus"],
        "POMPEY":    ["Pompey", "good Pompey"],
        "OCTAVIA":   ["Octavia", "fair Octavia"],
        "AGRIPPA":   ["Agrippa"],
        "MENAS":     ["Menas"],
    },

    "much_ado": {
        "BENEDICK":  ["Benedick", "good Benedick", "dear Benedick",
                      "kind Benedick"],
        "BEATRICE":  ["Beatrice", "dear Beatrice", "sweet Beatrice",
                      "fair Beatrice", "Lady Beatrice"],
        "CLAUDIO":   ["Claudio", "good Claudio", "young Claudio",
                      "dear Claudio"],
        "HERO":      ["Hero", "fair Hero", "sweet Hero", "dear Hero",
                      "gentle Hero"],
        "DON PEDRO": ["Don Pedro", "my lord", "prince"],
        "LEONATO":   ["Leonato", "good Leonato", "dear Leonato",
                      "old Leonato"],
        "DON JOHN":  ["Don John", "John", "bastard"],
        "BORACHIO":  ["Borachio"],
        "DOGBERRY":  ["Dogberry", "master constable"],
    },

    "asyoulikeit": {
        "ROSALIND":  ["Rosalind", "fair Rosalind", "sweet Rosalind",
                      "dear Rosalind", "Ganymede"],
        "CELIA":     ["Celia", "dear Celia", "sweet Celia",
                      "gentle Celia", "Aliena"],
        "ORLANDO":   ["Orlando", "good Orlando", "dear Orlando",
                      "sweet Orlando"],
        "JAQUES":    ["Jaques", "good Jaques", "melancholy Jaques"],
        "DUKE SENIOR": ["Duke Senior", "the duke", "good duke"],
        "TOUCHSTONE":  ["Touchstone", "the clown", "good clown"],
        "OLIVER":    ["Oliver", "dear Oliver"],
        "SILVIUS":   ["Silvius", "sweet Silvius"],
        "PHEBE":     ["Phebe", "fair Phebe", "sweet Phebe"],
        "AUDREY":    ["Audrey"],
        "ADAM":      ["Adam", "good old Adam"],
        "CORIN":     ["Corin", "good Corin"],
    },

    "richardiii": {
        "RICHARD":   ["Richard", "Gloucester", "king Richard",
                      "good Richard", "brave Richard"],
        "ANNE":      ["Anne", "Lady Anne", "sweet Anne", "fair Anne",
                      "dear Anne"],
        "BUCKINGHAM":["Buckingham", "good Buckingham", "dear Buckingham",
                      "my Buckingham"],
        "RICHMOND":  ["Richmond", "brave Richmond"],
        "CLARENCE":  ["Clarence", "good Clarence", "dear Clarence",
                      "poor Clarence"],
        "MARGARET":  ["Margaret", "old Margaret", "cursed Margaret"],
        "ELIZABETH": ["Elizabeth", "queen Elizabeth"],
        "HASTINGS":  ["Hastings", "good Hastings", "lord Hastings"],
        "CATESBY":   ["Catesby", "good Catesby"],
        "STANLEY":   ["Stanley"],
    },
}

# Generic appellations that are too ambiguous to resolve cross-play
SKIP_APPELLATIONS = {
    "sir", "madam", "lord", "lady", "my lord", "good lord",
    "my lady", "good lady", "dear sir", "good sir",
    "my liege", "your grace", "your majesty", "your highness",
    "friend", "good friend", "dear friend",
    "cousin", "brother", "sister",
    "fellow", "knave", "villain", "traitor", "fool",
}

# ──────────────────────────────────────────────────────────────────────────────
# Data structure
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class MentionRecord:
    """One mention event: SPEAKER mentions TARGET in a speech of `lines` lines."""
    speaker: str
    target: str
    lines: int
    act: int
    scene: int
    alias_matched: str       # which alias triggered the detection


# ──────────────────────────────────────────────────────────────────────────────
# HTTP helper
# ──────────────────────────────────────────────────────────────────────────────

def _get(url: str) -> Optional[BeautifulSoup]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        time.sleep(SLEEP)
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException as exc:
        print(f"  [WARN] {url}: {exc}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Alias utilities
# ──────────────────────────────────────────────────────────────────────────────

def build_alias_map(slug: str,
                    play_characters: Set[str]) -> Dict[str, str]:
    """
    Return a dict  alias_pattern → canonical_name.

    Sources (in priority order):
      1. Per-play hand-curated table (PLAY_ALIASES).
      2. Auto-generated from character names found in the play:
         first name, full name, title-stripped name.
    """
    alias_map: Dict[str, str] = {}

    # --- 1. Hand-curated aliases ---
    curated = PLAY_ALIASES.get(slug, {})
    for canonical, aliases in curated.items():
        for alias in aliases:
            lc = alias.lower().strip()
            if lc not in SKIP_APPELLATIONS:
                alias_map[lc] = canonical

    # --- 2. Auto-generate from character names ---
    for char in play_characters:
        # Full name
        lc_full = char.lower()
        if lc_full not in alias_map and lc_full not in SKIP_APPELLATIONS:
            alias_map[lc_full] = char

        # First word only (handles "LADY MACBETH" → "macbeth" last resort)
        parts = char.split()
        if len(parts) > 1:
            lc_first = parts[-1].lower()   # last word usually the personal name
            if lc_first not in alias_map and lc_first not in SKIP_APPELLATIONS:
                alias_map[lc_first] = char

    # Sort by length descending so longer patterns match first
    return dict(sorted(alias_map.items(), key=lambda x: len(x[0]), reverse=True))


def build_regex(alias_map: Dict[str, str]):
    """
    Compile a single regex that matches any alias as a whole word/phrase.
    Returns (compiled_regex, alias_map).
    """
    # Escape each alias for regex, wrap as a whole-word boundary match
    patterns = []
    for alias in alias_map:
        escaped = re.escape(alias)
        # For multi-word aliases, use lookahead/behind for word boundaries
        patterns.append(r"(?<!\w)" + escaped + r"(?!\w)")

    combined = "|".join(patterns)
    return re.compile(combined, re.IGNORECASE)


# ──────────────────────────────────────────────────────────────────────────────
# Scraping
# ──────────────────────────────────────────────────────────────────────────────

def _scene_urls(slug: str) -> List[Tuple[int, int, str]]:
    index_url = f"{BASE_URL}/{slug}/index.html"
    soup = _get(index_url)
    if soup is None:
        return []

    pattern = re.compile(
        rf"/{re.escape(slug)}/{re.escape(slug)}\.(\d+)\.(\d+)\.html"
    )
    seen: set = set()
    results: List[Tuple[int, int, str]] = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            href = BASE_URL + href
        m = pattern.search(href)
        if m:
            act, scene = int(m.group(1)), int(m.group(2))
            key = (act, scene)
            if key not in seen:
                seen.add(key)
                results.append((act, scene, href))

    return sorted(results)


def _count_speech_lines(blockquote_tag) -> int:
    """Count non-empty spoken lines, ignoring stage-direction italics."""
    for i in blockquote_tag.find_all("i"):
        i.decompose()
    text = blockquote_tag.get_text(separator="\n")
    return sum(1 for ln in text.splitlines() if ln.strip())


def _speech_text_clean(blockquote_tag) -> str:
    """Return speech text with stage directions removed."""
    bq = blockquote_tag.__copy__() if hasattr(blockquote_tag, "__copy__") else blockquote_tag
    tag_copy = BeautifulSoup(str(blockquote_tag), "html.parser")
    for i in tag_copy.find_all("i"):
        i.decompose()
    return tag_copy.get_text(separator=" ")


IGNORED_SPEAKERS = {
    "ALL", "BOTH", "OMNES", "CHORUS", "PROLOGUE", "EPILOGUE",
    "ATTENDANTS", "SOLDIERS", "LORDS", "CITIZENS", "SERVANTS",
    "MUSICIANS", "PLAYERS",
}


def scrape_scene(slug: str, act: int, scene: int,
                 url: str) -> Tuple[List[Tuple[str, str, int]], Set[str]]:
    """
    Returns:
      speeches  – list of (speaker, speech_text, line_count)
      characters – set of all speaker names found in this scene
    """
    soup = _get(url)
    if soup is None:
        return [], set()

    body = soup.find("body")
    if body is None:
        return [], set()

    speeches: List[Tuple[str, str, int]] = []
    characters: Set[str] = set()
    current_speaker: Optional[str] = None

    for tag in body.find_all(["b", "blockquote"]):
        if tag.name == "b":
            raw = tag.get_text(separator=" ").strip()
            if raw and raw == raw.upper() and len(raw) > 1:
                name = re.sub(r"\s+", " ", raw).strip().rstrip(".")
                if name not in IGNORED_SPEAKERS:
                    current_speaker = name
                    characters.add(name)
                else:
                    current_speaker = None
        elif tag.name == "blockquote" and current_speaker:
            n_lines = _count_speech_lines(
                BeautifulSoup(str(tag), "html.parser").find("blockquote") or tag
            )
            text = _speech_text_clean(tag)
            speeches.append((current_speaker, text, n_lines))

    return speeches, characters


# ──────────────────────────────────────────────────────────────────────────────
# Mention detection
# ──────────────────────────────────────────────────────────────────────────────

def detect_mentions(speaker: str,
                    speech_text: str,
                    line_count: int,
                    act: int,
                    scene: int,
                    alias_regex,
                    alias_map: Dict[str, str]) -> List[MentionRecord]:
    """
    Scan a speech for mentions of other characters.
    Returns one MentionRecord per unique target found.
    """
    found_targets: Dict[str, str] = {}   # target → alias that matched

    for m in alias_regex.finditer(speech_text):
        matched_alias = m.group(0).lower()
        target = alias_map.get(matched_alias)
        if target and target != speaker:
            if target not in found_targets:
                found_targets[target] = m.group(0)   # preserve original case

    records = []
    for target, alias in found_targets.items():
        records.append(MentionRecord(
            speaker=speaker,
            target=target,
            lines=line_count,
            act=act,
            scene=scene,
            alias_matched=alias,
        ))
    return records


# ──────────────────────────────────────────────────────────────────────────────
# Network builder
# ──────────────────────────────────────────────────────────────────────────────

def build_directed_network(mention_records: List[MentionRecord]) -> nx.DiGraph:
    """
    Build a weighted directed graph from mention records.

    Edge  SPEAKER → TARGET:
      weight    = total lines spoken by SPEAKER in speeches that mention TARGET
      mentions  = number of distinct speeches containing the mention
    Node attributes:
      total_lines_spoken  = all lines attributed to this character
      total_lines_received = total lines in which this character is mentioned
    """
    G = nx.DiGraph()

    # Accumulate edge weights
    edge_data: Dict[Tuple[str, str], Dict] = defaultdict(
        lambda: {"weight": 0, "mentions": 0, "scenes": set()}
    )
    node_lines_spoken: Dict[str, int] = defaultdict(int)
    node_lines_received: Dict[str, int] = defaultdict(int)

    for rec in mention_records:
        node_lines_spoken[rec.speaker] += rec.lines
        node_lines_received[rec.target] += rec.lines
        key = (rec.speaker, rec.target)
        edge_data[key]["weight"] += rec.lines
        edge_data[key]["mentions"] += 1
        edge_data[key]["scenes"].add((rec.act, rec.scene))

    # Add nodes
    all_chars = set(node_lines_spoken.keys()) | set(node_lines_received.keys())
    for char in all_chars:
        G.add_node(char,
                   total_lines_spoken=node_lines_spoken[char],
                   total_lines_received=node_lines_received[char])

    # Add edges
    for (src, tgt), attrs in edge_data.items():
        G.add_edge(src, tgt,
                   weight=attrs["weight"],
                   mentions=attrs["mentions"],
                   n_scenes=len(attrs["scenes"]))

    return G


# ──────────────────────────────────────────────────────────────────────────────
# Output helpers
# ──────────────────────────────────────────────────────────────────────────────

def print_summary(G: nx.DiGraph, title: str) -> None:
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")
    print(f"  Nodes (characters)  : {G.number_of_nodes()}")
    print(f"  Directed edges      : {G.number_of_edges()}")

    if G.number_of_edges() == 0:
        print("  (No mention edges found.)")
        return

    # Characters who mention others most (out-degree weighted)
    out_strengths = sorted(
        [(n, sum(d["weight"] for _, _, d in G.out_edges(n, data=True)))
         for n in G.nodes()],
        key=lambda x: x[1], reverse=True
    )[:10]
    print("\n  Top 10 characters by lines-in-speeches-that-mention-others:")
    for name, wt in out_strengths:
        print(f"    {name:<30} {wt:>5} lines  (out-degree {G.out_degree(name)})")

    # Most mentioned characters (in-degree weighted)
    in_strengths = sorted(
        [(n, sum(d["weight"] for _, _, d in G.in_edges(n, data=True)))
         for n in G.nodes()],
        key=lambda x: x[1], reverse=True
    )[:10]
    print("\n  Top 10 most-mentioned characters (weighted in-degree):")
    for name, wt in in_strengths:
        print(f"    {name:<30} {wt:>5} weighted lines  (in-degree {G.in_degree(name)})")

    # Strongest directed pairs
    top_edges = sorted(G.edges(data=True),
                       key=lambda x: x[2]["weight"], reverse=True)[:10]
    print("\n  Top 10 directed mention arcs (by weight):")
    for u, v, d in top_edges:
        print(f"    {u:<22} →  {v:<22}  weight={d['weight']:>5}  "
              f"mentions={d['mentions']:>3}")

    # Reciprocity
    reciprocal = sum(1 for u, v in G.edges()
                     if G.has_edge(v, u))
    print(f"\n  Reciprocal pairs     : {reciprocal // 2} "
          f"({100*reciprocal/max(G.number_of_edges(),1):.1f}% of edges)")


def export_graph(G: nx.DiGraph, slug: str) -> None:
    csv_path = f"{slug}_mention_edges.csv"
    gexf_path = f"{slug}_mention_network.gexf"

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("source,target,weight,mentions,scenes\n")
        for u, v, d in sorted(G.edges(data=True),
                               key=lambda x: x[2]["weight"], reverse=True):
            f.write(f"{u},{v},{d['weight']},{d['mentions']},{d['n_scenes']}\n")

    nx.write_gexf(G, gexf_path)
    print(f"\n  ✓ Edges CSV  → {csv_path}")
    print(f"  ✓ GEXF graph → {gexf_path}  (open with Gephi)")


def visualize_network(G: nx.DiGraph, title: str) -> None:
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
    except ImportError:
        print("  [WARN] matplotlib not installed – skipping visualisation.")
        return

    if G.number_of_nodes() == 0:
        print("  [WARN] Empty graph.")
        return

    fig, ax = plt.subplots(figsize=(18, 13))
    fig.patch.set_facecolor("#0d0d1a")
    ax.set_facecolor("#0d0d1a")

    # Keep only the top-N nodes by combined in+out weighted degree for clarity
    MAX_NODES = 30
    node_strength = {n: (G.in_degree(n, weight="weight") +
                         G.out_degree(n, weight="weight"))
                     for n in G.nodes()}
    top_nodes = sorted(node_strength, key=node_strength.get, reverse=True)[:MAX_NODES]
    sub = G.subgraph(top_nodes).copy()

    pos = nx.spring_layout(sub, weight="weight", k=3.0, seed=7, iterations=100)

    weights = [d["weight"] for _, _, d in sub.edges(data=True)]
    max_w = max(weights) if weights else 1

    # Draw curved edges with arrows
    nx.draw_networkx_edges(
        sub, pos, ax=ax,
        width=[0.4 + 4.0 * w / max_w for w in weights],
        edge_color=weights,
        edge_cmap=cm.YlOrRd,
        alpha=0.55,
        arrows=True,
        arrowsize=15,
        connectionstyle="arc3,rad=0.1",
        node_size=0,         # avoid clipping on nodes
    )

    in_str = [G.in_degree(n, weight="weight") for n in sub.nodes()]
    out_str = [G.out_degree(n, weight="weight") for n in sub.nodes()]
    node_sizes = [max(80, (ins + outs) * 2) for ins, outs in zip(in_str, out_str)]

    nc = nx.draw_networkx_nodes(
        sub, pos, ax=ax,
        node_size=node_sizes,
        node_color=[node_strength[n] for n in sub.nodes()],
        cmap=cm.cool,
        alpha=0.9,
    )

    nx.draw_networkx_labels(
        sub, pos, ax=ax,
        font_size=7, font_color="white", font_weight="bold",
    )

    plt.colorbar(nc, ax=ax, label="Combined weighted degree", shrink=0.55)
    ax.set_title(f"{title}\n(top {len(top_nodes)} characters by weighted degree)",
                 color="white", fontsize=13, pad=16)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


# ──────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ──────────────────────────────────────────────────────────────────────────────

def process_play(slug: str,
                 visualise: bool = False,
                 export: bool = False) -> nx.DiGraph:
    title = PLAYS.get(slug, slug)
    print(f"\n► Scraping «{title}» …")

    scene_urls = _scene_urls(slug)
    if not scene_urls:
        print(f"  [ERROR] No scenes found for '{slug}'.")
        return nx.DiGraph()

    print(f"  Found {len(scene_urls)} scenes.")

    # First pass: collect all character names across the entire play
    all_characters: Set[str] = set()
    scene_cache: Dict[Tuple[int, int], Tuple] = {}

    for act, scene_num, url in scene_urls:
        print(f"  Pass 1 – Act {act}, Scene {scene_num} …", end="\r", flush=True)
        speeches, chars = scrape_scene(slug, act, scene_num, url)
        all_characters.update(chars)
        scene_cache[(act, scene_num)] = (speeches, url)

    print(f"  {'':60}")  # clear line
    print(f"  Characters found: {len(all_characters)}")

    # Build alias map and compiled regex from full character list
    alias_map = build_alias_map(slug, all_characters)
    alias_regex = build_regex(alias_map)
    print(f"  Alias patterns  : {len(alias_map)}")

    # Second pass: detect mentions in each speech
    all_mentions: List[MentionRecord] = []

    for (act, scene_num), (speeches, url) in sorted(scene_cache.items()):
        print(f"  Pass 2 – Act {act}, Scene {scene_num} …  "
              f"({len(speeches)} speeches)", end="\r", flush=True)
        for speaker, text, n_lines in speeches:
            records = detect_mentions(
                speaker, text, n_lines, act, scene_num,
                alias_regex, alias_map
            )
            all_mentions.extend(records)

    print(f"  {'':60}")
    print(f"  Mention events  : {len(all_mentions)}")

    G = build_directed_network(all_mentions)
    print_summary(G, f"Directed Mention Network – {title}")

    if export:
        export_graph(G, slug)
    if visualise:
        visualize_network(G, f"Directed Mention Network\n{title}")

    return G


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def interactive_menu():
    print("\n╔═══════════════════════════════════════════════════╗")
    print("║  Shakespeare Directed Mention Network Builder     ║")
    print("╚═══════════════════════════════════════════════════╝")
    slugs = list(PLAYS.keys())
    for i, slug in enumerate(slugs):
        print(f"  [{i+1:2d}] {PLAYS[slug]}")

    print("\nEnter a number (or comma-separated), 'all', or 'q' to quit:")
    choice = input("  > ").strip().lower()
    if choice in ("q", "quit"):
        return

    viz = input("  Show visualisation? [y/N]: ").strip().lower() == "y"
    exp = input("  Export CSV + GEXF?  [y/N]: ").strip().lower() == "y"

    if choice == "all":
        selected = slugs
    else:
        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
        selected = [slugs[i] for i in indices if 0 <= i < len(slugs)]

    for slug in selected:
        process_play(slug, visualise=viz, export=exp)


def main():
    parser = argparse.ArgumentParser(
        description="Build Shakespeare directed character mention networks.")
    parser.add_argument("--play",   help="Play slug, e.g. hamlet")
    parser.add_argument("--all",    action="store_true")
    parser.add_argument("--viz",    action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--list",   action="store_true",
                        help="Show valid play slugs")
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
            print(f"Unknown slug '{slug}'. Use --list for valid options.")
            sys.exit(1)
        process_play(slug, visualise=args.viz, export=args.export)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
