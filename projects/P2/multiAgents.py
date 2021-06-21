import random
import util

from game import Agent
from util import manhattanDistance


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"
        # print(legalMoves[chosenIndex],'\n')
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        # newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        ghost_dists = []
        for ghost in newGhostStates:
            if ghost.scaredTimer == 0:
                ghost_dists.append(manhattanDistance(newPos, ghost.getPosition()))
        if len(ghost_dists) == 0 or min(ghost_dists) == 0:
            ghostScore = 1
        else:
            ghostScore = 1 / min(ghost_dists)

        foodScore = 0
        num_food = newFood.count()
        if num_food != 0:
            min_food_dist = min([manhattanDistance(newPos, foodPos) for foodPos in newFood.asList()])
            foodScore = 1 / min_food_dist
        # print(action, foodScore, ghostScore, foodScore + ghostScore)
        return foodScore - ghostScore + successorGameState.getScore()


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        legalMoves = gameState.getLegalActions()
        scores = [self.minimax_evaluation(gameState.generateSuccessor(0, action), 1, self.depth) for action in
                  legalMoves]
        return legalMoves[scores.index(max(scores))]
        # util.raiseNotDefined()

    def minimax_evaluation(self, gameState_curr, agentIndex, depth):
        # check if game ends or depth to expand is 0
        if gameState_curr.isWin() or gameState_curr.isLose() or depth == 0:
            return self.evaluationFunction(gameState_curr)
        # for given agent, get its possible actions' scores
        legalMoves = gameState_curr.getLegalActions(agentIndex)
        # next agent to deal with
        new_agentIndex = (agentIndex + 1) % gameState_curr.getNumAgents()
        # update depth
        if new_agentIndex == 0:
            depth -= 1
        # generate scores[]
        scores = [self.minimax_evaluation(gameState_curr.generateSuccessor(agentIndex, action), new_agentIndex, depth)
                  for action in legalMoves]
        # return rslt
        if agentIndex == 0:
            return max(scores)
        return min(scores)


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        legalMoves = gameState.getLegalActions()
        value = alpha = -99999999
        beta = 99999999
        opti_Action = legalMoves[0]
        for action in legalMoves:
            value_curr = self.AlphaBeta_evaluation(gameState.generateSuccessor(0, action), 1, self.depth, alpha, beta)
            if value_curr > value:
                opti_Action = action
                value = value_curr
            alpha = max(alpha, value)
        return opti_Action

    # return minimax value of given state with AlphaBeta pruning
    def AlphaBeta_evaluation(self, gameState_curr, agentIndex, depth, alpha, beta):
        # check if game ends or depth to expand is 0
        if gameState_curr.isWin() or gameState_curr.isLose() or depth == 0:
            return self.evaluationFunction(gameState_curr)
        # for given agent, get its possible actions' scores
        legalMoves = gameState_curr.getLegalActions(agentIndex)
        new_agentIndex = (agentIndex + 1) % gameState_curr.getNumAgents()
        if new_agentIndex == 0:
            depth -= 1
        if agentIndex == 0:
            value = -99999999
            for action in legalMoves:
                value = max(value,
                            self.AlphaBeta_evaluation(gameState_curr.generateSuccessor(0, action), 1, depth, alpha,
                                                      beta))
                if value > beta:
                    return value
                alpha = max(alpha, value)
        else:
            value = 99999999
            for action in legalMoves:
                value = min(value, self.AlphaBeta_evaluation(gameState_curr.generateSuccessor(agentIndex, action),
                                                             new_agentIndex, depth, alpha, beta))
                if value < alpha:
                    return value
                beta = min(beta, value)
        return value


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        legalMoves = gameState.getLegalActions()
        scores = [self.Expectimax_evaluation(gameState.generateSuccessor(0, action), 1, self.depth) for action in
                  legalMoves]
        return legalMoves[scores.index(max(scores))]

    def Expectimax_evaluation(self, gameState_curr, agentIndex, depth):
        # print("Expectimax_evaluation!!!")
        # check if game ends or depth to expand is 0
        if gameState_curr.isWin() or gameState_curr.isLose() or depth == 0:
            return self.evaluationFunction(gameState_curr)
        legalMoves = gameState_curr.getLegalActions(agentIndex)
        new_agentIndex = (agentIndex + 1) % gameState_curr.getNumAgents()
        if new_agentIndex == 0:
            depth -= 1
        scores = [
            self.Expectimax_evaluation(gameState_curr.generateSuccessor(agentIndex, action), new_agentIndex, depth) for
            action in legalMoves]
        if agentIndex == 0:
            return max(scores)
        return sum(scores) / len(scores)


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    pac_pos = currentGameState.getPacmanPosition()

    # part 1: manhattanDistance to the closest food
    food = currentGameState.getFood()
    foods_Pos = food.asList()
    food_dists = [manhattanDistance(pac_pos, food_Pos) for food_Pos in foods_Pos]
    min_food_dist = 0
    if len(food_dists) != 0:
        min_food_dist = min(food_dists)

    # part 2: num of remain foods
    food_count = currentGameState.getNumFood()

    # part 3: manhattanDistance to the closest normal ghost
    ghost_States = currentGameState.getGhostStates()
    normal_ghost = [ghost for ghost in ghost_States if ghost.scaredTimer == 0]
    normal_ghost_dists = [manhattanDistance(pac_pos, ghost.getPosition()) for ghost in normal_ghost]
    min_normal_ghost_dist = 30
    if len(normal_ghost_dists) != 0:
        min_normal_ghost_dist = min(normal_ghost_dists)

    # part 4: number & manhattanDistance to the closest frightened ghost
    frightened_ghost = [ghost for ghost in ghost_States if ghost.scaredTimer != 0]
    num_frightened_ghost = len(frightened_ghost)
    frightened_ghost_dists = [manhattanDistance(pac_pos, ghost.getPosition()) for ghost in frightened_ghost]
    min_frightened_ghost_dist = 0
    if len(frightened_ghost_dists) != 0:
        min_frightened_ghost_dist = min(frightened_ghost_dists)

    current_GameScore = currentGameState.getScore()
    num_capsules = len(currentGameState.getCapsules())
    # print("min_food_dist", - 2 * min_food_dist, "food_count", - 30 * food_count, "min_frightened_ghost_dist",
    #       "min_frightened_ghost_dist", - min_frightened_ghost_dist, "min_normal_ghost_dist", + min_normal_ghost_dist,
    #       "num_frightened_ghost", + num_frightened_ghost, "current_GameScore", - current_GameScore)
    return - 1.01 * min_food_dist - 15 * food_count - 3 * min_frightened_ghost_dist - 30 * num_capsules + min_normal_ghost_dist + num_frightened_ghost + current_GameScore


# Abbreviation
better = betterEvaluationFunction
