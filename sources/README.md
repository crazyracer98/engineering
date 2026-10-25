# sources/

Provenance for the taxonomy: material it was derived from.

- `import/` holds the two original inputs, verbatim and byte-identical.
  `engineering-best-practices.md` is edition 9, whose content is
  authoritative. `engineering-best-practices.yaml` is an older edition-6
  export (67 rules), used only as the schema seed. Neither is the source
  of truth: `data/` is (ADR 0003).
- `import/import_v9.py` is the importer that produced the first `data/`
  from those two inputs. It is now a frozen provenance record. By default
  (`--check`) it regenerates the import in memory and compares it with
  `data/` (exit 1 on any difference, which is expected once `data/` has
  been edited by hand). Only `--write` overwrites `data/`.

## Don't

- Edit the files in `import/`; changing a byte breaks their provenance.
- Run `import/import_v9.py --write` to change the taxonomy; edit `data/`
  instead (`--write` discards every edit made since the import).
