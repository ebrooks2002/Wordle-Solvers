# Wordle-Solver(s)

1) Greedy Algorithm. Average guesses: 4.7. Runtime: O(n*n), where n is the length of the "possible words" list.
2) Using letter frequency to inform our next guess. Average guesses: 4.5. Runtime O(n*n), where n is the length of the "possible words" list
3) Depth First Search Solver: Ideally O(n log n) after all the words have been added to the dictionary.
4) Entropy Based algorithm : Has exponential time complexity due to the Solve function which has to compute the entropies for all of the possible words. If however the entropies are calcuated earlier, and the solution space is continually reduced, the run time is actually much better. 
