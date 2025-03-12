
from pacai.agents.capture.capture import CaptureAgent
from collections import Counter

def createTeam(firstIndex, secondIndex, isRed,
        first='OffensiveAgent',
        second='DefensiveAgent'):
    
    return [
        OffensiveAgent(firstIndex),
        DefensiveAgent(secondIndex),
    ]

class BaseAgent(CaptureAgent):
    
    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        return successor

    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights()
        return sum(features[feature] * weights[feature] for feature in features)

    def getWeights(self):
        return {'successorScore': 1.0}

class OffensiveAgent(BaseAgent):
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.eatenCapsule = False  # Track if Pacman has eaten a power pellet

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        if 'Stop' in actions:
            actions.remove('Stop')  # Avoid stopping
        bestAction = max(actions, key=lambda a: self.evaluate(gameState, a))
        return bestAction

    def getFeatures(self, gameState, action):
        features = Counter()
        successor = self.getSuccessor(gameState, action)
        position = successor.getAgentPosition(self.index)
        foodList = self.getFood(gameState).asList()
        capsuleList = self.getCapsules(gameState)

        # Track food distance
        if foodList:
            features['distanceToFood'] = min(self.getMazeDistance(position, food)
                                             for food in foodList)
            # Track distance to closest food
            if position in foodList:
                features['foodEaten'] = 1
            else:
                features['foodEaten'] = 0
        else:
            features['distanceToFood'] = 0

        # Track capsule distance and ensure Pacman eats it
        if capsuleList:
            closestCapsule = min(capsuleList, key=lambda c: self.getMazeDistance(position, c))
            # Get the closest capsule
            features['distanceToCapsule'] = self.getMazeDistance(position, closestCapsule)
            # Track distance to closest capsule
            if position == closestCapsule:  # Pacman has eaten a power pellet
                self.eatenCapsule = True  # Pacman just ate a power pellet
                features['capsuleEaten'] = 1  # Pacman has eaten a power pellet
            else:
                features['capsuleEaten'] = 0  # Pacman has not eaten a power pellet
        else:
            features['distanceToCapsule'] = 0  # No capsules on the board

        # Track enemy ghosts
        enemyStates = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        # Get all enemy states
        ghosts = [e for e in enemyStates if not e.isPacman() and e.getPosition() is not None]
        scaredGhosts = [g for g in ghosts if g.isScaredGhost()]  # Get all scared ghosts

        if ghosts:  # If there are ghosts on the board
            closestGhostDistance = min(self.getMazeDistance(position, g.getPosition())
                                       for g in ghosts)
            # Get the closest ghost
            features['ghostDistance'] = closestGhostDistance
            # Track the distance to the closest ghost

            # If Pacman is in attack mode, prioritize hunting **only scared ghosts**
            if self.eatenCapsule and scaredGhosts:
                closestScaredGhost = min(scaredGhosts, key=lambda g:
                                         self.getMazeDistance(position, g.getPosition()))
                features['attackGhost'] = -self.getMazeDistance(position,
                                                                closestScaredGhost.getPosition())
            else:
                if closestGhostDistance < 3:
                    features['ghostDanger'] = 1  # High danger if ghost is too close
        else:
            features['ghostDistance'] = 9999

        return features

    def getWeights(self):
        return {
            'distanceToFood': -9,  # Strong incentive to eat food
            'foodEaten': 100,  # Strong reward for eating food
            'distanceToCapsule': -15,  # Stronger incentive to eat capsules
            'capsuleEaten': 80,  # Stronger reward for eating capsules
            'ghostDistance': 2,  # Encourage avoiding ghosts
            'ghostDanger': -20,  # Strongly discourage getting too close to ghosts
            'attackGhost': 100  # Highly encourage attacking scared ghosts
        }

    #  Still need to implement the once pellot eaten, attack ghosts part, I still win
    #  against the baseine team tho
class DefensiveAgent(BaseAgent):
    
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        
        # Start in the middle of the board
        chartWidth = gameState.getInitialLayout().getWidth()
        chartHeight = gameState.getInitialLayout().getHeight()
        middleChartWidth = (chartWidth // 2) - 2 if self.red else (chartWidth // 2)
        middleChartHeight = chartHeight // 2
        
        # Move to the nearest non-wall position in the middle
        while gameState.hasWall(middleChartWidth, middleChartHeight):
            middleChartHeight -= 1
        
        self.start = (middleChartWidth, middleChartHeight)  # Set starting position in the middle
        self.targetPosition = (middleChartWidth, middleChartHeight)
        # Default to waiting in the middle

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        actions.remove('Stop')  # Avoid stopping
        
        # Track enemy Pacman invaders
        opponents = self.getOpponents(gameState)
        # Initialize an empty list to store invading opponents (Pac-Man mode)
        invaders = []

        # Iterate through all opponent agents
        for o in opponents:
            agent_state = gameState.getAgentState(o)  # Get the agent's state
            agent_position = gameState.getAgentPosition(o)  # Get the agent's position

            # Check if the opponent is in Pac-Man mode and has a known position
            if agent_state.isPacman() and agent_position is not None:
                invaders.append(o)  # Add the opponent to the invaders list
        
        if invaders:
            bestAction = max(actions, key=lambda a: self.evaluate(gameState, a))
        else:
            # If no invaders, move toward the middle of the board
            bestAction = min(actions, key=lambda a: self.getMazeDistance
                             (gameState.generateSuccessor
                              (self.index, a).getAgentPosition
                              (self.index), self.start))
        
        return bestAction

    def getFeatures(self, gameState, action):
        features = Counter()
        successor = self.getSuccessor(gameState, action)
        pos = successor.getAgentPosition(self.index)

        # Track enemy Pacman invaders
        opponents = self.getOpponents(successor)
        # Initialize an empty list to store invading opponents (those in Pac-Man mode)
        invaders = []

        # Iterate through all opponent agents
        for i in opponents:
            agent_state = successor.getAgentState(i)  # Get the agent's state
            agent_position = successor.getAgentPosition(i)  # Get the agent's position

            # Check if the opponent is in Pac-Man mode and has a known position
            if agent_state.isPacman() and agent_position is not None:
                invaders.append(i)  # Add the opponent index to the invaders list
        if invaders:
            features['invaderDistance'] = min(self.getMazeDistance
                                              (pos, successor.getAgentPosition(i))
                                              for i in invaders)

        return features

    def getWeights(self):
        return {'invaderDistance': -2}