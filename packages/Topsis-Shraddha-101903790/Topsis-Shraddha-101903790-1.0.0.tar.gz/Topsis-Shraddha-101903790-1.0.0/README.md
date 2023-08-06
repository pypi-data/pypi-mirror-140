TOPSIS, known as Technique for Order of Preference by Similarity to Ideal Solution, is a multi-criteria decision analysis method. It compares a set of alternatives based on a pre-specified criterion. The method is used in the business across various industries, every time we need to make an analytical decision based on collected data.
What does it really mean?
Let’s imagine the situation when we want to compare several companies and find out which one has the strongest financials. These companies are our alternatives set. To combine them together and decide which one is the strongest, we need to employ some reliable metrics. In such a case we can use some indicators derived from financial statements like for example ROA (return on assets), ROE (return on equity), DR (debt ratio), or CG (capital gearing). These indicators will form our criteria set.
The mysterious logic of TOPSIS is based on the concept that the chosen alternative should have the shortest geometric distance from the best solution and the longest geometric distance from the worst solution. Pretty simple huh?
Such methodology allows finding trade-offs between criteria when a poor performance in one can be canceled by a good performance in another criterion. This provides a pretty comprehensive form of modeling because we are not excluding alternative solutions based on pre-defined thresholds.
TOPSIS algorithm
Generally, the whole TOPSIS process can be encapsulated in 7 steps:
1.
Create a matrix consisting of M alternatives and N criteria. This matrix is usually called an “evaluation matrix”.

As an example: M will be the number of our companies, while N, the number of metrics (ROA, ROE, DR, CG).
2.
Normalize evaluation matrix:

Each metric j for each company i is normalized to be in between 0 and 1. The higher its value the better the metric.
3.
Calculate the weighted normalized decision matrix. It is important to note that each criterion should have its own weight so that all of them will sum up to 1. The weights can be derived randomly (not recommended) or based on expert knowledge (industry standard).

After we assign a weight to each financial metric, we need to normalize those so that these sum up to 1. Then we need to multiply each normalized metric from step 2 by corresponding normalized weight.
4.
Determine the best and the worst alternative for each criterion:

We want to find the maximum and minimum value of each financial metric among all companies.
5.
Calculate the Euclidean distance between the target alternative and the best/worst alternative:

This is a calculation of the geometric distance between the value of each financial metric for a given company i and the best/worst value of such a metric among all companies.
6.
For each alternative calculate the similarity to the worst alternative. The results are our TOPSIS scores.

We compute a score for each company that is based on distances obtained in a step before.
7.
Rank alternatives according to the TOPSIS score by descending order.
The company with metrics closest to the best will obtain the highest score and therefore will be at the top of our ranking.
And… that’s all. We obtained a ranked set of alternatives based on specified criteria!