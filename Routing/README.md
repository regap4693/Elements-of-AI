Besides baseball, McDonald's, and reality TV, few things are as canonically American as hopping in the car
for an old-fashioned road trip. We've prepared a dataset of major highway segments of the United States
(and parts of southern Canada and northern Mexico), including highway names, distances, and speed limits;
you can visualize this as a graph with nodes as towns and highway segments as edges. We've also prepared
a dataset of cities and towns with corresponding latitude-longitude positions. These les should be in the
GitHub repo you cloned in step 0. Your job is to implement algorithms that nd good driving directions
between pairs of cities given by the user. Your program should be run on the command line like this:
./route.py [start-city] [end-city] [routing-algorithm] [cost-function]
where:
 start-city and end-city are the cities we need a route between.
 routing-algorithm is one of:
{ bfs uses breadth-rst search (which ignores edge weights in the state graph)
{ uniform is uniform cost search (the variant of bfs that takes edge weights into consideration)
{ dfs uses depth-rst search
{ ids uses iterative deepening search
{ astar uses A* search, with a suitable heuristic function
 cost-function is one of:
{ segments tries to nd a route with the fewest number of \turns" (i.e. edges of the graph)
{ distance tries to nd a route with the shortest total distance
{ time tries to nd the fastest route, for a car that always travels at the speed limit
The output of your program should be a nicely-formatted, human-readable list of directions, including travel
times, distances, intermediate cities, and highway names, similar to what Google Maps or another site might
produce. In addition, the last line of output should have the following machine-readable output about the
route your code found:
[optimal?] [total-distance-in-miles] [total-time-in-hours] [start-city] [city-1] [city-2] ... [end-city]
The rst item on the line, [optimal?], should be either yes or no to indicate whether the program can guar-
antee that the solution found is one with the lowest cost. The reason for this ag is that some combinations
of algorithms and cost functions may not guarantee optimality; for example BFS with the segments cost
function will give an optimal answer, but BFS with distance cost function does not. Make sure that A*'s
3
optimality can always be guaranteed (by designing admissible (and potentially also consistent) heuristics for
each cost-function).
Please be careful to follow these interface requirements so that we can test your code properly. For instance,
the last line of output might be:
no 51 1.0795 Bloomington,_Indiana Martinsville,_Indiana Jct_I-465_&_IN_37_S,_Indiana Indianapolis,_Indiana

Like any real-world dataset, our road network has mistakes and inconsistencies; in the example above, for
example, the third city visited is a highway intersection instead of the name of a town. Some of these \towns"
will not have latitude-longitude coordinates in the cities dataset; you should design your code to still work
well in the face of these problems.
In the comment section at the top of your code le, remember to explain your search abstraction (as described
above under What to Do). Be sure to explain the heuristic functions you chose, and why you chose them.
Hints: This problem involves implementing three cost functions and 5 algorithms, so you could solve it by
writing 3  5 = 15 dierent functions. But this is a bad idea! You'll do a lot more work, and it will be hard
to debug and test all of that code. Instead, think about writing your algorithm functions so that they can
handle any of the cost functions; that means you'll need to write just 3+5 = 8 functions instead of 15. Also,
many of the algorithms are very similar; BFS, DFS, uniform and A* are almost the same, but with slightly
dierent uses of data structures. Use this to your advantage to save yourself work!