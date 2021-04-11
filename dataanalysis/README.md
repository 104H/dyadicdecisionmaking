# Data Analysis

## Visualizations
1. Distribution of Response Times
2. Line graph of Response Time in a sequence of trials separated by observation/action, being correct in detecting a signal, the correct answer
3. Distribution of Response Time when Correct and not
4. Probability of same response as dyad's response in the previous trial.
5. Probability of same response as one's own response in the previous trial.
6. Histogram of Response Times separated by Previous Condition, Current Condition and the Presence of a Signal. _Condition_ is the state of observing or acting
7. Sequence plot of response times throughout a trial
8. Histogram of Response Time faceted by how long a subject has been _acting_ (and not observing)
9. Scatter plot of Response Time against difference between the titration threshold of the two subjects

## Frequentist Hypothesis
1.

## Bayesian Hypothesis
1. Difference between Response Time based on how long a subject has been in the _acting_ condition

## Drift diffusion model
Following Urai et al. (2019), from the collected choices and response times of the participants, estimate the following parameters:

* non-decision time (the time needed for sensory encoding and response execution)
* starting point of the decision variable
* separation of the decision bounds
* mean drift rate
* drift criterion (a stimulus-independent constant added to the mean drift), cf. Ratcliff and McKoon (2008). Note: Urai et al. 2019 call this parameter "drift bias."

Let drift criterion (drift bias), starting point bias or both to vary as a function of previous choice (made either by oneself or by the second participant)

## References
* Urai et al. eLife 2019. DOI: <https://doi.org/10.7554/eLife.46331>
* Ratcliff and McKoon 2008. The diffusion decision model: theory and data for two-choice decision tasks. Neural Computation **20**:873–922. DOI: <https://doi.org/10.1162/neco.2008.12-06-420>
