# AGENTS.md

## Project

Seigaiha is a Python CLI that generates traditional and modern Japanese wave patterns as SVG and PNG.
Input is a JSON *preset*; output is one "single element" file plus, when the preset defines `pattern`,
a full pattern file. Distributed primarily as a Docker image (`ghcr.io/toshy/seigaiha`).

- Python `>=3.11`, packaged with `setup.py` (version constant `VERSION` in `setup.py`).
- Console entrypoint: `seigaiha` → `seigaiha.cli:cli`; module entrypoint: `python -m seigaiha`.
- Docs are built with [Zensical](https://zensical.org) (config in `zensical.toml`), sources in
  `docs/`, published to GitHub Pages.

## Layout

```
seigaiha/
  __main__.py   # python -m seigaiha
  cli.py        # click command + all polygon geometry (Shapely) and pattern assembly
  svg.py        # SVGmaker: XML string building, viewbox, colours, SVG/PNG writing (CairoSVG)
  args.py       # click callbacks: InputPathChecker, OutputPathChecker, OptionalValueChecker
  helper.py     # files_in_dir, read_json, combine_arguments_by_batch
  exception.py  # InvalidViewBoxError, SvgToPngImageError
input/          # example presets (JSON) — gitignored contents, used as CLI default input dir
output/         # generated artefacts — gitignored
docs/           # Zensical docs sources
```

## How it fits together

1. `args.py` callbacks resolve `-i/--input-path`, `-o/--output-path` and `-e/--extension` into
   per-*batch* dicts (`{"batch": n, ...}`). Each option may be repeated; a single value is broadcast
   across all input batches, otherwise counts must match.
2. `helper.combine_arguments_by_batch` merges those per-option lists into one dict per batch.
3. `cli.create_polygon` builds the base polygon with Shapely: points on a circle → rotate → rescale →
   translate back to origin → split into concentric fractions → alternating colours.
4. `SVGmaker` turns coordinates into SVG XML (`%polygons%` placeholder substitution) and writes
   `.svg` / `.png`.
5. If the preset has a `pattern` object, `cli` tiles translated copies of the polygon, intersects them
   with a container polygon to clip edges, optionally substitutes "broken" polygons/images, and writes
   a second file suffixed `seigaiha`.

Randomness is seeded from the preset's `seed` key via `random.seed`, so runs are reproducible; keep it
that way — don't introduce unseeded randomness.

## Preset keys (input JSON)

`seed`, `fractions`, `edges`, `spacing`, `rotation`, `colours` (list of `{R,G,B,A}`),
`output.resolution` (default 2500), `output.svg.preserveAspectRatio`, `output.svg.style`, and
`pattern` with `horizontal/vertical.{amount,spacing}`, `alternate`, and
`broken.{factor,factor_rounding,fractions,skip_edge,colours,images}`. `broken.images` are
base64-encoded SVG strings. See `input/default.json` and `docs/getting-started.md`.

## Commands

Everything runs through Docker Compose via [Task](https://taskfile.dev); there is no local venv workflow.

```sh
task                        # list tasks
task build                  # build dev + prod images
task dev -- -i input/default.json -o output    # run CLI in dev image (args after --)
task prod -- -h             # run CLI in prod image
task shell:dev              # bash in dev container
task ruff / task ruff:fix
task black / task black:fix
task mypy
task docs / task docs:live  # build / serve docs on :8001 (Zensical)
task svg2base i=path.svg    # base64 an SVG for `pattern.broken.images`
task down                   # tear down compose
```

Repo/CI hygiene tooling, also containerised (image tags pinned in the Taskfile `env` block:
`HADOLINT_IMAGE`, `ACTIONLINT_IMAGE`, `ZIZMOR_IMAGE`, `PINACT_IMAGE`):

```sh
task hadolint               # lint the Dockerfile
task actionlint             # lint .github/workflows
task zizmor                 # audit workflows for security issues
task pinact [t=<token>]     # check actions are pinned to commit SHAs (--diff)
task pinact:fix [t=<token>] # pin them in place
```

`task pinact`/`pinact:fix` hit the GitHub API; pass a token via `t=github_pat_...` to avoid rate
limiting.

Pre-commit (`.pre-commit-config.yaml`, `fail_fast: true`) runs ruff, black and mypy in the dev
container. CI: `codequality.yml` (ruff), `codestyle.yml` (black), `statictyping.yml` (mypy),
`security.yml` (pip-audit), `hadolint.yml`, `actionlint.yml`, `zizmor.yml`, `pinact.yml`,
`docs.yml` (Zensical → GitHub Pages), `release.yml` (publishes the image on GitHub release).

## Conventions

- Formatting is **Black** with default settings; lint is **Ruff** with default rules; **Mypy** runs
  with defaults. None of the three has a config file — do not add one unless asked.
- Third-party imports lacking stubs are silenced inline with `# type: ignore[import-untyped]`.
  Keep annotations light and consistent with the existing style; don't retrofit strict typing broadly.
- Module-level functions with short triple-quoted docstrings are the norm in `cli.py`/`helper.py`;
  `SVGmaker` prefixes internal methods with `_`.
- Logging uses `loguru` (`logger.info`), and `cli` is wrapped in `@logger.catch`.
- Errors that reach the user are custom exceptions in `exception.py`; invalid CLI input raises
  `click.BadParameter`.
- GitHub Actions are pinned to commit SHAs with a `# vX.Y.Z` comment, and `pinact.yml` enforces it.
  When adding or bumping an action, run `task pinact:fix` rather than writing a bare version tag.
  Workflow jobs declare least-privilege `permissions` and use `persist-credentials: false` on
  checkout; keep new workflows in that shape (`task actionlint` and `task zizmor` verify).

## Gotchas

- **There is no test suite.** Verify changes by rendering presets, e.g.
  `task dev -- -i input/default.json -o output` (or `task dev:times t=5 -- ...` for repeated runs),
  then inspecting the SVG/PNG in `output/`. Large `output.resolution` values (the examples use 8500)
  make PNG rendering slow — use a small resolution while iterating.
- `input/` and `output/` are gitignored; example presets already tracked in `input/` are the reference
  fixtures. Don't commit generated artefacts.
- PNG rendering needs `libcairo2`, installed in the Docker image — that's why the containerised
  workflow is the supported one.
- Output filenames get a datetime suffix by default (`--unique-filename`); pass
  `--no-unique-filename` for stable paths when diffing renders.
- Bumping the release version means editing `VERSION` in `setup.py`; the Docker tag comes from the
  GitHub release tag.
