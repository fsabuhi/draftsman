#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
"""Checks the spec in docs/ against the rules in docs/AGENTS.md.

    python3 scripts/check_spec.py             report every problem; exit 1 if there are any
    python3 scripts/check_spec.py --fix       also regenerate the feature index in docs/README.md
    python3 scripts/check_spec.py --root DIR  check another repository

Plain Python 3.9+. YAML data files need PyYAML (`uv run scripts/check_spec.py` installs it), and
TOML data files need Python 3.11+. Installed by draftsman: when it reports a problem, fix the docs,
never this file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
URL = re.compile(r"[a-z][a-z0-9+.-]*:", re.I)
# D- ids are the project's own decisions; P- ids are the platform's, in docs/platform/decisions.md.
DECISION = re.compile(r"\b[DP]-\d{3,}\b")
APP_DECISION = re.compile(r"\bD-\d{3,}\b")
STEP = re.compile(r"^- \[([ x])\] \*\*((\d+)\.\d+[a-z]?)\*\* (\S.*)$")
STEP_LIKE = re.compile(r"^\s*[-*+] \[[ xX]\]")
# "(after 2.1)", "(after 2.1, 2.3; D-004)" or "(…; after 2.1)": the ids that follow the word. A project's
# step may also wait for a step of the platform's build order, written "platform 2.1".
AFTER = re.compile(r"\bafter ((?:platform )?\d+\.\d+[a-z]?(?:(?:,| and|, and) (?:platform )?\d+\.\d+[a-z]?)*)")
AFTER_ITEM = re.compile(r"(platform )?(\d+\.\d+[a-z]?)\b")
AFTER_CLAUSE = re.compile(r"\bafter\b([^;)]*)", re.I)
TEAM = re.compile(r"[(;]\s*team\s*[;)]")
DONE_WHEN = re.compile(r"^\s+- Done when: \S")
ENDPOINT = re.compile(r"^\|\s*`((?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) /[^`]*)`\s*\|")
ERROR_MENTION = re.compile(r"`([a-z][a-z0-9_]*)` \(([1-5]\d\d)\)")
DATA_REF = re.compile(r"`([\w-]+\.(?:ya?ml|toml|json))\s*→\s*([^`]+?)\s*`")
FEATURE_FM = re.compile(r"\A---\nships_in: ([a-z0-9-]+)\ndecisions: \[([^\]\n]*)\]\n---\n")
OTHER_FM = re.compile(r"\A---\ndecisions: \[([^\]\n]*)\]\n---\n")
PLACEHOLDERS = [
    re.compile(r"\b(?:TBD|TBA|TODO|FIXME|XXX)\b|\?\?\?|<<fill"),
    re.compile(r"\betc\b|\band so on\b|\blorem ipsum\b|\bto be (?:decided|determined|confirmed)\b", re.I),
]
ACCEPTED = ["ID", "Date", "Status", "Decision", "Why", "Supersedes"]
OPEN = ["ID", "Date", "Status", "Question", "Recommendation", "Needed by"]
NEVER = ["We won't build", "Why", "Decision"]
REQUIRED = ["AGENTS.md", "docs/AGENTS.md", "docs/README.md", "docs/product.md",
            "docs/decisions.md", "docs/never.md", "docs/ideas.md"]
DATA_SUFFIXES = {".yaml", ".yml", ".toml", ".json"}
INDEX_START, INDEX_END = "<!-- features:start -->", "<!-- features:end -->"


def blank_fences(text: str) -> str:
    """The text with fenced code blocks blanked out, keeping line numbers."""
    out, fence = [], None
    for line in text.split("\n"):
        m = re.match(r"\s*(`{3,}|~{3,})", line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append("")
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def numbered(text: str) -> list[tuple[int, str]]:
    return list(enumerate(text.split("\n"), 1))


def lineno(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def sections(lines, level):
    """[(title, line, body)] for each heading of exactly `level`; a higher heading ends a section."""
    out, current = [], None
    for n, line in lines:
        m = HEADING.match(line)
        if m and len(m.group(1)) <= level:
            current = None
            if len(m.group(1)) == level:
                current = (m.group(2), n, [])
                out.append(current)
        elif current is not None:
            current[2].append((n, line))
    return out


def find_section(lines, level, title):
    return next((body for t, _, body in sections(lines, level) if t == title), None)


def cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def tables(lines):
    """Each table in `lines` as [(line, cells)]: the header row first, no separator row."""
    out, rows = [], None
    for n, line in lines:
        if line.lstrip().startswith("|"):
            if rows is None:
                rows = []
                out.append(rows)
            row = cells(line)
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in row):
                rows.append((n, row))
        else:
            rows = None
    return out


def table(lines):
    """The first table in `lines`, or []."""
    return next(iter(tables(lines)), [])


def slug(title: str) -> str:
    """GitHub's anchor for a heading."""
    return re.sub(r"[^\w\- ]", "", title.strip().lower()).replace(" ", "-")


def anchors(text: str) -> set[str]:
    seen, out = {}, set()
    for _, line in numbered(blank_fences(text)):
        m = HEADING.match(line)
        if m:
            base = slug(m.group(2))
            k = seen.get(base, 0)
            out.add(base if k == 0 else f"{base}-{k}")
            seen[base] = k + 1
    return out


def parse_data(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix == ".toml":
        try:
            import tomllib
        except ImportError:
            raise RuntimeError("TOML data files need Python 3.11 or newer") from None
        return tomllib.loads(text)
    try:
        import yaml
    except ImportError:
        raise RuntimeError(
            "YAML data files need PyYAML: run `uv run scripts/check_spec.py` or `pip install pyyaml`"
        ) from None
    return yaml.safe_load(text)


def has_key(node, dotted: str) -> bool:
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def spec_files(root: Path) -> list[Path]:
    """The files the rules cover: the agent guides and everything under docs/."""
    candidates = [root / "AGENTS.md", root / "CLAUDE.md", *sorted(root.glob("*/AGENTS.md")),
                  *sorted((root / "docs").rglob("*.md"))]
    skip = {"node_modules", "vendor", "docs-archive"}  # docs-archive holds a migration's originals
    return [f for f in dict.fromkeys(candidates) if f.is_file()
            and not any(p.startswith(".") or p in skip for p in f.relative_to(root).parts[:-1])]


def check(root: Path, fix: bool = False) -> tuple[list[str], str]:
    """Returns (problems, summary). Problems are `path:line: message`, sorted by place."""
    problems: list[tuple[str, int, str]] = []

    def err(path: Path, msg: str, line: int = 0) -> None:
        problems.append((str(path.relative_to(root)), line, msg))

    docs = root / "docs"
    for rel in REQUIRED:
        if not (root / rel).is_file():
            err(root / rel, "missing: every draftsman spec has this file")
    files = spec_files(root)
    texts = {f: f.read_text(encoding="utf-8") for f in files}
    prose = {f: blank_fences(t) for f, t in texts.items()}

    phases, steps, milestones, roadmap_text = check_product(docs / "product.md", prose, err)
    platform_order = docs / "platform" / "build-order.md"
    psteps, pmilestones = {}, {}
    if platform_order in prose:
        psteps, pmilestones = check_platform_order(platform_order, prose, err)
    check_platform_waits(docs / "product.md", steps, psteps, platform_order in prose, err)
    dec_path, platform_dec = docs / "decisions.md", docs / "platform" / "decisions.md"
    decisions, platform = {}, {}
    if dec_path in prose:
        decisions = parse_decisions(dec_path, numbered(prose[dec_path]), err, "D")
    if platform_dec in prose:
        platform = parse_decisions(platform_dec, numbered(prose[platform_dec]), err, "P")
    rows = {**decisions, **platform}
    check_decision_links(rows, phases, (steps, milestones), (psteps, pmilestones), err)
    check_step_decisions(rows, {"project": (steps, docs / "product.md"), "platform": (psteps, platform_order)}, err)

    fdir = docs / "features"
    features: dict[str, tuple[str, str | None]] = {}
    if fdir.is_dir():
        for sub in sorted(p for p in fdir.iterdir() if p.is_dir()):
            err(sub, "feature files sit directly in docs/features/, with no subfolders")
        for f in sorted(fdir.glob("*.md")):
            features[f.stem] = check_feature(f, texts[f], phases, roadmap_text, err)
    if not features:
        err(fdir, "the spec needs at least one feature file in docs/features/")

    registry_path, platform_errors = docs / "shared" / "errors.md", docs / "platform" / "errors.md"
    registry = parse_registry(registry_path, prose, err)
    platform_registry = parse_registry(platform_errors, prose, err)
    codes: dict[str, tuple[str, str]] = {}  # each code's status and the table it's in
    for path, reg in ((platform_errors, platform_registry), (registry_path, registry)):
        for code, (status, n) in (reg or {}).items():
            if code in codes:
                err(path, f"`{code}` is already in {codes[code][1]}: each code is in one table only", n)
            else:
                codes[code] = (status, path.relative_to(root).as_posix())
    code_tables = "docs/shared/errors.md" + (" or docs/platform/errors.md" if platform_registry is not None else "")
    app_codes = {c for c, (_, home) in codes.items() if home == "docs/shared/errors.md"}
    data = load_data_files(docs / "data", err)
    # A superseded row is history: the keys it names may have moved since.
    history = {(r["path"], r["line"]) for r in rows.values() if r["status"] == "superseded"}
    endpoint_home: dict[str, tuple[Path, int]] = {}
    anchor_cache: dict[Path, set[str]] = {}
    for f in files:
        p = prose[f]
        no_code = re.sub(r"`[^`\n]*`", "", p)
        for rx in PLACEHOLDERS:
            for m in rx.finditer(no_code):
                err(f, f"`{m.group(0)}` leaves a gap: write the answer, or record an open decision",
                    lineno(no_code, m.start()))
        for m in LINK.finditer(p):
            target = m.group(1)
            if URL.match(target):
                continue
            path_part, _, anchor = target.partition("#")
            dest = (f.parent / path_part).resolve() if path_part else f
            if not dest.exists():
                err(f, f"broken link {target}", lineno(p, m.start()))
            elif anchor and dest.suffix == ".md":
                if dest not in anchor_cache:
                    anchor_cache[dest] = anchors(dest.read_text(encoding="utf-8"))
                if anchor not in anchor_cache[dest]:
                    err(f, f"broken anchor {target}", lineno(p, m.start()))
        if f not in (dec_path, platform_dec):
            for m in DECISION.finditer(p):
                d, ln = m.group(0), lineno(p, m.start())
                if d.startswith("D-") and dec_path not in prose:
                    continue
                if d not in rows:
                    err(f, f"{d} isn't in {'docs/platform/' if d.startswith('P-') else ''}decisions.md", ln)
                elif rows[d]["status"] == "superseded":
                    err(f, f"{d} is superseded: cite the decision that replaced it", ln)
        if f.parent != fdir and texts[f].startswith("---\n") and not OTHER_FM.match(texts[f]):
            err(f, "frontmatter outside docs/features/ is exactly three lines: ---, decisions: [D-001], ---", 1)
        for n, line in numbered(p):
            m = ENDPOINT.match(line)
            if not m:
                continue
            key = " ".join(m.group(1).split())
            if key in endpoint_home:
                home, home_line = endpoint_home[key]
                err(f, f"`{key}` is already defined at {home.relative_to(root)}:{home_line}; "
                       "define each endpoint once and link to it", n)
            else:
                endpoint_home[key] = (f, n)
        if f not in (registry_path, platform_errors):
            for m in ERROR_MENTION.finditer(p):
                code, status, ln = m.group(1), m.group(2), lineno(p, m.start())
                if code in codes:
                    if codes[code][0] != status:
                        err(f, f"`{code}` is {codes[code][0]} in {codes[code][1]}, not {status}", ln)
                elif registry is None:
                    err(f, f"`{code}` ({status}) is an error code, so it needs a row in docs/shared/errors.md", ln)
                else:
                    err(f, f"error code `{code}` isn't in {code_tables}", ln)
        if docs / "platform" in f.parents:
            check_platform_file(f, p, docs, f == platform_dec, app_codes, err)
        for m in DATA_REF.finditer(p):
            name, ln = m.group(1), lineno(p, m.start())
            if (f, ln) in history:
                continue
            key = m.group(2).split("<")[0].split("*")[0].strip().rstrip(".")
            if name not in data:
                err(f, f"docs/data/{name} doesn't exist", ln)
            elif data[name] is not None and key and not has_key(data[name], key):
                err(f, f"docs/data/{name} has no key `{key}`", ln)

    check_never(docs / "never.md", prose, err)
    agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
    if agents in texts and "docs/AGENTS.md" not in texts[agents]:
        err(agents, "must link to docs/AGENTS.md, so every agent finds the docs rules")
    if claude in texts and "@AGENTS.md" not in texts[claude]:
        err(claude, "must import the shared guide with an `@AGENTS.md` line, so Claude Code follows the same rules")
    check_index(docs / "README.md", texts, features, phases, fix, err)

    problems.sort(key=lambda p: (p[0], p[1]))
    lines = [f"{path}:{line}: {msg}" if line else f"{path}: {msg}" for path, line, msg in problems]
    n_open = sum(1 for d in decisions.values() if d["status"] == "open")
    n_ticked = sum(1 for s in steps.values() if s["ticked"])
    n_platform = ""
    if platform_dec in prose:
        p_open = sum(1 for d in platform.values() if d["status"] == "open")
        n_platform = f"{len(platform)} platform decisions ({p_open} open), "
    n_psteps = ""
    if platform_order in prose:
        p_ticked = sum(1 for s in psteps.values() if s["ticked"])
        n_psteps = f", {len(psteps)} platform steps ({p_ticked} ticked)"
    summary = (f"Spec OK: {len(features)} features, {len(decisions)} decisions ({n_open} open), {n_platform}"
               f"{len(steps)} steps ({n_ticked} ticked){n_psteps}.")
    return lines, summary


def check_product(path, prose, err):
    phases, steps, milestones, roadmap_text = [], {}, {}, ""
    if path not in prose:
        return phases, steps, milestones, roadmap_text
    lines = numbered(prose[path])
    top = [t for t, _, _ in sections(lines, 2)]
    for need in ("Vision", "Roadmap"):
        if need not in top:
            err(path, f"needs a `## {need}` section")
    roadmap = find_section(lines, 2, "Roadmap") or []
    roadmap_text = "\n".join(line for _, line in roadmap)
    pg = find_section(roadmap, 3, "Phases and gates")
    if pg is None:
        err(path, "the roadmap needs a `### Phases and gates` table")
    else:
        for n, row in table(pg)[1:]:
            m = re.fullmatch(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", row[0]) if row else None
            if m:
                phases.append(m.group(1))
            else:
                err(path, "each phase is a backticked slug in the first column, like `mvp`", n)
        if not phases:
            err(path, "the phases table lists no phases")
    bo = find_section(roadmap, 3, "Build order")
    if bo is None:
        err(path, "the roadmap needs a `### Build order`")
    else:
        steps, milestones = parse_build_order(bo, path, err)
    return phases, steps, milestones, roadmap_text


def check_platform_order(path, prose, err):
    """The platform's build order: the template's own milestones, headed `## <n>. <name>`."""
    lines = numbered(prose[path])
    if not any(re.fullmatch(r"# Build order\s*", line) for _, line in lines):
        err(path, "the platform's build order starts with a `# Build order` heading, then holds only its milestones")
    steps, milestones = parse_build_order(lines, path, err, level=2, label="the platform's build order")
    if not milestones:
        err(path, "the platform's build order needs at least one milestone, headed `## 1. <name>`")
    for sid, s in steps.items():
        if s["platform_after"]:
            err(path, f"step {sid} is a platform step, so its (after …) names other platform steps by number alone, "
                      f"as in (after {s['platform_after'][0]})", s["line"])
    return steps, milestones


def check_platform_waits(path, steps, psteps, has_order, err):
    """A project's step that waits for a platform step names one that exists, and isn't ticked before it."""
    for sid, s in steps.items():
        for ref in s["platform_after"]:
            if not has_order:
                err(path, f"step {sid} comes after platform step {ref}, but there's no docs/platform/build-order.md",
                    s["line"])
            elif ref not in psteps:
                err(path, f"step {sid} comes after platform step {ref}, which isn't in docs/platform/build-order.md",
                    s["line"])
            elif s["ticked"] and not psteps[ref]["ticked"]:
                err(path, f"step {sid} is ticked, but platform step {ref}, which it comes after, isn't ticked in "
                          "docs/platform/build-order.md", s["line"])


def parse_build_order(lines, path, err, level=4, label="the build order"):
    steps, milestones, expected = {}, {}, 1
    for title, n, body in sections(lines, level):
        m = re.match(r"(\d+)\. \S", title)
        if not m:
            err(path, f"a milestone is headed `{'#' * level} <n>. <name>`", n)
            continue
        num = int(m.group(1))
        if num != expected:
            err(path, f"milestone {num} should be numbered {expected}", n)
        expected = num + 1
        milestones[num] = []
        if not any("Done when" in line for _, line in body
                   if not line.startswith((" ", "\t")) and not STEP.match(line)):
            err(path, f"milestone {num} needs a `Done when …` line saying what a person can do once it's built", n)
        current = None
        for ln, line in body:
            s = STEP.match(line)
            if s:
                sid, major = s.group(2), int(s.group(3))
                if sid in steps:
                    err(path, f"step {sid} is defined twice", ln)
                if major != num:
                    err(path, f"step {sid} sits in milestone {num}, so its id starts with {num}.", ln)
                text = s.group(4)
                after = [i for g in AFTER.findall(text) for i in AFTER_ITEM.findall(g)]
                loose = sum(len(re.findall(r"\bplatform\b", c, re.I)) for c in AFTER_CLAUSE.findall(text))
                if loose > sum(1 for plat, _ in after if plat):
                    err(path, f"step {sid}: in (after …), each platform step is written `platform 2.1`, "
                              "one `platform` per id", ln)
                current = steps[sid] = {"ticked": s.group(1) == "x", "line": ln, "text": text,
                                        "done_when": False, "milestone": num, "team": bool(TEAM.search(text)),
                                        "decisions": DECISION.findall(text),
                                        "after": [ref for plat, ref in after if not plat],
                                        "platform_after": [ref for plat, ref in after if plat]}
                milestones[num].append(sid)
            elif STEP_LIKE.match(line):
                err(path, "a step is written `- [ ] **<id>** <what it builds>`", ln)
                current = None
            elif current and line[:1] in (" ", "\t"):
                if DONE_WHEN.match(line):
                    current["done_when"] = True
            elif line.strip():
                current = None
    for sid, s in steps.items():
        if not s["ticked"] and not s["done_when"]:
            err(path, f"step {sid} needs an indented `- Done when: …` line that a test or a command can prove",
                s["line"])
        for ref in s["after"]:
            if ref == sid or ref not in steps:
                err(path, f"step {sid} comes after step {ref}, which isn't another step in {label}",
                    s["line"])
    for num, ids in milestones.items():
        confirm = [sid for sid in ids if steps[sid]["team"]
                   and re.match(rf"Confirm milestone {num}['’]s done-when", steps[sid]["text"])]
        if not confirm:
            line = next((n for t, n, _ in sections(lines, level) if t.startswith(f"{num}. ")), 0)
            err(path, f"milestone {num} needs a `Confirm milestone {num}'s done-when (team)` step, "
                      "so agents know when the next milestone may start", line)
        elif steps[confirm[0]]["ticked"]:
            for sid in ids:
                if not steps[sid]["ticked"]:
                    err(path, f"milestone {num} is confirmed, but step {sid} isn't ticked", steps[sid]["line"])
    return steps, milestones


def parse_decisions(path, lines, err, prefix):
    """docs/decisions.md holds D- rows; docs/platform/decisions.md holds P- rows in the same two tables."""
    rows = {}
    if prefix == "P" and find_section(lines, 2, "Accepted and proposed") is None:
        found = [t for t in tables(lines) if t]
        if found and found[0][0][1] == ACCEPTED:
            # Before Draftsman 0.5.0 the file held one table; the template's update brings the two.
            err(path, "holds the two tables of docs/decisions.md, under `## Accepted and proposed` and `## Open`, "
                      "since Draftsman 0.5.0: the template's update brings them", found[0][0][0])
            parse_rows(path, found[0][1:], ACCEPTED, prefix, {"accepted", "proposed", "superseded"},
                       "the Accepted and proposed table", rows, err)
            return rows
    layout = (("Accepted and proposed", ACCEPTED, {"accepted", "proposed", "superseded"}),
              ("Open", OPEN, {"open"}))
    for title, header, statuses in layout:
        body = find_section(lines, 2, title)
        if body is None:
            err(path, f"needs a `## {title}` section with its table")
            continue
        t = table(body)
        if not t or t[0][1] != header:
            err(path, f"the {title} table's header is | {' | '.join(header)} |", t[0][0] if t else 0)
            continue
        parse_rows(path, t[1:], header, prefix, statuses, f"the {title} table", rows, err)
    return rows


def parse_rows(path, body, header, prefix, statuses, where, rows, err):
    """Adds each decision row in `body` to `rows`; `where` names the table in problems."""
    open_table = header == OPEN
    for n, c in body:
        if len(c) != 6:
            err(path, f"a decision row has 6 cells; this one has {len(c)}", n)
            continue
        did, date, status = c[0], c[1], c[2]
        if not re.fullmatch(rf"{prefix}-\d{{3,}}", did):
            err(path, f"`{did}` isn't a decision id like {prefix}-012", n)
            continue
        if did in rows:
            err(path, f"{did} is defined twice", n)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            err(path, f"{did}: the date is written YYYY-MM-DD", n)
        if status not in statuses:
            err(path, f"{did}: `{status}` doesn't belong in {where} (it holds {', '.join(sorted(statuses))})", n)
        empty = [header[i] for i in (3, 4) if not c[i]]
        if open_table and not c[5]:
            empty.append("Needed by")
        if empty:
            err(path, f"{did}: fill in {' and '.join(empty)}", n)
        rows[did] = {"status": status, "line": n, "cells": c, "open_table": open_table, "path": path}


def check_decision_links(rows, phases, project, platform, err):
    """`project` and `platform` are each build order's (steps, milestones): an open D- row blocks the
    project's steps, milestones or phases, and an open P- row the platform's steps or milestones."""
    named = set()
    for did, r in rows.items():
        if r["open_table"]:
            continue
        path = r["path"]
        for old in DECISION.findall(r["cells"][5]):
            named.add(old)
            if did.startswith("D-") and old.startswith("P-"):
                err(path, f"{did} can't supersede {old}: a project's own decision never replaces a platform decision",
                    r["line"])
            elif old not in rows:
                # A P- row may name the D- rows of the project the platform came from.
                if not (did.startswith("P-") and old.startswith("D-")):
                    err(path, f"{did} supersedes {old}, which doesn't exist", r["line"])
            elif rows[old]["status"] != "superseded":
                err(path, f"{did} supersedes {old}, so mark {old} `superseded`", r["line"])
    for did, r in rows.items():
        path = r["path"]
        if r["status"] == "superseded" and did not in named:
            err(path, f"{did} is superseded, but no row names it under Supersedes", r["line"])
        if r["status"] != "open":
            continue
        need = r["cells"][5]
        is_platform = did.startswith("P-")
        steps, milestones = platform if is_platform else project
        order = "docs/platform/build-order.md" if is_platform else "the build order"
        kind = "platform step" if is_platform else "step"
        named_steps = re.findall(r"\bstep\s+(\d+\.\d+[a-z]?)", need, re.I)
        named_milestones = [int(x) for x in re.findall(r"\bmilestone\s+(\d+)", need, re.I)]
        named_phases = [] if is_platform else [p for p in phases if f"`{p}`" in need]
        r["holds"] = (set(named_steps), set(named_milestones), named_phases)
        if not (named_steps or named_milestones or named_phases):
            if is_platform:
                err(path, f"{did}: Needed by names what it blocks: a step (Step 2.3) or a milestone (Milestone 4) "
                          "of docs/platform/build-order.md", r["line"])
            else:
                examples = ", ".join(f"`{p}`" for p in phases) or "from the roadmap"
                err(path, f"{did}: Needed by names what it blocks: a step (Step 2.3), "
                          f"a milestone (Milestone 4) or a phase ({examples})", r["line"])
        if is_platform and (named_steps or named_milestones) and not steps and not milestones:
            err(path, f"{did} is needed by the platform's build order, but there's no docs/platform/build-order.md",
                r["line"])
            continue
        for s in named_steps:
            if s not in steps:
                err(path, f"{did} is needed by {kind} {s}, which isn't in {order}", r["line"])
            elif steps[s]["ticked"]:
                err(path, f"{kind} {s} is ticked, but {did}, which it needs, is still open", r["line"])
        for m in named_milestones:
            if m not in milestones:
                err(path, f"{did} is needed by milestone {m}, which isn't in {order}", r["line"])
            elif milestones[m] and all(steps[s]["ticked"] for s in milestones[m]):
                err(path, f"{'platform ' if is_platform else ''}milestone {m} is done, but {did}, which it needs, "
                          "is still open", r["line"])


def check_step_decisions(rows, orders, err):
    """An agent's step that names an open decision must wait for it, and one that names a proposed
    decision can't start: a recommendation doesn't authorize building it. Team steps may be the
    work that answers a decision, so they're left out. `orders` maps "project" and "platform" to
    each build order's (steps, path). An open D- row holds the project's steps, and an open P- row
    the platform's; a project step waits for a P- row through the platform step it holds."""
    def held(kind, sid, did, seen):
        steps = orders[kind][0]
        if (kind, sid) in seen or sid not in steps:
            return False
        seen.add((kind, sid))
        if kind == "platform" and steps[sid]["ticked"]:
            # A shipped platform step holds nothing back, so a project step can't wait through it.
            return False
        named_steps, named_milestones, named_phases = rows[did]["holds"]
        if kind == ("platform" if did.startswith("P-") else "project") and (
                named_phases or sid in named_steps or steps[sid]["milestone"] in named_milestones):
            return True
        nexts = [(kind, a) for a in steps[sid]["after"]] + [("platform", a) for a in steps[sid]["platform_after"]]
        return any(held(k, a, did, seen) for k, a in nexts)

    for kind, (steps, path) in orders.items():
        for sid, s in steps.items():
            if s["ticked"] or s["team"]:
                continue
            for did in dict.fromkeys(s["decisions"]):
                if kind == "platform" and did.startswith("D-"):
                    continue  # the platform cites no D- id, which the folder's own check reports
                status = rows.get(did, {}).get("status")
                if status == "proposed" and kind == "project" and did.startswith("P-"):
                    err(path, f"step {sid} names {did}, which is only proposed: nothing builds on it until the "
                              "template's team accepts it", s["line"])
                elif status == "proposed":
                    err(path, f"step {sid} names {did}, which is only proposed: the team accepts it first, "
                              "or it becomes an open row that names this step under Needed by", s["line"])
                elif status == "open" and "holds" in rows[did] and not held(kind, sid, did, set()):
                    if kind == "project" and did.startswith("P-"):
                        err(path, f"step {sid} names {did}, an open platform decision: make it wait "
                                  f"(after platform …) for an unticked platform step that {did} holds", s["line"])
                    else:
                        err(path, f"step {sid} names {did}, which is open but doesn't hold the step back: name the "
                                  f"step under {did}'s Needed by, or make it wait (after …) for a step that does",
                            s["line"])


def check_feature(path, text, phases, roadmap_text, err):
    title = path.stem
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.stem):
        err(path, "a feature file is named with a lowercase-kebab-case slug")
    fm = FEATURE_FM.match(text)
    if not fm:
        err(path, "starts with exactly four lines: ---, ships_in: <phase>, decisions: [D-001, D-002], ---", 1)
        return title, None
    phase = fm.group(1)
    if phases and phase not in phases:
        err(path, f"ships_in `{phase}` isn't a phase in the roadmap ({', '.join(phases)})", 2)
    for d in filter(None, (x.strip() for x in fm.group(2).split(","))):
        if not DECISION.fullmatch(d):
            err(path, f"`{d}` in the frontmatter isn't a decision id like D-012", 3)
    lines = numbered(blank_fences(text))
    h1 = [line for _, line in lines if re.match(r"# \S", line)]
    if len(h1) != 1:
        err(path, "needs exactly one `# Title` heading")
    else:
        title = h1[0][2:].strip()
    h2 = [t for t, _, _ in sections(lines, 2)]
    if h2 not in (["Behavior"], ["Behavior", "Implementation"]):
        err(path, f"its sections are `## Behavior` then `## Implementation`, and no others "
                  f"(found: {', '.join(h2) or 'none'})")
    done = find_section(find_section(lines, 2, "Behavior") or [], 3, "Done when")
    if done is None or not any(re.match(r"[-*] \S", line) for _, line in done):
        err(path, "Behavior needs a `### Done when` list")
    impl = find_section(lines, 2, "Implementation")
    if phases and phase == phases[0] and not (impl and any(line.strip() for _, line in impl)):
        err(path, f"features in `{phases[0]}` need an `## Implementation` section")
    if f"features/{path.stem}.md" not in roadmap_text:
        err(path, "isn't linked from the roadmap in docs/product.md")
    return title, phase


def parse_registry(path, prose, err):
    """The error codes in an errors.md, as {code: (status, line)}, or None when the file doesn't exist."""
    if path not in prose:
        return None
    t = table(numbered(prose[path]))
    if not t or t[0][1][:2] != ["Code", "Status"]:
        err(path, "holds one table whose header starts | Code | Status |")
        return {}
    registry = {}
    for n, row in t[1:]:
        m = re.fullmatch(r"`([a-z][a-z0-9_]*)`", row[0]) if row else None
        if not m or len(row) < 3 or not all(row):
            err(path, "each row is | `code` | status | meaning | …, with every cell filled in", n)
            continue
        if m.group(1) in registry:
            err(path, f"`{m.group(1)}` is defined twice", n)
        registry[m.group(1)] = (row[1], n)
    return registry


def check_platform_file(path, text, docs, is_decisions, app_codes, err):
    """docs/platform/ is the same in every project built from the template, so it names nothing of one project's."""
    platform, data = (docs / "platform").resolve(), (docs / "data").resolve()
    for n, line in numbered(text):
        if is_decisions and line.lstrip().startswith("|") and cells(line)[2:3] != ["open"]:
            line = "|".join(cells(line)[:5])  # a Supersedes cell may name the D- rows a platform row replaced
        for m in APP_DECISION.finditer(line):
            err(path, f"{m.group(0)} is this project's own decision: docs/platform/ is the same in every project, "
                      "so it cites only P- ids", n)
    for m in ERROR_MENTION.finditer(text):
        if m.group(1) in app_codes:
            err(path, f"`{m.group(1)}` is this project's own error code: docs/platform/ is the same in every "
                      "project, so it names only the codes in docs/platform/errors.md", lineno(text, m.start()))
    for m in LINK.finditer(text):
        target = m.group(1)
        path_part = target.partition("#")[0]
        if URL.match(target) or not path_part:
            continue
        dest = (path.parent / path_part).resolve()
        if not (dest == platform or platform in dest.parents or data in dest.parents):
            err(path, f"{target} is outside docs/platform/: the folder is the same in every project, "
                      "so it links only inside itself and to docs/data/", lineno(text, m.start()))


def load_data_files(ddir, err):
    data = {}
    if not ddir.is_dir():
        return data
    for f in sorted(ddir.iterdir()):
        if f.name.startswith("."):
            continue
        if f.suffix not in DATA_SUFFIXES or not f.is_file():
            err(f, "docs/data/ holds only .yaml, .yml, .toml and .json files")
            continue
        try:
            data[f.name] = parse_data(f)
        except Exception as e:  # any parse failure is a problem with this file, reported once
            data[f.name] = None
            err(f, f"can't be read: {e}")
    return data


def check_never(path, prose, err):
    if path not in prose:
        return
    t = table(numbered(prose[path]))
    if not t:
        return
    if t[0][1] != NEVER:
        err(path, f"the table's header is | {' | '.join(NEVER)} |", t[0][0])
        return
    for n, row in t[1:]:
        if len(row) != 3 or not all(row) or not DECISION.search(row[2]):
            err(path, "each refusal says why and cites the decision behind it", n)


def check_index(path, texts, features, phases, fix, err):
    if path not in texts:
        return
    order = {p: i for i, p in enumerate(phases)}
    rows = sorted(features.items(), key=lambda kv: (order.get(kv[1][1], len(order)), kv[1][0].lower()))
    index = "\n".join(["| Feature | Ships in |", "| --- | --- |"]
                      + [f"| [{title}](features/{slug}.md) | {phase or 'unknown'} |"
                         for slug, (title, phase) in rows])
    generated = f"{INDEX_START}\n{index}\n{INDEX_END}"
    current = re.search(re.escape(INDEX_START) + ".*?" + re.escape(INDEX_END), texts[path], re.S)
    if not current:
        err(path, f"needs the feature index markers {INDEX_START} and {INDEX_END}")
    elif current.group(0) != generated:
        if fix:
            path.write_text(texts[path].replace(current.group(0), generated), encoding="utf-8")
            print("Regenerated the feature index in docs/README.md")
        else:
            err(path, "the feature index is out of date: run with --fix")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check the spec in docs/ against docs/AGENTS.md.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="the repository to check (default: the one this script is in)")
    parser.add_argument("--fix", action="store_true", help="regenerate the feature index in docs/README.md")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"{root} isn't a directory", file=sys.stderr)
        return 2
    problems, summary = check(root, args.fix)
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s). The rules are in docs/AGENTS.md.")
        return 1
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
