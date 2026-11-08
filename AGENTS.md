# AGENTS.md

Instructions for AI coding agents, and a short version for anyone working here. [CONTRIBUTING.md](CONTRIBUTING.md) is the full process.

## What this repository is

hello-galaxy-goatenv is the worked example the goatnet tutorials rehearse: one directory per tutorial step (`00-goatlite`, `01-founder`, `02-first-federated-node`, `03-boundary-node`) and a recorded checkpoint of each rehearsal's output. The tutorials themselves are in goatcore's `docs/tutorials/`.

It sits beside [goatcore](https://github.com/usareur-af/goatcore), which builds and runs a goatnet. A real deployment is goatcore at a pinned commit plus a private overlay repository with that deployment's configuration; no deployment's configuration is ever in this repository.

## Layout

| Path | What |
|---|---|
| `00-goatlite/` … `03-boundary-node/` | the files each tutorial step starts from |
| `checkpoints/` | the expected output of each rehearsal |
| `run` | rehearses every step and diffs it against its checkpoint |
| `GOATBUILDER_REF` | the goatcore commit whose `goatbuilder` the rehearsal uses |

## Rules CI enforces

1. **No identifier of a real deployment.** Hostnames, domains, addresses, account ids, keys, people, places and organisations of any real goatnet never enter a file or a commit message. Use the example goatnet `zagros`, documentation addresses (RFC 5737, and `100.127.0.0/16` for mesh), and `example.org` mail. The leak gate (`.github/workflows/leak-gate.yml`) checks every added line against a private list of deployment names. It never prints what matched, so a red leak gate means: rename the identifier. The name list is not available outside CI.
2. **Commits.** Conventional Commits subject of 100 characters or fewer, with a scope (`fix(<component>): …`). Every commit is signed off (`git commit -s`, the DCO) and signed. One logical change per pull request.
3. **Design documents move with the code.** A change to behaviour, data flow, topology or an integration point updates its design document in the same pull request, using the status words built, measured, designed and not built exactly. Decisions are ADRs in [goatcore](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md).

## Before you push

```bash
shellcheck run
GOAT_REPO=../goatcore ./run          # every rehearsal must match its checkpoint
```

`./run --record` rewrites the checkpoints. Use it only when a tutorial's output changed on purpose, and review the diff.
