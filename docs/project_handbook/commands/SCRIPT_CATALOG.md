# Script Catalog

The stable user-facing interface is `apk_sbom.cli`. Scripts under `scripts/`
build fixtures, aggregate evidence, run evaluations, or generate documents.
Most write JSON/CSV/Markdown artifacts and should be run from the repository
root.

## Toolchain and controlled fixtures

- `check_toolchain.py`: reports required and optional tool availability.
- `build_controlled_apk.py`: builds a known coordinate/version fixture with a
  selected clear or R8 variant.
- `build_limitation_apk.py`: builds controlled boundary fixtures.
- `run_generated_apk_batch.py`: builds and evaluates the configured generated
  fixture set.
- `evaluate_controlled_reports.py`: aggregates controlled exact-version results.
- `evaluate_baselines.py`: compares simpler baseline methods.
- `build_apk_testset_inventory.py`: inventories APK evidence.
- `build_apk_type_evaluation.py`: groups results by APK type.
- `build_dataset_coverage_matrix.py`: summarizes dataset dimensions.

## Real-APK collection and proof

- `collect_fdroid_real_apk_batch.py`: collects source-linked F-Droid cases.
- `scaffold_real_apk_proof.py`: creates proof-bundle structure.
- `advance_real_apk_batch_proofs.py`: advances configured source-validation
  cases and generated status.
- `build_real_apk_candidate_matrix.py`: prioritizes candidates.
- `build_real_apk_source_validation_dashboard.py`: generates current real-APK
  status and metrics.

## Reference DB and coverage

- `build_source_observed_reference_catalog.py`: exact versions observed in
  source trees.
- `build_source_observed_failed_download_retry_plan.py`: classifies failed
  source-observed downloads.
- `extract_missing_source_observed_all_versions.py`: selects missing all-version
  extraction work.
- `build_real_apk_priority_reference_catalog.py`: value-first real-APK catalog.
- `build_real_apk_priority_failed_download_retry_plan.py`: retry classification.
- `build_real_apk_priority_lightweight_retry.py`: bounded lightweight recovery.
- `recover_real_apk_priority_from_existing_db.py`: copies already-complete rows
  from another DB.
- `stage_real_apk_priority_i2p_source_build.py`: prepares isolated I2P source
  builds.
- `build_scoped_reference_db_experiment.py`: adds selected rows to an isolated
  experiment DB.
- `filter_reference_db.py`: creates a coordinate/version slice.
- `build_large_combined_reference_db.py`: combines large reference sources.
- `build_reference_db_coverage_dashboard.py`: source-row coordinate/exact
  coverage denominator.
- `build_source_version_candidate_queue.py`: ranks source-observed versions for
  bounded reference-growth work.
- `run_real_apk_priority_reference_evaluation.py`: priority DB evaluation.
- `run_large_combined_source_coordinate_evaluation.py`: source-constrained
  large-DB evaluation.
- `build_large_combined_evaluation_analysis.py` and
  `build_large_db_source_gap_triage.py`: analyze large-DB outcomes.

## Matcher and wrong-version diagnostics

- `analyze_version_band_ties.py`
- `build_low_risk_version_band_diagnostics.py`
- `build_low_risk_version_band_trigger_diagnostics.py`
- `build_version_tie_reranker_diagnostics.py`
- `build_version_unique_literal_context_diagnostics.py`
- `build_version_unique_literal_context_control_validation.py`
- `build_version_unique_literal_context_promotion_candidate.py`
- `build_version_unique_literal_context_default_promotion_readiness.py`
- `evaluate_wrong_version_p1_experiment.py`
- `build_wrong_version_optimization_dashboard.py`
- `build_lifecycle_family_separation_diagnostics.py`
- `build_artifact_family_diagnostics.py`
- `build_pom_coherence_diagnostics.py`
- `build_literal_context_version_tie_diagnostics.py`
- `evaluate_api_reference_weight.py`
- `evaluate_opcode_ngram_weight.py`
- `build_opcode_api_signal_diagnostics.py`
- `evaluate_low_risk_source_versions.py`
- `evaluate_nextcloud_source_versions.py`

These scripts produce diagnostic or promotion-gate evidence. Their names do not
imply that the tested method became a default.

## Candidate pruning and shortlist diagnostics

- `build_coarse_to_fine_pruning_diagnostics.py`
- `build_class_correspondence_pruning_diagnostics.py`
- `build_family_identity_prefilter_simulation.py`
- `build_composite_family_shortlist_simulation.py`
- `build_composite_family_shortlist_live_validation.py`
- `build_composite_family_shortlist_opt_in_verification.py`
- `build_composite_family_shortlist_default_promotion_readiness.py`
- `build_guarded_reference_db_promotion_workflow.py`

## R8, hidden code, and boundary diagnostics

- `build_r8_obfuscation_method_selection.py`
- `build_r8_obfuscation_diagnostics.py`
- `build_r8_multiscale_feature_diagnostics.py`
- `build_r8_optimization_aware_diagnostics.py`
- `build_r8_phase4_scoped_experiment_diagnostics.py`
- `build_r8_phase5_scoped_trigger_diagnostics.py`
- `build_r8_phase5_trigger_control_validation.py`
- `build_r8_phase5_report_evidence.py`
- `build_r8_minified_confidence_policy_diagnostics.py`
- `build_r8_minified_confidence_report_evidence.py`
- `build_r8_structural_recall_experiment.py`
- `build_r8_apk_structural_promotion_gate.py`
- `build_r8_strict_apk_promotion_gate_matrix.py`
- `build_hidden_dex_diagnostics.py`
- `build_native_boundary_diagnostics.py`
- `build_k9_blocker_diagnostics.py`
- `build_limitation_boundary_dashboard.py`
- `build_no_maven_signal_diagnostics.py`
- `build_no_maven_androidx_report_only_experiment.py`
- `build_mastodon_fork_family_report_only_audit.py`

## AI and hybrid work

- `build_ai_r8_training_dataset.py`
- `train_ai_r8_assistant.py`
- `build_ai_r8_assistant_diagnostics.py`
- `build_ai_r8_summary_export.py`
- `build_ai_r8_report_only_demo.py`
- `build_ai_r8_token_corpus.py`
- `train_ai_r8_tiny_transformer.py`
- `build_ai_r8_independent_corpus.py`
- `build_ai_r8_raw_opcode_corpus.py`
- `train_ai_r8_raw_opcode_transformer.py`
- `build_ai_r8_mvp_integration_gate.py`
- `build_ai_r8_final_evaluation.py`
- `build_hybrid_matcher_router.py`
- `build_hybrid_ai_production_report_evidence.py`
- `build_final_hybrid_ai_demo_smoke.py`
- `run_final_ai_defense_demo.py`
- `build_version_band_rerank_experiment.py`
- `build_version_band_apk_reranker.py`
- `build_version_band_candidate_expansion_v3.py`

## Reporting, thesis, demo, and external validation

- `build_thesis_evaluation_tables.py`
- `build_thesis_artifact_index.py`
- `build_demo_final_matcher_recall_diagnostics.py`
- `build_demo_final_transparency_export.py`
- `build_demo_final_fixable_reference_growth_result.py`
- `build_demo_final_fixable_reference_retry.py`
- `build_demo_final_second_stage_reference_retry.py`
- `build_graduation_demo_rehearsal.py`
- `run_graduation_demo_report.py`
- `build_osv_source_validation_triage.py`
- `validate_sbom_against_version_catalog.py`
- `build_external_scanner_validation_status.py`
- `run_external_scanner_validation.py`
- `compare_experiment_summaries.py`
- `evaluate_reconciled_reference_eight.py`
- `build_mvp_cons_improvement_plan.py`

## Finding exact script flags

Run:

```powershell
docker compose run --rm apk-sbom python scripts/SCRIPT_NAME.py --help
```

Scripts are more specialized and evolve faster than the stable CLI. Their
generated Markdown report is usually the best explanation of the expected
output and verdict.
