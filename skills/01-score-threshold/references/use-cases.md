# Use cases

## Worked example

At threshold 0.5, the default flags are 0,0,0,1,1. There is one crossing between scales 3 and 4. The raw scores rise by only a few hundredths at each interval, and the largest adjacent slope is 0.04 score units per scale unit.

At threshold 0.55, the flags become 0,0,0,0,1. The location of the apparent skill arrival moves to the last observation without changing a single score. The binary jump is real as a reported measurement. The unsupported inference would be that it identifies a sudden internal mechanism or a universal capability boundary.

## Changed assumption

A threshold diagnostic can fail through overinterpretation even when its arithmetic is correct. The raw curve might conceal a genuinely sharp change between sampled scales, or the score might be a noisy estimate with a broad uncertainty interval. This notebook does not settle either possibility because it receives no replicate measurements and fits no mechanism model.

A second failure comes from comparing scores produced under different tasks or environments. A larger score can result from an easier prompt, a changed tool interface, or a more forgiving evaluator. Those changes need separate records. The computation validates numeric alignment, but it cannot verify that the rows share a scientific contract. Keep the source of every score beside the figure and use a matched experiment to isolate the part of the assembled system being changed.

## New inputs

The transfer data uses a wider scale range and stronger raw-score movement. Its cutoff of 0.7 produces a pass only at the final point. Calculate the adjacent slopes with their unequal scale intervals before describing the curve. A score increase of 0.3 over 20 scale units is not the same local rate as an increase of 0.2 over 40 units.

For local data, retain the original continuous outcome wherever possible. If only pass/fail results were saved, record that loss of information rather than reconstructing an invented smooth curve. The next useful measurement is the pre-threshold score or a set of outcomes under several declared cutoffs.

## Acceptance invariants

- Default crossing occurs at scale 4.
- Changed cutoff moves crossing to scale 5.
- Repeated scales are rejected.
