"""
In this file, you will implement generic search algorithms which are called by Pacman agents.
"""
import heapq
def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first [p 85].

    Your search algorithm needs to return a list of actions that reaches the goal.
    Make sure to implement a graph search algorithm [Fig. 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:
    ```
    print("Start: %s" % (str(problem.startingState())))
    print("Is the start a goal?: %s" % (problem.isGoal(problem.startingState())))
    print("Start's successors: %s" % (problem.successorStates(problem.startingState())))
    ```
    """
    stack = [(problem.startingState(), [])]
    visited = set()
    while stack:
        state, actions = stack.pop()
        if problem.isGoal(state):
            return actions
        if state in visited:
            continue
        visited.add(state)
        for successor, action, _ in problem.successorStates(state):
            stack.append((successor, actions + [action]))
    # start with inital state
    return []
    # push state onto stack
    # pop state to exlpore successors
    # push successors onto stack
            

def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first. [p 81]
    """
    frontier = [(problem.startingState(), [])]
    visited = set()
    while frontier:
        state, actions = frontier.pop(0)
        if problem.isGoal(state):
            return actions
        if state in visited:
            continue
        visited.add(state)
        for successor, action, _ in problem.successorStates(state):
            frontier.append((successor, actions + [action]))
    return []


def uniformCostSearch(problem):
    """
    Search the node of least total cost first.
    """
    frontier = []
    heapq.heappush(frontier, (0, problem.startingState(), []))
    visited = {}
    while frontier:
        cost, state, actions = heapq.heappop(frontier)
        if problem.isGoal(state):
            return actions
        if state in visited and visited[state] <= cost:
            continue
        visited[state] = cost
        for successor, action, stepCost in problem.successorStates(state):
            heapq.heappush(frontier, (cost + stepCost, successor, actions + [action]))
    return []
def aStarSearch(problem, heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    # *** Your Code Here ***
    frontier = []
    heapq.heappush(frontier, (0 + heuristic(problem.startingState(),
            problem), 0, problem.startingState(), []))
    visited = {}
    while frontier:
        fCost, gCost, state, actions = heapq.heappop(frontier)
        if state in visited and visited[state] <= fCost:
            continue
        visited[state] = fCost
        if problem.isGoal(state):
            return actions
        for successor, action, stepCost in problem.successorStates(state):
            currGCost = gCost + stepCost
            currFCost = currGCost + heuristic(successor, problem)
            if successor not in visited or visited[successor] > currFCost:
                heapq.heappush(frontier, (currFCost, currGCost, successor, actions + [action]))
    return []
