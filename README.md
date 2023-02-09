Welcome to my master's thesis code. 

Link to the thesis: http://resolver.tudelft.nl/uuid:3906ebda-d667-4d3e-8bee-3f1f4df78387

Here is a description of what everything does:

MAIN STUFF:
- Main.py: Can be used to launch PITCH, TWITCH, BOTCH and Brute Force on test sets. 
- TreeContainment.py: Contains the framework of TWITCH and PITCH. Also has commented debugging tools for these algorithms. 
- BOTCH.py: Contains BOTCH (the main function is called tc_brute_force()). Also contains the cherry-picking algorithm (main function is tcn_contains())
- BruteForce.py: Contains the brute force implementation. 
- TreeDecomposition.py: Contains my implementations for creating (nice) tree decompositions.
- TreeContainmentTestGeneration.py: Can be used to generate all sorts of test cases. Contains the algorithms for generating random networks and trees. 

IMPORTANT FUNCTIONS:
- JoinNode.py: Contains the code used for join bags. Contains some outdated code for attempts at getting super-compactness to work with join bags (two_long_pathing and others). 
- IntroduceNode.py: Contains the code used for introduce bags. Read at your own risk. 
- TreeContainmentCheck.py: Contains all signature filters
- NetworkIsomorphismTools.py: Contains the isomorphism filter (isomorphism_checker6) and the isomorphism check without iso-labellings that is used in join bags (isomorphism_checker7). 

DEBUGGING TOOLS:
- TreeContainmentTools.py: Contains 2 tools, most importantly the signature_image function that visualizes signatures. 

GRAPHIC TOOLS: 
- SignatureDrawing.py: Can be used to manually draw signatures and display graphs
- GraphGeneration.py: Contains tools for making plots of testcases. 
- FlowChartDraw.py: Contains code that makes a certain flow charts using graphviz. 
- DefinitionNetwork.py: Contains code that makes a certain graph of definitions. 

DEPENDANCIES:
- NetworkxTreeIsomorphism.py: Code from networkx that is used in BruteForce.py. This is included here since I couldn't get it to work using the networkx package without manually copying code. 
- TreewidthHeuristics.py: Old code from networkx that might be used somewhere. 
- IsomorphismCheckSource.py: Old code from networkx that might be used somewhere. 

SAGE:
There is also code that was written in Sage. The sage code can import the .txt files generated by the TreeContainmentTestGeneration.py and create path-decompositions of the graphs using a Sage function. It then exports those in the form of .txt files again. .
This Sage code can also do the comparison checks between the treewidth of the display graph and the treewidth of the network. This part is commented. 
This code is included in the .txt file that can be copied into Sage. This can be done without installing Sage, by using https://cocalc.com/ for example.

To whoever reads this, I hope this has been useful.  

Sincerely, 
Robbert V. Huijsman
