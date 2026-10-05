# Method

The declared family is y=alpha+beta f(x), where f(x)=x for a linear fit or f(x)=log(x) for a log fit. Let z_i=f(x_i). Least squares gives beta=sum_i(z_i-z_bar)(y_i-y_bar)/sum_i(z_i-z_bar)^2 and alpha=y_bar-beta z_bar. Variation in the development scales is necessary because a zero denominator leaves the slope unidentified.

At a test scale x_j, the frozen prediction is y_hat_j=alpha+beta f(x_j). Residuals are y_j-y_hat_j, the observed value minus the frozen prediction, as in Equation (3.2). Test RMSE is sqrt(mean residual squared), while bias is the signed mean residual. RMSE measures magnitude; bias distinguishes systematic overprediction from underprediction. Neither is a probability of being correct.

The log family requires positive scales and interprets equal multiplicative scale changes as equal increments in its transformed coordinate. Family selection is part of the prospective protocol and must occur before seeing test outcomes. The software cannot verify the historical order of an external experiment, but it rejects overlapping development and test scales and never uses test y values in the fit.

Supply two aligned development vectors and two aligned test vectors. State the family explicitly. The function validates finite values, dimensional alignment, development variation, and separation of scale sets. It computes coefficients, frozen predictions, residuals, RMSE, and bias.

The forecast and unseen-observation figures share test scale and score units. The residual figure makes errors visible rather than hiding them beneath a fitted line. Run the default case, save its coefficients, and predict what will happen when only test_y changes. The coefficients must remain identical. If they move, test evidence leaked into fitting. For real data, keep a timestamped forecast artifact or preregistered protocol beside the exported result to support the prospective claim.

## Apply this to an agent

Freeze the forecast for a named agent procedure before its withheld outcomes arrive. Record the tool set, retry policy, resource allowance and scoring rule with the prediction. A better retrospective fit does not rescue a missed prospective forecast.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
