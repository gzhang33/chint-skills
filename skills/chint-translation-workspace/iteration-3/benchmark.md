# Skill Benchmark: chint-translation (v2.0.0)

**Model**: gemini-4-neon-high
**Date**: 2026-11-23T16:10:00Z
**Evals**: 0, 1, 2, 3, 4 (1 blind run each per configuration; 41 assertions total)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate (Macro Mean) | 100.0% ± 0.0% | 60.5% ± 12.9% | +0.40 |
| Pass Rate (Micro, 41 assertions) | 41/41 (100.0%) | 25/41 (61.0%) | +0.39 |
| Time | 215.6s ± 50.1s | 129.0s ± 70.4s | +86.6s |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill | Delta |
|------|------------|---------------|-------|
| Eval 0 (`acb-accessory-catalog-translation`) | 8/8 (100.0%) | 4/8 (50.0%) | +50.0% |
| Eval 1 (`mccb-datasheet-audit`) | 9/9 (100.0%) | 5/9 (55.6%) | +44.4% |
| Eval 2 (`ats-manual-translation-track2`) | 6/6 (100.0%) | 4/6 (66.7%) | +33.3% |
| Eval 3 (`en-to-zh-datasheet-backtranslation`) | 10/10 (100.0%) | 8/10 (80.0%) | +20.0% |
| Eval 4 (`mccb-iec60947-2-2024-annexes-translation`) | 8/8 (100.0%) | 4/8 (50.0%) | +50.0% |

## Key Differentiators Observed

- **Eval 0 (`acb-accessory-catalog-translation`)**: `with_skill` enforced `ACB Key Lock (KLC)`, `panel hole saw or hole punch`, hyphenated `circuit-breaker`, and explicit non-fabrication of rated control voltage; `without_skill` drifted to `Breaker-Mounted Keylock`, `hole cutter`, unhyphenated `circuit breaker`, and omitted the non-fabrication caveat.
- **Eval 1 (`mccb-datasheet-audit`)**: `with_skill` validated `Frame size: 250 A` under exact `IEC 60947-2:2024 Cl. 3.1.1` (vs `GB/T 14048.2 Inm`), flagged `durability` (0 occurrences in Ed. 6.0 -> `operational performance` / `operating cycles` / `endurance`), `kA rms`, and unscoped `100% Icu`; `without_skill` permitted `durability`, missed `kA rms` and `100% Icu` scoping, and mislabelled selectivity Cat A/B as `Utilization category A / B`.
- **Eval 2 (`ats-manual-translation-track2`)**: `with_skill` delivered `Open Transition (BBM)` / `Closed Transition (MBB)` and explicitly flagged timing figures as unverified datasheet characteristics; `without_skill` omitted `Open Transition` / `Closed Transition` head terms and omitted the datasheet-verification caveat.
- **Eval 3 (`en-to-zh-datasheet-backtranslation`)**: `with_skill` landed directly on `塑壳断路器`, preserved `kA rms` / `kA peak` / `V AC` verbatim, and flagged the `Category A` vs `Isd` contradiction + missing `Icw`; `without_skill` translated the heading as `塑料外壳式断路器` and rewrote units into Chinese (`有效值`, `峰值`, `AC 800 V`).
- **Eval 4 (`mccb-iec60947-2-2024-annexes-translation`)**: `with_skill` achieved 100% accuracy across Annexes A/B/D/H/K/L/P with strict IEC British spelling (`utilisation`, `aluminium`, `colour`, `withdrawable`, `moulded-case circuit-breaker`) and verified Ed. 6.0 clauses (`D.8.5`, `L.4.1`, `B.4.1.3`, `H.2–H.5`, `9.3.10`, `P.8.3.9`); `without_skill` leaked US `utilization`, missed `Annex D` entirely (hallucinating `Cl. 8.1.7` terminals and non-existent `Cl. 9.2.4`), mislabelled `Annex A` as Informative, and omitted Annex P subclauses and Test Sequence VII.
