# Method

Let total arrival rate be lambda and delegated fraction f. Effective review arrival is lambda_review=lambda f. Under an M/M/1 construction with service rate mu, the queue is stable when lambda_review<mu. Mean system time, including service, is W=1/(mu-lambda_review). At or above capacity no finite stationary mean exists, so the output remains unavailable.

A task requires delegation when the agent lacks authority or its declared risk exceeds the autonomous threshold. In this simplified contract, autonomous release requires current agent authority and acceptable risk. Delegated release requires human authority, a received review, and a mean-time diagnostic that does not exceed the task deadline.

The last predicate is deliberately a planning convention, not a pathwise guarantee. Queue mean W is not a measured duration for an individual task. A receipt may in reality arrive earlier or later. The returned flag identifies incompatibility between the declared capacity plan and deadline, and should not be mistaken for evidence that a specific observed review was late.

Supply arrival and service rates in the same time unit, delegated fraction, risk threshold, and task rows. Exact booleans distinguish current agent authority, human authority, and review receipt. Validation requires positive service rate, valid probabilities, and nonnegative deadlines.

The function calculates effective load, stability, and mean sojourn when available. It then emits delegation-required, queue-mean-exceeds-deadline, release, and review-packet-required flags for each task. The sensitivity figure varies review arrivals below service capacity and shows how mean time grows near saturation. In the changed case increase the delegated fraction while preserving total arrivals and service rate. Predict which releases the capacity contract will block.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
