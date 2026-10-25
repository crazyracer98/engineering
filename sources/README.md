# sources/

Provenance for the taxonomy: material it was derived from.

- `import/` holds the two original inputs, verbatim and byte-identical.
  `engineering-best-practices.md` is edition 9, whose content is
  authoritative. `engineering-best-practices.yaml` is an older edition-6
  export (67 rules), used only as the schema seed. Neither is the source
  of truth; `data/` will be (ADR 0003, forthcoming).
- `import/import_v9.py` (planned) will live there too.

## Don't

- Edit the files in `import/`; changing a byte breaks their provenance.
