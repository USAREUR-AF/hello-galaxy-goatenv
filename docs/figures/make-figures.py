#!/usr/bin/env python3
"""Draw the repository's figures from the tree.

    python3 -I docs/figures/make-figures.py           # write docs/figures/*.svg
    python3 -I docs/figures/make-figures.py --check   # exit 1 if a committed figure is out of date

Each figure is written twice, `<name>-light.svg` and `<name>-dark.svg`, for a
`<picture>` element. Every name and value in a figure is read from the tree:
each step's `goatbuilder.yaml`, its checkpoint under `checkpoints/`, and the
step table in README.md. The output is deterministic. Standard library only.
"""

import os
import re
import sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

THEMES = {
    "light": {
        "paper": "#ffffff", "panel": "#f6f8fa", "ink": "#1f2328", "quiet": "#59636e", "rule": "#d1d9e0",
        "line": "#818b98", "accent": "#0969da", "accent_soft": "#ddf4ff", "on_accent": "#ffffff",
        "good": "#1a7f37", "good_bg": "#dafbe1", "crit": "#cf222e", "crit_bg": "#ffebe9", "mute": "#6e7781",
        "s0": "#0969da", "s1": "#bc4c00", "s2": "#1a7f37", "s3": "#8250df",
    },
    "dark": {
        "paper": "#0d1117", "panel": "#161b22", "ink": "#e6edf3", "quiet": "#9198a1", "rule": "#3d444d",
        "line": "#7d8590", "accent": "#4493f8", "accent_soft": "#132c4c", "on_accent": "#0d1117",
        "good": "#3fb950", "good_bg": "#12261e", "crit": "#f85149", "crit_bg": "#2f1517", "mute": "#8b949e",
        "s0": "#4493f8", "s1": "#f0883e", "s2": "#3fb950", "s3": "#bc8cff",
    },
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def n(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def tw(s, size, mono=False, bold=False):
    """Text width estimate; the browser check in the README confirms it."""
    if mono:
        return len(s) * size * 0.62
    w = 0.0
    for c in s:
        if c in "il.,:;|!'`·1 ":
            w += 0.30
        elif c in "ft()[]/-":
            w += 0.36
        elif c in "mwMW@%":
            w += 0.86
        elif c.isupper() or c in "0123456789≤≥²→":
            w += 0.64
        else:
            w += 0.55
    return w * size * (1.06 if bold else 1.0)


def wrap(s, width, size, mono=False, bold=False):
    out, line = [], ""
    for word in s.split(" "):
        t = word if not line else line + " " + word
        if tw(t, size, mono, bold) <= width or not line:
            line = t
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


class SVG:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.items = []

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="panel", stroke="rule", rx=8, sw=1, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="{%s}" stroke="{%s}" stroke-width="%s"%s/>'
                 % (n(x), n(y), n(w), n(h), n(rx), fill, stroke, n(sw), d))

    def text(self, x, y, s, size=14, fill="ink", anchor="start", bold=False, mono=False, italic=False):
        self.add('<text x="%s" y="%s" font-size="%s" fill="{%s}" text-anchor="%s"%s%s%s>%s</text>'
                 % (n(x), n(y), n(size), fill, anchor, ' font-weight="600"' if bold else "",
                    ' font-family="%s"' % MONO if mono else "", ' font-style="italic"' if italic else "", escape(s)))

    def lines(self, x, y, rows, size=14, lead=1.4, **kw):
        for i, r in enumerate(rows):
            self.text(x, y + i * size * lead, r, size, **kw)
        return y + len(rows) * size * lead

    def line(self, x1, y1, x2, y2, stroke="line", sw=1.5, dash=None, arrow=False):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="{%s}" stroke-width="%s"%s%s/>'
                 % (n(x1), n(y1), n(x2), n(y2), stroke, n(sw), d, m))

    def path(self, d, stroke="line", fill="none", sw=1.5, dash=None, arrow=False):
        dd = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        f = "none" if fill == "none" else "{%s}" % fill
        self.add('<path d="%s" fill="%s" stroke="{%s}" stroke-width="%s"%s%s/>' % (d, f, stroke, n(sw), dd, m))

    def circle(self, x, y, r, fill="ink", stroke=None, sw=1.5):
        s = ' stroke="{%s}" stroke-width="%s"' % (stroke, n(sw)) if stroke else ""
        f = "none" if fill == "none" else "{%s}" % fill
        self.add('<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (n(x), n(y), n(r), f, s))

    def ellipse(self, x, y, rx, ry, fill="none", stroke="line", sw=1.5, dash=None, opacity=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        f = "none" if fill == "none" else "{%s}" % fill
        o = ' fill-opacity="%s"' % opacity if opacity is not None else ""
        self.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s stroke="{%s}" stroke-width="%s"%s/>'
                 % (n(x), n(y), n(rx), n(ry), f, o, stroke, n(sw), d))

    def render(self, theme):
        t = THEMES[theme]
        body = "\n".join(self.items)
        for k, v in t.items():
            body = body.replace("{%s}" % k, v)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
                'aria-labelledby="t d" font-family="%s">\n<title id="t">%s</title>\n<desc id="d">%s</desc>\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                'orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="%s"/></marker></defs>\n'
                '<rect width="100%%" height="100%%" rx="12" fill="%s"/>\n%s\n</svg>\n'
                % (self.w, self.h, self.w, self.h, SANS.replace("'", "&apos;"), escape(self.title), escape(self.desc),
                   t["line"], t["paper"], body))


def header(f, title, sub):
    """Title and subtitle at the top left."""
    f.text(24, 38, title, 20, bold=True)
    f.text(24, 62, sub, 14, fill="quiet")



# ---------------------------------------------------------------- tree facts
def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def steps_from_readme():
    """(number, title, directory, checkpoint) for each row of the README's step table."""
    out = []
    for line in read("README.md").splitlines():
        m = re.match(r"^\| (\d+)\. ([^|]+?) \| [^|]+ \| `([\w-]+)/`, `(checkpoints/[\w.-]+)` \|$", line)
        if m:
            out.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    if len(out) < 2:
        sys.exit("make-figures: the step table in README.md was not found")
    return out


def declared_sites(step_dir):
    """Sites from a step's goatbuilder.yaml: [(name, role, [classes])], plus its peerings' `with:` names."""
    sites, peerings, components, cur, in_classes, section = [], [], [], None, False, None
    for line in read(step_dir, "goatbuilder.yaml").splitlines():
        if re.match(r"^\w", line):
            section = line.split(":")[0]
        m = re.match(r"^      - name: (\S+)", line)
        if section == "environments" and m:
            cur = [m.group(1), "", []]
            sites.append(cur)
            in_classes = False
            continue
        if cur is not None and section == "environments":
            r = re.match(r"^        role: (\S+)", line)
            if r:
                cur[1] = r.group(1)
            if re.match(r"^        classes:", line):
                in_classes = True
                continue
            c = re.match(r"^          (\w+):", line)
            if in_classes and c:
                cur[2].append(c.group(1))
            elif in_classes and re.match(r"^        \w", line):
                in_classes = False
        k = re.match(r"^  ([\w-]+):", line)
        if section == "components" and k:
            components.append(k.group(1))
        p = re.match(r"^  - with: (\S+)", line)
        if section == "peerings" and p:
            peerings.append([p.group(1), ""])
        ps = re.match(r"^    (site|edge_class): (\S+)", line)
        if section == "peerings" and ps and peerings:
            peerings[-1][1] = (peerings[-1][1] + " " + ps.group(2)).strip()
    return [tuple(s) for s in sites], peerings, components


def checkpoint(path):
    text = read(path)
    st = re.search(r"^Status: (\S+)\s*\n\s*\n(\d+) components? on (\d+) machines?\. (\d+) of (\d+) converged", text, re.M)
    if st:
        env, comps, nmach, ok, total = st.groups()
        table = text[st.end():].split("COMPONENT", 1)[1].split("\n\n", 1)[0]
        machines = []
        for row in table.splitlines()[1:]:
            cols = row.split()
            if len(cols) != 5 or cols[0].endswith(":"):
                break
            if cols[1] not in machines:
                machines.append(cols[1])
        if len(machines) != int(nmach):
            sys.exit("make-figures: %s lists %d machines, says %s" % (path, len(machines), nmach))
        return {"env": env, "components": int(comps), "machines": machines, "ok": int(ok), "total": int(total)}
    pl = re.search(r"^Plan: (.+)$", text, re.M)
    if pl:
        phases = re.findall(r"^(\d+)\s+(gate|ansible|tool|manual)\s", text, re.M)
        return {"plan": pl.group(1), "phases": len(phases), "ran": "Nothing has run." not in text}
    sys.exit("make-figures: %s has neither a status nor a plan" % path)


W = 880
COLW, GAP, X0, TOP = 196, 16, 24, 88
CHIP, PITCH = 24, 30


def fit(s, size, width, mono=False, bold=False):
    """Refuse to draw text wider than its space."""
    if tw(s, size, mono, bold) > width:
        sys.exit("make-figures: %r does not fit in %d units; shorten it or widen the box" % (s, width))


def gather():
    steps = []
    prev_machines, prev_classes = set(), set()
    last = None
    prev_env, prev_components = None, set()
    for num, title, d, cp in steps_from_readme():
        sites, peerings, components = declared_sites(d)
        c = checkpoint(cp)
        if "machines" in c:
            env = c["env"]
            by_site = {}
            for m in c["machines"]:
                by_site.setdefault(m.split("-")[0], []).append((m, m not in prev_machines))
            roles = {s[0]: s[1] for s in sites}
            groups = [(s, roles.get(s, ""), ms) for s, ms in by_site.items()]
            last = (env, c["machines"])
            prev_machines = set(c["machines"])
        else:
            env, machines = last
            by_site = {}
            for m in machines:
                by_site.setdefault(m.split("-")[0], []).append((m, False))
            for s, _, classes in sites:
                for cl in classes:
                    if (s, cl) not in prev_classes and s in by_site:
                        by_site[s].append(("%s %s class" % (s, cl), True))
            roles = {s[0]: s[1] for s in sites}
            groups = [(s, roles.get(s, ""), ms) for s, ms in by_site.items()]
        prev_classes = {(s, cl) for s, _, classes in sites for cl in classes}
        if env != prev_env:
            prev_components = set()
        new_components = [x for x in components if x not in prev_components]
        prev_env, prev_components = env, set(components)
        steps.append({"num": num, "title": title, "env": env, "groups": groups, "peerings": peerings, "cp": c,
                      "new_components": new_components})
    return steps


def column(f, x, st, height=None, title_lines=1):
    """Draw one step; return the height it needs. With height=None, measure only."""
    draw = height is not None
    y = TOP
    inner = COLW - 24
    tl = wrap(st["title"], COLW - 52, 15, bold=True)
    if draw:
        f.rect(x, TOP, COLW, height, fill="panel", stroke="rule", sw=1.5)
        f.circle(x + 22, y + 24, 12, fill="accent")
        f.text(x + 22, y + 29, str(st["num"]), 14, fill="on_accent", anchor="middle", bold=True)
        for i, t in enumerate(tl):
            f.text(x + 42, y + 29 + i * 20, t, 15, bold=True)
    y += 29 + (max(title_lines, len(tl)) - 1) * 20 + 26
    if draw:
        f.text(x + 12, y, "goatnet %s" % st["env"], 14, fill="quiet")
    y += 16
    for site, role, ms in st["groups"]:
        gh = 26 + len(ms) * PITCH + 4
        if draw:
            f.rect(x + 10, y, COLW - 20, gh, fill="paper", stroke="rule", rx=6)
            f.text(x + 20, y + 19, "site %s%s" % (site, " · " + role if role else ""), 13, fill="quiet")
        cy = y + 28
        for m, new in ms:
            if draw:
                fit(m, 13, inner - 24, mono=True)
                dashed = " class" in m
                f.rect(x + 18, cy, COLW - 36, CHIP, fill="accent_soft" if new else "panel",
                       stroke="accent" if new else "rule", rx=4, dash="4,3" if dashed else None, sw=1.5 if new else 1)
                f.text(x + 28, cy + 16.5, m, 13, mono=True, fill="ink" if new else "quiet", bold=new)
            cy += PITCH
        y += gh + 10
    if st["new_components"]:
        if draw:
            f.text(x + 12, y + 8, "new components", 13, fill="quiet")
        y += 30
        for comp in st["new_components"]:
            if draw:
                fit(comp, 13, inner - 8, mono=True)
                f.text(x + 20, y, comp, 13, mono=True)
            y += 19
        y += 6
    for p, via in st["peerings"]:
        st["edge_site"] = via
        if draw:
            f.line(x + COLW / 2, y - 6, x + COLW / 2, y + 22, stroke="accent", sw=1.5, arrow=True)
            f.rect(x + 18, y + 24, COLW - 36, 64, fill="paper", stroke="line", rx=6, dash="5,4")
            f.text(x + COLW / 2, y + 43, p, 13, mono=True, anchor="middle", bold=True)
            f.text(x + COLW / 2, y + 62, "their own goatnet,", 13, anchor="middle", fill="quiet")
            f.text(x + COLW / 2, y + 80, "peered from %s" % st["edge_site"], 13, anchor="middle", fill="quiet")
        y += 98
    c = st["cp"]
    if "machines" in c:
        lines = [("%d of %d converged" % (c["ok"], c["total"]), "good", True),
                 ("%d components" % c["components"], "quiet", False),
                 ("on %d machine%s" % (len(c["machines"]), "" if len(c["machines"]) == 1 else "s"), "quiet", False)]
    else:
        lines = [("plan: %d phases" % c["phases"], "accent", True),
                 ("printed by the", "quiet", False),
                 ("rehearsal, not run" if not c["ran"] else "and run", "quiet", False)]
    if draw:
        by = TOP + height - 66
        f.line(x + 12, by - 14, x + COLW - 12, by - 14, stroke="rule", sw=1)
        for i, (t, col, b) in enumerate(lines):
            fit(t, 14, inner, bold=b)
            f.text(x + 12, by + 6 + i * 20, t, 14, fill=col, bold=b)
    y += 88
    return y - TOP


def fig_steps():
    steps = gather()
    tlines = max(len(wrap(st["title"], COLW - 52, 15, bold=True)) for st in steps)
    h = max(column(None, 0, st, None, tlines) for st in steps)
    title = "Four rehearsed steps: one box, a goatnet, a second site, a partner peering"
    parts = []
    for st in steps:
        c = st["cp"]
        if "machines" in c:
            parts.append("step %d, %s: goatnet %s, %d of %d converged on %d machine%s (%s)"
                         % (st["num"], st["title"], st["env"], c["ok"], c["total"], len(c["machines"]),
                            "" if len(c["machines"]) == 1 else "s",
                            ", ".join(c["machines"])))
        else:
            parts.append("step %d, %s: %s, a plan of %d phases that is printed, not run"
                         % (st["num"], st["title"], c["plan"], c["phases"]))
    f = SVG(W, TOP + h + 24, title, "; ".join(parts) + ".")
    header(f, title, "goatbuilder --mock against a scripted converger; ./run compares each step with checkpoints/")
    for i, st in enumerate(steps):
        x = X0 + i * (COLW + GAP)
        column(f, x, st, h, tlines)
        if i < len(steps) - 1:
            f.line(x + COLW + 2, TOP + 24, x + COLW + GAP - 2, TOP + 24, sw=1.5, arrow=True)
    return f


FIGURES = [("four-steps", fig_steps)]


def main(argv):
    check = "--check" in argv
    stale = []
    for name, fn in FIGURES:
        fig = fn()
        for theme in THEMES:
            p = os.path.join(HERE, "%s-%s.svg" % (name, theme))
            out = fig.render(theme)
            if check:
                if not os.path.isfile(p) or open(p, encoding="utf-8").read() != out:
                    stale.append(os.path.relpath(p, ROOT))
            else:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(out)
                print(os.path.relpath(p, ROOT))
    if stale:
        print("out of date: " + ", ".join(stale) + "; run python3 -I docs/figures/make-figures.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
