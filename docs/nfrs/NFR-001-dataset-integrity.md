# NFR-001. The dataset and its generated files stay internally consistent

## Status

Implemented

## Attribute

Maintainability (data integrity).

## Description

`uv run taxonomy check` exits 0 on every commit, and `uv run taxonomy build --check`
shows that `publication/` is current. Each check below fails with a message that
names the offending ID, slug, file or row. "Citation" means a Pandoc citation
written as `[@slug]`; citations inside code spans and fenced code are ignored.

| Check | Rule | Enforced in | Test |
| --- | --- | --- | --- |
| `unique-ids` | IDs are unique within rules, conflict rules, quotes and categories, and no conflict ID is also a rule ID | `validate.check_unique_ids` | `test_unique_ids` |
| `related-targets` | every `related` target is an existing rule | `validate.check_related_targets` | `test_related_target_missing` |
| `id-references` | rule IDs named in categories, conflicts, domains, quotes and `known_exceptions` exist (`Master` allowed where the schema allows it) | `validate.check_id_references` | `test_id_reference_missing` |
| `rule-in-domain` | every rule appears in at least one domain row | `validate.check_rule_in_domain` | `test_rule_in_no_domain` |
| `source-used` | every source of `data/sources.yaml`, `paper/references-extra.yaml` and `docs/methodology-references.yaml` is used by data, or cited in `paper/` or `docs/` | `validate.check_source_used` | `test_unused_source`, `test_unused_paper_source` |
| `table-columns` | every table of the rendered single file has the header's column count (escaped `\|` does not count) | `validate.check_table_columns` | `test_table_column_count`, `test_escaped_pipe_is_not_a_column` |
| `relation-contradictions` | see below | `validate.check_relation_contradictions` | `test_relation_contradiction_*`, `test_relation_self_reference`, `test_missing_inverse_is_allowed` |
| `primary-source` | every rule has at least one `primary` source unless `meta.known_exceptions` lists it (today only C15) | `validate.check_primary_source` | `test_primary_source_missing`, `test_known_exception_is_allowed` |
| `counterexamples` | every C-rule has a non-empty `counterexample` | `validate.check_counterexamples` | `test_c_rule_without_counterexample` |
| `conflict-rules` | every K-rule names at least 2 distinct, existing rules | `validate.check_conflict_rules` | `test_k_rule_names_too_few_rules`, `test_k_rule_names_unknown_rule` |
| `category-membership` | each rule is listed in exactly one category, the one in its `category` field | `validate.check_category_membership` | `test_category_membership_mismatch` |
| `quick-view` | the quick view has 5 to 9 questions, one per category | `validate.check_quick_view` | `test_quick_view_count` |
| `id-map` | every `history.id_map` entry points at an existing rule | `validate.check_id_map` | `test_id_map_target_missing` |
| `citations` | every citation in data, `paper/` and `docs/` resolves in the merged registry and is well formed | `validate.check_citations` | `test_unresolved_citation_*`, `test_citation_in_code_is_ignored` |
| `registry-unique` | slugs and URLs are unique across the three registries | `validate.check_registry_unique` | `test_duplicate_slug_across_registries`, `test_duplicate_url_across_registries` |
| `schema` | every data file, and the two extra registries, validate against their JSON Schema with `jsonschema` and a `FormatChecker` | `validate.check_schema` | `test_schema_violation`, `test_schema_format_checker_is_enforced`, `test_schema_covers_extra_registries` |
| generated files current | `publication/` equals what `data/` renders | `taxonomy build --check`, prek hook `taxonomy-generated` | `test_build_check_detects_stale_files`, `test_publication_is_up_to_date` |

`test_every_check_has_a_seeded_test` fails when a check is added to `CHECKS`
without being listed here. `test_round_trip_only_the_edition_line_differs`
checks that the rendered single file equals the imported edition-9 text except
for the version line.

### Relation contradictions

Missing inverses are allowed: 122 one-directional relations exist at 1.0.0 and
are not errors. The check fails only on a contradiction:

1. A rule lists itself in `related`.
2. Two rules conflict (`conflicts_with`, in either direction) and also have a
   supportive relation (`depends_on`, `strengthens`, `strengthened_by`,
   `checks`, `checked_by`, `scaled_by`) in either direction.
3. Two rules depend on each other (`depends_on` both ways).

## Source

Round 4 of the method (single source and automated checks) and the repository
plan's integrity-check list, as amended by its decisions: inverses may be
missing, and schema validation uses a `FormatChecker`. Related: [ADR 0003](../adrs/0003-dataset-single-source-of-truth.md),
[ADR 0004](../adrs/0004-edition-equals-release-version.md).

## Verification

The prek hooks `taxonomy-check` and `taxonomy-generated` run on every change to
`data/`, `schema/`, `src/`, `paper/`, `docs/` and `publication/`; `pytest`
runs the seeded-violation tests (one per check) on every commit; CI runs the
same hooks.
