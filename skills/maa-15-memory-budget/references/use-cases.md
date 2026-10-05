# Use cases

## Worked example

At budget 6, review-v2 and summary fit exactly and contribute value 11. Old-review is excluded because its authority belongs to v1, despite its declared value 100 and low token cost. Its timestamp is fresh; freshness alone is therefore insufficient.

Original action values [4,6] and compressed values [3,5] both prefer action 1. With changed budget 2, only summary is retrieved, giving value 3. Changed compressed values [6,5] prefer action 0, so compression no longer preserves the decision. That flag concerns this supplied value comparison; it does not infer which memory sentence caused the reversal.

## Changed assumption

Additive record values can overcount redundant memories. Two records that repeat the same fact may contribute less together than the sum of their isolated values. This implementation declares additivity rather than inventing a submodular or semantic model. If redundancy matters, provide a different valuation experiment.

The authority boundary is equally important. A remembered instruction does not become authorized because it is recent, highly ranked, or compressed into a confident summary. Version checks preserve a limited current-state contract; broader permissions still need a live authority check.

Compression can also preserve today's action while destroying tomorrow's distinction. The argmax diagnostic is task-relative. Test novel decisions and changed state before claiming sufficient memory. Keep excluded-record reasons in the report so token scarcity is not mistaken for intentional retention of unsafe evidence.

## New inputs

The transfer case excludes expired even though it is cheap and valuable. Current is fresh, version-valid, and consumes the full budget 3, so it is selected with value 4. Both supplied decision vectors prefer action 0, preserving this action under compression.

To apply this to your own system, attach timestamps and document versions to records when those affect authority. Give decision values an explicit source, such as a constructed study or measured task benefit. A retrieval recommendation should name records to retain, records to exclude, and the evidence needed to justify their values. Use separate trace analysis when memory is trying to promote untrusted data into control.

## Acceptance invariants

- Selected token cost never exceeds budget.
- Invalid authority is never selected.
- Changed compression reverses argmax.
