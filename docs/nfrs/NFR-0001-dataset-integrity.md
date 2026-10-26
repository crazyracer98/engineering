# NFR-0001. The dataset and its generated files stay internally consistent

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
| `domain-count` | the domain-index intro sentence "N domains in B branches (E engineering branches, M management branches)" matches `domains.yaml` | `validate.check_domain_count` | `test_domain_count_mismatch` |
| `management-count` | the sentence "Section 10 states N of the M rules in management form … the other K (IDs)" in `meta` matches `rules.yaml`: N rules have a `management` form, M rules in all, and the K listed IDs (ranges such as `P5–P8, P18–P21, P35`, en dash or hyphen, for any prefix in `meta.id_prefixes`) are exactly the rules whose `management` is null | `validate.check_management_count` | `test_management_count_wrong_n`, `test_management_count_wrong_id_list`, `test_management_count_sentence_missing`, `test_parse_id_list_is_prefix_generic` |
| `slug-references` | every structured slug (rule and management `sources`, domain `references`, quote `source` and `extra_sources`, `master_rule.sources`) is in the merged registry; `taxonomy build` stops with exit 1 and a message naming the slug and where it is used | `validate.check_slug_references`, `cli.main` | `test_slug_reference_typo` |
| `source-used` | every source of `data/sources.yaml`, `paper/references-extra.yaml` and `docs/methodology-references.yaml` is used by data, or cited in `paper/` or `docs/`; a citation inside a registry (a title, note or `via`) does not count | `validate.check_source_used` | `test_unused_source`, `test_unused_paper_source`, `test_source_cited_only_by_itself_is_unused` |
| `table-columns` | every table of the rendered single file has the header's column count (escaped `\|` does not count) | `validate.check_table_columns` | `test_table_column_count`, `test_escaped_pipe_is_not_a_column` |
| `relation-contradictions` | see below | `validate.check_relation_contradictions` | `test_relation_contradiction_*`, `test_relation_self_reference`, `test_missing_inverse_is_not_a_contradiction`, `test_contradiction_found_when_edges_run_from_larger_to_smaller_id` |
| `inverse-complete` | A `strengthens` B needs B `strengthened_by` A and the reverse; the same for `checks`/`checked_by`. `depends_on` and `scaled_by` have no inverse type and stay one-way | `validate.check_inverse_complete` | `test_missing_inverse_strengthened_by`, `test_missing_inverse_strengthens`, `test_missing_inverse_checked_by` |
| `conflicts-symmetric` | A `conflicts_with` B needs B `conflicts_with` A | `validate.check_conflicts_symmetric` | `test_conflicts_one_sided` |
| `related-order` | `related` keys follow `meta.relation_types` order, and each list's IDs run by prefix (`meta.id_prefixes` order), then by number | `validate.check_related_order` | `test_related_key_order`, `test_related_id_order` |
| `override-agreement` | a `related_text` override names exactly the rule IDs of the rule's structured `related`, each as often; non-rule text ("accountability", "(see K7)", qualifiers) is ignored | `validate.check_override_agreement` | `test_override_disagrees_with_related`, `test_override_ignores_non_rule_text` |
| `sources-primary-first` | every rule's `sources`, and every management form's `sources`, list all primary sources before any secondary one | `validate.check_sources_primary_first` | `test_secondary_source_before_primary`, `test_management_secondary_source_before_primary` |
| `primary-source` | every rule has at least one `primary` source unless `meta.known_exceptions` lists it (today only P53) | `validate.check_primary_source` | `test_primary_source_missing`, `test_known_exception_is_allowed` |
| `counterexamples` | every conditional rule has a non-empty `counterexample` | `validate.check_counterexamples` | `test_c_rule_without_counterexample` |
| `conflict-rules` | every conflict rule names at least 2 distinct, existing rules | `validate.check_conflict_rules` | `test_k_rule_names_too_few_rules`, `test_k_rule_names_unknown_rule` |
| `category-membership` | each rule is listed in exactly one category, the one in its `category` field | `validate.check_category_membership` | `test_category_membership_mismatch` |
| `quick-view` | the quick view has 5 to 9 questions, one per category | `validate.check_quick_view` | `test_quick_view_count` |
| `id-map` | every `history.id_map` entry points at an existing rule | `validate.check_id_map` | `test_id_map_target_missing` |
| `citations` | every citation in data, `paper/` and `docs/` resolves in the merged registry and is well formed | `validate.check_citations` | `test_unresolved_citation_*`, `test_citation_in_code_is_ignored` |
| `registry-unique` | slugs and URLs are unique across the three registries | `validate.check_registry_unique` | `test_duplicate_slug_across_registries`, `test_duplicate_url_across_registries` |
| `schema` | every data file, and the two extra registries, validate against their JSON Schema with `jsonschema` and a `FormatChecker`; a missing or invalid schema, or an extra registry that fails to load, is a finding for that file and the other files are still validated | `validate.check_schema` | `test_schema_violation`, `test_schema_format_checker_is_enforced`, `test_schema_covers_extra_registries`, `test_schema_findings_are_per_file` |
| generated files current | `publication/` equals what `data/` renders | `taxonomy build --check`, prek hook `taxonomy-generated` | `test_build_check_detects_stale_files`, `test_publication_is_up_to_date` |

`test_every_check_has_a_seeded_test` fails when a check is added to `CHECKS`
without being listed here. Edition 9 is not an oracle: since the G1 decision
(ADR 0003, "G1 delta") `data/` deliberately differs from it, and no test
compares the rendered file with the imported edition-9 text.

A file that cannot be read or parsed (missing, YAML syntax error, missing schema)
is reported as a `load` or `schema` finding with its path, and a check that
crashes on malformed data is reported as a finding of its own. When a data file
fails to load, the other checks cannot run, but the `schema` check still
validates every other file one by one. The CLI exits 1
with that message and no traceback.

### Relation contradictions

A missing inverse is not a contradiction; `inverse-complete` and
`conflicts-symmetric` report it. This check fails on a contradiction:

1. A rule lists itself in `related`.
2. Two rules conflict (`conflicts_with`, in either direction) and also have a
   supportive relation (`depends_on`, `strengthens`, `strengthened_by`,
   `checks`, `checked_by`, `scaled_by`) in either direction.
3. Two rules depend on each other (`depends_on` both ways).

Each unordered pair is examined once, with edges in either direction.

## Source

Round 4 of the method (single source and automated checks) and the repository
plan's integrity-check list, as amended by its decisions: schema validation
uses a `FormatChecker`, and since the user's G1 decision a missing inverse, a
one-sided `conflicts_with`, an unordered `related` list, a `related_text`
override that disagrees with `related` and a secondary source listed before a
primary one are errors. Related: [ADR 0003](../adrs/0003-dataset-single-source-of-truth.md),
[ADR 0004](../adrs/0004-edition-equals-release-version.md).

## Verification

The prek hooks `taxonomy-check` and `taxonomy-generated` run on every change to
`data/`, `schema/`, `src/`, `paper/`, `docs/` and `publication/`; `pytest`
runs the seeded-violation tests (one per check) on every commit; CI runs the
same hooks.
