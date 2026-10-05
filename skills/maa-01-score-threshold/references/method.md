# Method

Let s(x) be a supplied continuous score at scale x. The thresholded score is B_tau(x)=1{s(x)>=tau}. A discontinuity in B_tau can occur whenever s crosses tau, even if s itself has no sharp change. This construction is a property of the measurement rule. It does not require a discontinuity inside the model.

Adjacent raw-score slopes are [s(x_i)-s(x_(i-1))]/[x_i-x_(i-1)]. They have score-per-scale units, so the scale definition matters. Replacing model size with its logarithm would change their numerical meaning. The implementation requires strictly increasing scales to keep these slopes defined and aligned.

Crossing count measures adjacent changes in the binary score, including downward crossings. It is not a statistical test for emergence. With only a handful of supplied points, many different underlying functions could interpolate the observations. A useful evaluation contract therefore declares the task, scoring rule, scale variable, environment, and uncertainty before attaching a mechanism label.

Provide aligned lists of increasing scales and scores between zero and one. Set the threshold separately. Validation rejects a repeated scale, mismatched vector lengths, nonfinite values, and a cutoff outside the score domain. The function calculates the pass flags, adjacent raw slopes, and number of binary crossings.

The two figures share scale on the horizontal axis. The continuous chart shows score movement; the binary chart shows the measurement transformation. Compare their shapes before making any claim about new ability. In the changed case only the threshold moves from 0.5 to 0.55. The scores and scale values remain fixed. That choice isolates a measurement intervention from a model intervention. The returned interpretation keeps this distinction explicit.

## Apply this to an agent

Treat a benchmark pass flag as one measurement of a specified agent procedure. Hold its tools, permissions, budget and success rule fixed before comparing scales. A threshold crossing alone cannot show that the procedure acquired a new mechanism.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
