import matplotlib.pyplot as plt

import BruteForce
import TreeContainment
import TreeDecomposition
import networkx as nx
import time
import ast
import seaborn as sns
import numpy as np

# Choose algorithm from ["path", "tree", "bruteforce"]
# algorithm = "bruteforce"
# test_set_name = "TestSetRange100Randomized"
# test_folder_name in ["TestSet4ConstantTreewidth_True", "TestSet5Ratio_True"]
test_folder_name = "TestSet5Ratio_True"
test_set_names = ["hits_and_misses_brute_force", "hits_and_misses_tc_brute_force", "hits_and_misses_tree", "hits_and_misses_path"]
# test_set_names = ["hits_and_misses_brute_force", "hits_and_misses_tc_brute_force"]

# test_set_names = ["hits_and_misses_brute_force", "hits_and_misses_tc_brute_force", "hits_and_misses_tc_brute_force_old"]

expected_result = "True"
# test_set_type = ["ratio", "constant_reticulations", "constant_leaves"]
test_set_type = "ratio"
plotted_stuff = []
sns.color_palette()
legend_names = ["Brute Force", "BOTCH", "TWITCH", "PITCH"]
xvalues = []
yvalues = []

fig = plt.figure()
ax1 = fig.add_subplot(111)
zvalues = []

for count, file_name in enumerate(test_set_names):
    print(f"file_name = {file_name}")
    xvalues.append([])
    yvalues.append([])
    xvalues[count] = []
    yvalues[count] = []

    try:
        file = open(test_folder_name + "\\" + file_name + ".txt", "r")

        file_content = file.read()
        file_content = file_content.split("\n")
        file.close()
    except:
        print(f"did not find {file_name}")
        continue


    # Remove annoying front/end stuff
    if file_content[-1] == "":
        file_content.pop()

    if file_name == "hits_and_misses_tc_brute_force":
        file_content = [file_content[0], file_content[-1]]


    for line in file_content:
        line_split = line.split(";")
        if line_split[3] != expected_result:
            print(f"WARNING: Wrong result in line {line_split[0]}")
        if test_set_type == "ratio":
            xvalues[count].append(ast.literal_eval(line_split[1]))
            if count == 1:
                zvalues.append(ast.literal_eval(line_split[2]))

        elif test_set_type == "constant_reticulations":
            xvalues[count].append(ast.literal_eval(line_split[1]))

        elif test_set_type == "constant_leaves":
            xvalues[count].append(ast.literal_eval(line_split[2]))

        yvalues[count].append(ast.literal_eval(line_split[4]))
        print(line_split)

    # print(ast.literal_eval(file_content[0]))
    #
    # xvalues = [ast.literal_eval(line[2]) for line in file_content]

    # print(xvalues)
    # colorvar = ['red', 'blue', 'green', 'yellow', 'purple'][count]
    plotted_stuff.append(legend_names[count])
    # plt.plot(xvalues, yvalues, 'bo', color=colorvar, markersize=5)
    # plt.plot(xvalues, yvalues, 'bo', markersize=5)
    sns.scatterplot(x=xvalues[count], y=yvalues[count], color=sns.color_palette()[count])
    # ax1.scatter(xvalues[count], yvalues[count], color=sns.color_palette()[count])
if test_set_type == "ratio":
    plt.xlabel('leaves')
if test_set_type == "constant_reticulations":
    plt.xlabel('leaves')
if test_set_type == "constant_leaves":
    plt.xlabel('reticulations')

# title = "Speed:"
# plt.title(title)
plt.legend(plotted_stuff)
for count, file_name in enumerate(test_set_names):
    if not xvalues[count]:
        plt.scatter(0, y=3600, marker="x", color=sns.color_palette()[count])
    else:
        if xvalues[count][-1] not in [99, 100]:
            if file_name == "hits_and_misses_path":
                continue
            plt.scatter(xvalues[count][-1] + 1, y=3600, marker="x", color=sns.color_palette()[count])
        # Manual point add:
        # if file_name == "hits_and_misses_path":
        #     plt.scatter(6, y=3600, marker="x", color=sns.color_palette()[count])


if test_set_type == "ratio":
    ax2 = ax1.twiny()
    ax2.scatter((zvalues[0], zvalues[-1]), (100, 100), 0)
    # ax2.cla()
    print(zvalues)
    ax2.set_xlabel('reticulations')


plt.ylabel('time(s)')
plt.ylim((0.0007, 4400))
plt.yscale('log')

plt.show()

