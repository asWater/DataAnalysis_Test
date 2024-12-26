import matplotlib.pyplot as plt
import seaborn as sns

# Data
data = [1, 2, 2, 3, 3, 3, 4, 4, 5]

# Creating a histgram
sns.histplot(data, bins=5, kde=True)

# Showing the plot
plt.show()