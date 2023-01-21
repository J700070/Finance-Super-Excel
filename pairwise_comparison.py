import pandas as pd


def pairwise_comparison(my_list):
    n = len(my_list)
    # Create an empty matrix to store the scores
    scores = [[0] * n for _ in range(n)]
    # Loop through all possible pairs of elements
    for i in range(n):
        for j in range(i + 1, n):
            # If the score is already known, skip the comparison
            if scores[i][j] != 0:
                continue

            score = float(
                input(f"Score for comparison between {my_list[i]} and {my_list[j]}: ")
            )
            scores[i][j] = score
            scores[j][i] = -score

    # Convert the scores to a pandas dataframe
    scores = pd.DataFrame(scores, index=my_list, columns=my_list)

    return scores


scores = pairwise_comparison(["FB", "EVO", "APPLE", "GOOG"])
print(scores)

# Calculate the sum of scores for each row
scores["sum"] = scores.sum(axis=1)
# Sort the scores by the sum
scores = scores.sort_values(by="sum", ascending=False)
print(scores)
