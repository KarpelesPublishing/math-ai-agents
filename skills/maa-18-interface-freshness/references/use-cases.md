# Use cases

## Worked example

The default coordinate action is issued at a fresh observation age but points to delete, so confirmed completion is false. Semantic targeting points to release and is issued, giving confirmed completion true under the supplied receipt flag. Version-bound action refuses issuance because layout-1 differs from layout-2.

In the changed case age 3 exceeds max_age 2. All interfaces refuse issuance, including the semantic one. Freshness policy changes the action set before any claim of completion. The result does not say the page was unusable; it says this declared contract requires a renewed observation before acting.

Equation 18.3 is also computed when change_rate is supplied. With rate 0.02 changes per second, delays of 5, 15 and 30 seconds give freshness probabilities 0.9048, 0.7408 and 0.5488, which reproduces the chapter's second exercise. This is a constant-rate model of how likely no invalidating change has occurred. It is reported beside the age-limit rule, not in place of it, and a bursty update pattern would make it unsuitable.

## Changed assumption

Semantic targeting is not a universal repair for computer-use errors. Labels can be duplicated, accessibility trees can be stale, and resolver rules can name the wrong object. The runtime accepts a declared semantic target so that this boundary stays visible rather than assuming semantics equals correctness.

A second failure treats historical permission as current authority. The controller must check permission at issuance, not merely remember that a similar action was allowed earlier. The transfer case blocks every method despite correct targets and matching versions.

Finally, a click receipt is not necessarily an effect receipt. This experiment's confirmation flag refers to the desired completed effect. Real interfaces may need a state query, durable operation identifier, or verification page. Do not translate a low-level input event into terminal completion without that evidence.

## New inputs

The transfer observation is fresh, versions match, and both target methods resolve submit correctly. Current permission is false, so every issuance flag is false. This is an authority boundary independent of perception accuracy.

For local use, preserve the observed target, action-time target, layout version, and timestamp. If a field is unavailable, specify the observation needed instead of guessing it. Compare interfaces under the same task and permission contract. Use uncertain-effect tracing after issuance when the real question is whether the remote action happened despite a missing acknowledgement.

## Acceptance invariants

- Wrong coordinate target never counts as completion.
- Stale observations block all methods.
- Denied permission blocks even fresh correct targets.
- Freshness probability equals exp(-rate*delay) and falls as delay grows.
