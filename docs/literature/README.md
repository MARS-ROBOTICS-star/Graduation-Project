# Literature Workflow

## Goal

Keep source PDFs and MinerU-derived Markdown side by side so Codex can read the Markdown first and fall back to the PDF when verification is needed.

## Directory Rules

- Source PDFs stay directly under `docs/literature/`.
- MinerU outputs go under `docs/literature/mineru_output/`.
- `docs/literature/catalog.md` maps each PDF to its converted Markdown and extracted assets.

## Codex Reading Order

1. Read the corresponding Markdown file first when it exists.
2. Use the source PDF to verify figures, equations, page numbers, and passages that look suspicious after conversion.
3. Treat the PDF as the source of truth if the Markdown and PDF disagree.

## Conversion Command

Run from the repository root:

```bash
scripts/literature/mineru_batch_convert.sh
```

Convert a single paper:

```bash
scripts/literature/mineru_batch_convert.sh --pdf "docs/literature/Sartoretti 等 - 2019 - Distributed learning of decentralized control policies for articulated mobile robots.pdf"
```

Pass extra MinerU CLI flags after `--`:

```bash
scripts/literature/mineru_batch_convert.sh -- --lang en
```

## First-Run Note

On this machine, the first MinerU run may need to download parsing models.

- If your shell inherits proxy variables that point to a local proxy which is unavailable in the current session, clear those variables first.
- MinerU supports switching the model source to `modelscope`, which is the current preferred first-run path in this repository.

Example:

```bash
/usr/bin/env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  MINERU_MODEL_SOURCE=modelscope \
  scripts/literature/mineru_batch_convert.sh \
  --pdf "docs/literature/Staicu - 2007 - Dynamics of a 3-RRR Spherical Parallel Mechanism Based on Principle of Virtual Powers.pdf" \
  -- -b pipeline -d cpu -l en
```

## Expected Result

After conversion, each parsed paper should have:

- the original PDF in `docs/literature/`
- a MinerU output directory in `docs/literature/mineru_output/`
- at least one Markdown file that Codex can read directly
- extracted images or assets when MinerU decides they are useful
