# Method

Let total demand be D. Symmetry assigns x to each outer route and z to the shortcut, so 2x+z=D. Each congestible edge carries x+z and takes time v=(x+z)/capacity. Outer path time is v+c; shortcut time is 2v+overhead. The shortcut also pays a private toll.

At an interior equilibrium, used routes have equal private cost. Solving v+c=2v+overhead+toll gives z=2 capacity(c-overhead-toll)-D, clipped to [0,D]. Boundary clipping handles unused outer or shortcut routes. Without the shortcut, outer flow is D/2 and total travel time is D[D/(2 capacity)+c].

Social travel time excludes toll transfers and equals 2x(v+c)+z(2v+overhead). After substitution it is (D+z)^2/(2 capacity)+c(D-z)+overhead*z. This convex quadratic is minimized at z=capacity(c-overhead)-D, clipped to [0,D]. The price of anarchy compares equilibrium social time with that minimum, not with toll-inclusive private expense.

Declare demand, congestion capacity, outer constant delay, shortcut overhead, and toll. Validation requires positive demand and capacity and nonnegative other quantities. The function computes symmetric equilibrium flow, path costs, total delay, optimal shortcut flow, and toll revenue.

The figure varies shortcut flow from zero to total demand and plots exact social travel time. Its minimum should match the reported optimum. In the changed case add toll 0.5 without changing physical travel times. Predict how it shifts equilibrium, then compare social cost. The transfer case reduces demand, checking that a shortcut need not worsen performance under every loading condition.

## Apply this to an agent

Adding a route or worker can change the incentives of every participant. Compare private routing choices with total workflow cost before assuming that another available path improves the agent team. The network is a declared construction, not a measured deployment.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
