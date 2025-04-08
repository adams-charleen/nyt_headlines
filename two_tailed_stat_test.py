import numpy as np
from scipy.stats import norm

# Step 1: Define the data
total_headlines = 915  # Total number of headlines (n)
israeli_mentions = 267  # Number of headlines mentioning Israeli terms (x_Israeli)
palestinian_mentions = 375  # Number of headlines mentioning Palestinian terms (x_Palestinian)

# Step 2: Set up the hypotheses
# Null Hypothesis (H0): p_Israeli = p_Palestinian
# Alternative Hypothesis (H1): p_Palestinian != p_Israeli (two-tailed test)

# Step 3: Calculate the proportions
p_israeli = israeli_mentions / total_headlines
p_palestinian = palestinian_mentions / total_headlines

print(f"Proportion of Israeli mentions: {p_israeli:.4f}")
print(f"Proportion of Palestinian mentions: {p_palestinian:.4f}")

# Step 4: Perform the Two-Proportion Z-Test
# Pooled proportion (p_hat)
p_hat = (israeli_mentions + palestinian_mentions) / (total_headlines + total_headlines)
print(f"Pooled proportion (p_hat): {p_hat:.4f}")

# Standard Error (SE)
se = np.sqrt(p_hat * (1 - p_hat) * (1 / total_headlines + 1 / total_headlines))
print(f"Standard Error (SE): {se:.4f}")

# Z-Statistic
z = (p_palestinian - p_israeli) / se
print(f"Z-Statistic: {z:.4f}")

# P-Value (two-tailed test)
# The two-tailed p-value is the area in both tails of the normal distribution
# Since z is positive, we calculate the area to the right and double it for both tails
p_value_one_tail = 1 - norm.cdf(z)  # Area to the right of the z-statistic
p_value_two_tail = 2 * p_value_one_tail  # Double for two-tailed test
print(f"P-Value (one-tailed): {p_value_one_tail:.6f}")
print(f"P-Value (two-tailed): {p_value_two_tail:.6f}")

# Step 5: Conclusion
alpha = 0.05  # Significance level
if p_value_two_tail < alpha:
    print(f"With a two-tailed p-value of {p_value_two_tail:.6f} < {alpha}, we reject the null hypothesis.")
    print("The difference in proportions is statistically significant.")
    print("There is a significant difference in the frequency of Palestinian vs. Israeli mentions.")
else:
    print(f"With a two-tailed p-value of {p_value_two_tail:.6f} >= {alpha}, we fail to reject the null hypothesis.")
    print("The difference in proportions is not statistically significant.")

# Additional: Mention Ratio
mention_ratio = israeli_mentions / palestinian_mentions
print(f"Mention Ratio (Israeli:Palestinian): {mention_ratio:.2f}")
print(f"For every 1 Israeli mention, there are {1/mention_ratio:.2f} Palestinian mentions.")
