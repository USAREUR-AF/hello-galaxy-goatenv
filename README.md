<h1 align="center">hello-galaxy-goatenv</h1>

<p align="center">
  A step-by-step walkthrough that builds a goat environment from nothing.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

> [!NOTE]
> goat is pre-1.0: interfaces can still change between releases. This repository is generated from goat's source tree; each update arrives as a new commit on `main`.

The goatnet the tutorials build, one verified step at a time, so you can diff your own run against a known-good one. Part of the Hello Galaxy series: small, runnable examples, each showing best practice in one dimension. This one builds [`usareur-af/goatenv`](https://github.com/usareur-af/goatenv) from an empty directory using [`goatcore`](https://github.com/usareur-af/goatcore).

| Step | Tutorial (in goatcore) | Here |
|---|---|---|
| 0. goatlite: one box, one file | `docs/tutorials/00-goatlite.md` | `00-goatlite/`, `checkpoints/00-goatlite.txt` |
| 1. A new goatnet | `docs/tutorials/01-new-goatnet.md` | `01-founder/`, `checkpoints/01-new-goatnet.txt` |
| 2. The first federated node | `docs/tutorials/02-first-federated-node.md` | `02-first-federated-node/`, `checkpoints/02-first-federated-node.txt` |
| 3. A boundary node for partner sharing | `docs/tutorials/03-boundary-node.md` | `03-boundary-node/`, `checkpoints/03-boundary-node.txt` |

Each step directory is a `goatbuilder --mock` fixture: the declaration (`goatbuilder.yaml`), the digest-pinned refs (`declared/pins.yaml`) and how each machine behaves under the scripted converger (`converger.yaml`). `diff 01-founder/goatbuilder.yaml 02-first-federated-node/goatbuilder.yaml` is exactly what tutorial 2 declares.

## Run it

You need `goatbuilder` built from `goatcore` at the ref in `GOATBUILDER_REF` (`cd crates && cargo build --release -p goatbuilder`, then put it on your `PATH` or set `GOATBUILDER`), and a checkout of `goatcore` in `GOAT_REPO` (the acceptance assay reads its manifest).

```bash
GOAT_REPO=../goatcore ./run            # rehearses all four steps and compares them with checkpoints/
GOAT_REPO=../goatcore ./run --record   # re-records the checkpoints after a deliberate change
```

Nothing touches a network: a scripted converger stands in for the hosts, so every verb runs for real against files and the output is the same every time.

## Build on your own base images

Every goat image starts from base images named by role: `rust-build`, `go-build`, `runtime-cc`, `runtime-static`, `runtime-shell` (and `node-build` in goatstuff). goatcore's defaults are Chainguard's free images, pinned by digest. To build on others, such as a private Chainguard catalogue with versioned tags and FIPS variants: put a file per role at `ops/base-images/<role>/Dockerfile` in your environment, holding one digest-pinned `FROM` line, and every image built from the assembled tree uses it. No Dockerfile changes.

[`base-images/overlay/`](base-images/overlay/) is that overlay for a private catalogue under a placeholder organisation, `example-org`. The rehearsal copies it over goatcore's role files, as a deploy does, and prints the build arguments three goatcore images would get:

```bash
GOAT_REPO=../goatcore base-images/run            # compares with checkpoints/base-images.txt
GOAT_REPO=../goatcore base-images/run --record   # re-records after a deliberate change
```

```
== roles after the overlay is copied over goatcore
go-build  overlay  cgr.dev/example-org/go-fips:1.26-dev@sha256:0000…
runtime-cc  overlay  cgr.dev/example-org/glibc-dynamic-fips:latest@sha256:0000…
…
== build arguments for ops/goat-relay/Dockerfile
BASE_RUNTIME_CC=cgr.dev/example-org/glibc-dynamic-fips:latest@sha256:0000…
```

To build for real, copy your environment over goatcore and run `python3 ops/base-images/base-images.py build --unit <image workflow stem> --tag <your registry>/<image>:<tag> --push`; then pin the digest in your environment's `ops/pins/`. The whole procedure, with the rules each role's image must meet, is goatcore's [build goat images on your own base images](https://github.com/usareur-af/goatcore/blob/main/docs/operations/build-on-your-own-base-images.md).

## Licence

`hello-galaxy-goatenv` was written by U.S. Federal government employees. In the U.S. it is not subject to copyright and is in the public domain; in countries where copyright is recognized, it is released under the [Apache License 2.0](LICENSE). See [INTENT.md](INTENT.md).
