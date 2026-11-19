# Figures

`make-figures.py` draws every figure in this directory from the tree; nothing in a figure is typed by hand. Each figure is written in a light and a dark variant for a `<picture>` element.

```sh
python3 -I docs/figures/make-figures.py           # write the SVG files
python3 -I docs/figures/make-figures.py --check   # exit 1 if a committed file is out of date
```

| Figure | Shows | Data |
|---|---|---|
| `four-steps` | the four rehearsed steps: the goatnet, its sites and machines, the components each step adds, and what the rehearsal reports | the step table in `README.md`; each step's `goatbuilder.yaml` (sites, roles, classes, components, peerings); each `checkpoints/*.txt` (the status line and machine table, or the federate plan's phases) |

Regenerate after a checkpoint is re-recorded (`./run --record`). The generator refuses to draw text wider than its box, and refuses a checkpoint whose machine table disagrees with its status line.

## Checks

Each figure was rendered in headless Chromium as an `<img>` at 830 px and 400 px wide in both themes and inspected. Text is at least 13 units on an 880-unit canvas.
