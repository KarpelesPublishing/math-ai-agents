# Use cases

## Worked example

Without the shortcut, default total time is 1(0.5+1)=1.5. With a zero-cost shortcut, equilibrium sends all demand through it, giving path time 2 and total time 2. The social optimum uses no shortcut and remains at 1.5. Price of anarchy is 2/1.5=4/3.

A toll 0.5 changes the equilibrium shortcut flow to zero. Outer private time is 1.5, while an unused shortcut would also cost 1.5 including toll. Total travel time returns to 1.5. The toll affects incentives; it is not counted as destroyed travel time or an extra physical delay.

The toll 0.5 sits exactly at the break-even value, so this teaching case is knife-edge. At toll 0.49 the lab returns shortcut flow 0.02 and equilibrium social time 1.5002, and at 0.51 it returns flow 0 and time 1.5. Try nearby tolls to see the threshold rather than reading 0.5 as a robust remedy.

## Changed assumption

The paradox relies on a particular network and demand regime. At low demand, the shortcut can be socially useful and privately efficient. Presenting the default construction as a law against connectivity would erase those conditions.

Institutional metrics can also confuse transfers with resource costs. A toll payment changes who bears money but is excluded from this travel-time objective. A real institution may care about distributional effects or administrative overhead, which should be modeled separately. Shortcut overhead here is a real delay and therefore enters social cost.

Continuous equilibrium assumes many small participants choosing minimum private cost. A small team with indivisible jobs, strategic coordination, or centralized routing may behave differently. The calculation is an exact finite model result under those assumptions, not a fitted causal claim about organizational performance.

## New inputs

At demand 0.5, capacity 1, and constant delay 1, equilibrium sends all flow through the shortcut. Its total time is 0.5, below the no-shortcut total 0.625. The social optimum also uses shortcut flow 0.5, so price of anarchy is 1.

For workflow analysis, identify who selects routes and which costs they internalize. Separate routing overhead from incentive charges and preserve demand units. Compare local choice with a collective objective before adding a new interface. If route delays are estimated, collect measurements under several loads rather than assuming a linear congestion law.

## Acceptance invariants

- Default shortcut worsens 1.5 to 2.
- Toll 0.5 restores total 1.5.
- Low demand transfer optimum uses full shortcut.
