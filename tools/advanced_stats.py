"""The All Stats groups (data/advanced_stats.tsv): the rows in display order, the group headings and the
own rows' texts that tools/statbook.py writes into the book. Copied from the D2R-XL 2012 tools by its
tools/export_statbook.py; edit them there.

data/advanced_stats.tsv, one row per All Stats row in display order inside its group:
  stat    itemstatcost row name; several joined by "," for a row of several stats
  show    always / nonzero
  group   one of GROUPS
  row     empty = D2R's own row text (the item tooltip line); else the plugin's own row:
          range:<Key>  min and max stat     value:<Key>  one percent stat based on 100
          avoid        passive_dodge, passive_avoid, passive_evade
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "data" / "advanced_stats.tsv"


# from tools/advanced_stats.py

GROUPS = {
    "offense": ("AdvStatsGroupOffense", "Offense"),
    "spell": ("AdvStatsGroupSpell", "Spell Damage"),
    "defense": ("AdvStatsGroupDefense", "Defense"),
    "resist": ("AdvStatsGroupResist", "Resistances"),
    "speed": ("AdvStatsGroupSpeed", "Speed"),
    "lifemana": ("AdvStatsGroupLifeMana", "Life & Mana"),
    "attributes": ("AdvStatsGroupAttributes", "Attributes"),
    "skills": ("AdvStatsGroupSkills", "Skills"),
    "summons": ("AdvStatsGroupSummons", "Summons"),
    "other": ("AdvStatsGroupOther", "Other"),
}

TEXTS = {
    "AdvStatsAddsFire": "Adds %d-%d Fire Damage",
    "AdvStatsAddsLightning": "Adds %d-%d Lightning Damage",
    "AdvStatsAddsCold": "Adds %d-%d Cold Damage",
    "AdvStatsAddsMagic": "Adds %d-%d Magic Damage",
    "AdvStatsSkillAttackSpeed": "%+d%% Attack Speed from Skills",
    "AdvStatsSkillMoveSpeed": "%+d%% Movement Speed from Skills",
}

AVOID_STATS = ["passive_dodge", "passive_avoid", "passive_evade"]

KINDS = {"": ("Stat", 1), "range": ("Range", 2), "value": ("Value", 1), "avoid": ("Avoid", 3)}


def read_rows(path: Path = TSV) -> list[dict]:
    """The rows in display order (GROUPS order, file order inside a group), checked."""
    lines = [line.split("\t") for line in path.read_text("utf-8").splitlines() if line.strip()]
    h = lines[0]
    rows, seen = [], set()
    for n, r in enumerate(lines[1:], 2):
        d = dict(zip(h, r))
        stats = d["stat"].split(",")
        kind, _, key = d.get("row", "").partition(":")
        where = f"{path.name}:{n} {d['stat']}"
        if d["group"] not in GROUPS:
            raise ValueError(f"{where}: group {d['group']!r} is not one of {list(GROUPS)}")
        if kind not in KINDS:
            raise ValueError(f"{where}: row {d['row']!r}: kind must be empty, range:<Key>, value:<Key> or avoid")
        if len(stats) != KINDS[kind][1]:
            raise ValueError(f"{where}: a {kind or 'stat'} row has {KINDS[kind][1]} stat(s)")
        if kind in ("range", "value") and key not in TEXTS:
            raise ValueError(f"{where}: text key {key!r} is not in TEXTS")
        if kind == "avoid" and stats != AVOID_STATS:
            raise ValueError(f"{where}: an avoid row lists {','.join(AVOID_STATS)}")
        if d["show"] not in ("always", "nonzero"):
            raise ValueError(f"{where}: show must be always or nonzero")
        for s in stats:
            if s in seen:
                raise ValueError(f"{where}: {s} listed twice")
            seen.add(s)
        rows.append({"stats": stats, "always": d["show"] == "always", "group": d["group"], "kind": kind, "key": key})
    order = list(GROUPS)
    return sorted(rows, key=lambda r: order.index(r["group"]))
