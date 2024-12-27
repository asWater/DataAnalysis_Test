import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

DATA_FILE = 'data/smon.tsv'

# Reference of pandas.read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
# SMON TSV File: 
# (First number: 0)
# > Column Titles: Row 2
# > Column Starts: Col 1
# > Total columns number: 31
# > Data Starts: Row 4
df = pd.read_csv(DATA_FILE, skiprows=2, header=0, usecols=range(1,32), skip_blank_lines=True, sep='\t')

print(df.head())
print(df.info())
#print(df.describe())
#print("CPU User Average: ", df['CPU Usr'].mean())
#print("CPU System Average: ", df['CPU Sys'].mean())

#df_cpu = pd.DataFrame(data=df, columns=[ df["Time"].name, df["AS Instance"].name, df["CPU Usr"].name, df["CPU Sys"].name ])

# To show some graphs(axes) in a figure
# (In this case, Rows:2, Cols: 2)
fig = plt.figure(facecolor="white", tight_layout=True)
fig.set_size_inches(18.5, 10.5)
gs = fig.add_gridspec(2, 3)

# Graph (Axes) definitions
ax_r1_box = fig.add_subplot(gs[0, 0], facecolor="white")
ax_r1_line = fig.add_subplot(gs[0, 1:3], facecolor="white")
ax_r2_box = fig.add_subplot(gs[1, 0], facecolor="white")
ax_r2_line = fig.add_subplot(gs[1, 1:3], facecolor="white")

#----------------------------------------
# Boxplot
#----------------------------------------
sns.boxplot( data=df, x="AS Instance", y="CPU Usr", ax=ax_r1_box )
sns.boxplot( data=df, x="AS Instance", y="CPU Sys", ax=ax_r2_box )

# Changing the angle of X label
#plt.setp( plt.gca().get_xticklabels(), rotation=90 )
ax_r1_box.set_xticklabels(ax_r1_box.get_xticklabels(), rotation=90)
ax_r2_box.set_xticklabels(ax_r1_box.get_xticklabels(), rotation=90)

#----------------------------------------
# Lineplot
#----------------------------------------
sns.lineplot( data=df, x="Time", y="CPU Usr", hue="AS Instance", ax=ax_r1_line )
sns.lineplot( data=df, x="Time", y="CPU Sys", hue="AS Instance", ax=ax_r2_line )

# Setting the distance of lable in X-Axis
#plt.gca().xaxis.set_major_locator( ticker.MultipleLocator(10) )
ax_r1_line.xaxis.set_major_locator( ticker.MultipleLocator(5) )
ax_r2_line.xaxis.set_major_locator( ticker.MultipleLocator(5) )

#plt.setp( plt.gca().get_xticklabels(), rotation=90 )
ax_r1_line.set_xticklabels( ax_r1_line.get_xticklabels(), rotation=90 )
ax_r2_line.set_xticklabels( ax_r1_line.get_xticklabels(), rotation=90 )

ax_r1_line.legend( fontsize=8 )
ax_r2_line.legend( fontsize=8 )

# Plots created using seaborn need to be displayed like ordinary matplotlib plots. 
plt.show()