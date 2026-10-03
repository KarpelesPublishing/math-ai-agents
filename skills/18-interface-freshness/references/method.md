# Method

Let age be observation age and tau the maximum permitted age. Freshness is F=1{age<=tau}. Current authorization is A. Target correctness is T=1{resolved target=wanted target}. Version validity is V=1{observed version=current version} for the version-bound interface.

For coordinate and semantic methods, issuance is F and A under this simplified contract. For version-bound action it is F and A and V. Authorized confirmed completion additionally requires target correctness and an effect-confirmation flag. Those predicates represent different evidence: an issued request can be wrong, and a correct target can still lack confirmation.

The coordinate method deliberately has no semantic identity check before issuance. The semantic method avoids the particular moved-location failure but can still resolve the wrong object. Version binding rejects a changed layout rather than guessing whether the old observation remains sufficient. Age and version are separate: a recent observation can already be obsolete, and an old observation may describe an unchanged layout.

Supply age, freshness limit, observed and current versions, current permission, effect confirmation, and target identifiers. Exact boolean checks keep authorization and confirmation distinct from truthy strings. The function emits one row per interface with freshness, version match, authorization, issuance, target correctness, and confirmed completion.

Two figures compare issued actions and confirmed completions. Their difference is operationally important; a higher issuance bar does not imply better behavior. Run the default layout-change case, then increase only observation age beyond the limit. Predict which interfaces will refuse issuance. The transfer case removes permission while preserving fresh, matching observations, checking that a stable interface cannot manufacture authority.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
