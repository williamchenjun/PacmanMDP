# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
from util import manhattanDistance

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # Default initial value
        initial = 0

        # Game Entities Positions Storage
        self.FoodPositions = []
        self.GhostPositions = []
        self.CapsulePositions = []
        self.WallPositions = []

        # Probabilities
        self.IntendedDirectionProbability = 0.8
        self.NotIntendedDirectionProbability = 0.1

        # Entity rewards
        self.FOOD_REWARD = 20
        self.GHOST_REWARD = -50
        self.GHOST_NEIGH = -25
        self.CAPSULE_REWARD = 15
        self.BLANK_REWARD = -3
        self.WALL_REWARD = -10

        # Map dimensions initialisation
        self.MapWidth = initial
        self.MapHeight = initial

    #Gets run after an MDPAgent object is created and once there is
    #game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

        # Register the dimensions of the map on start up.
        self.Corners = api.corners(state)
        self.MapHeight = max(self.Corners)[1] + 1
        self.MapWidth = max(self.Corners)[0] + 1

        # Initialise the reward dictionary.
        self.Rewards = {(x,y): self.BLANK_REWARD for x in range(self.MapWidth) for y in range(self.MapHeight)}
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        
    def __is_medium_map(self):
        """Returns `True` if the map width is more than 10px. Otherwise, it's `False`."""
        if self.MapWidth >= 10:
            return True
        return False
    
    def getFood(self, state):
        """Returns food positions."""
        return api.food(state)
    
    def getWalls(self, state):
        """Returns wall positions."""
        return api.walls(state)
    
    def getCapsules(self, state):
        """Returns capsule positions."""
        return api.capsules(state)

    def getGhosts(self, state):
        """Returns a dictionary with the ghosts' position (as tuples of integers) as key and states as key value."""
        
        temp_dict = {ghost : s for ghost, s in api.ghostStates(state)}
        ghosts = [(int(x),int(y)) for (x,y) in list(temp_dict.keys())]
        states = [s for s in list(temp_dict.values())]
        return dict(zip(ghosts, states))

    def getDangerZone(self, state, radius, AreaType = "default"):
        """
        #### Default Danger Zone
        The "default" danger zone is an area defined by a "square block" around each ghost. For example, for R = 1, we have

        ```
        XXX
        XGX
        XXX
        ```
        where `G` is the ghost's position and `X` is the danger zone. The danger zone does not interact with walls (i.e. it extends beyond them).

        ---

        #### "Cross" Danger Zone
        The "cross" danger zone is an area defined only in four directions w.r.t. the ghosts' position. For example, for R = 1, we have
        ```   
         X     
        XGX
         X  
        ```
        where `G` is the ghost's position and `X` is the danger zone.
        """

        if radius < 0:
            print "The radius of the danger zone cannot be less than 0."
            return
        
        GhostPositions = self.getGhosts(state)
        MapGrid = [(x,y) for x in range(self.MapWidth) for y in range(self.MapHeight)]
        DangerZone = []

        if AreaType.lower() == "default":
            for ghost in GhostPositions:
                for x in range(-radius, radius + 1):
                    for y in range(-radius,radius + 1):
                        DangerZone.append((int(ghost[0]+x), int(ghost[1]+y)))

            return [x for x in (set(j for j in DangerZone)) if x in MapGrid]
        
        elif AreaType.lower() == "cross":
            for ghost in GhostPositions:
                for x in range(-radius, radius + 1):
                    DangerZone.append((int(ghost[0] + x), int(ghost[1])))
                    for y in range(-radius,radius + 1):
                        DangerZone.append((int(ghost[0]), int(ghost[1]+y)))

            return [x for x in (set(j for j in DangerZone))]
        
        else:
            print "The type " + AreaType + " does not exist."
            return

    def getRewards(self, state):
        """Returns a dictionary with all the corresponding rewards for each cell of the game map."""

        self.FoodPositions = self.getFood(state)
        self.WallPositions = self.getWalls(state)
        Ghosts = self.getGhosts(state)
        self.GhostPositions = list(Ghosts.keys())
        self.CapsulePositions = self.getCapsules(state)
        self.BlankPositions = list(set(self.Rewards.keys()) - set(self.FoodPositions) - set(self.WallPositions) - set(self.GhostPositions) - set(self.CapsulePositions))
        CurrentPosition = api.whereAmI(state)
        DangerZone = []
        
        # If the map is mediumClassic, we generate a danger zone 
        # depending on the distance from each ghost.
        if self.__is_medium_map():
            radius = 3
            for ghost in Ghosts:
                if manhattanDistance(CurrentPosition, ghost) <= radius:
                    DangerZone = self.getDangerZone(state, radius)
        else:
            radius = 1
            DangerZone = self.getDangerZone(state, radius)

        # We update the rewards after each move.
        self.Rewards.update({blank : self.BLANK_REWARD for blank in self.BlankPositions})
        self.Rewards.update({food : self.FOOD_REWARD for food in self.FoodPositions})
        self.Rewards.update({capsule : self.CAPSULE_REWARD for capsule in self.CapsulePositions})
        self.Rewards.update({wall : self.WALL_REWARD for wall in self.WallPositions})

        # If not all the ghosts are edible, then we avoid them.
        # And if a danger zone has been defined, we avoid that area as well.
        if not all(ghostState == 1 for ghostState in Ghosts.values()):
            if DangerZone:
                self.Rewards.update({danger : self.GHOST_NEIGH for danger in DangerZone})
            self.Rewards.update({ghost : self.GHOST_REWARD for ghost in Ghosts})
        
        # Otherwise, we get greedy.
        else:
            if DangerZone:
                self.Rewards.update({danger : -self.GHOST_NEIGH for danger in DangerZone})
            self.Rewards.update({ghost : -self.GHOST_REWARD for ghost in Ghosts})

    def getPossibleStates(self, state, NewState, action = None):
        """Returns a dictionary of the possible actions that Pacman can make as dictionary keys (N,E,S,W) and the new states after taking those actions as dictionary values."""
        
        Walls = self.getWalls(state)

        UP = (NewState[0], NewState[1] + 1)
        DOWN = (NewState[0], NewState[1] - 1)
        LEFT = (NewState[0] - 1, NewState[1])
        RIGHT = (NewState[0] + 1, NewState[1])

        # If somehow our current position is a wall coordinate, we get out of it.
        if NewState in Walls:
            # If Pacman is inside one of the four outer walls...
            if NewState[1] == max(self.Corners)[1]:
                return {Directions.SOUTH : DOWN}
            if NewState[1] == min(self.Corners)[1]:
                return {Directions.NORTH : UP}
            if NewState[0] == max(self.Corners)[0]:
                return {Directions.WEST : LEFT}
            if NewState[0] == min(self.Corners)[0]:
                return {Directions.EAST : RIGHT}
            
            # If Pacman is inside one of the inner walls...
            if min(self.Corners)[0] < NewState[0] < max(self.Corners)[0] and min(self.Corners)[1] < NewState[1] < max(self.Corners)[1]:
                Escape = {}

                if UP not in Walls and UP[1] < self.MapHeight:
                    Escape.update({Directions.NORTH: UP})
                if DOWN not in Walls and DOWN[1] >= 0:
                    Escape.update({Directions.SOUTH: DOWN})
                if LEFT not in Walls and LEFT[0] >= 0:
                    Escape.update({Directions.WEST: LEFT})
                if RIGHT not in Walls and RIGHT[0] < self.MapWidth:
                    Escape.update({Directions.EAST: RIGHT})

                return Escape

        PossibleStates = {}
        PossibleDirections = {Directions.NORTH : UP, Directions.SOUTH : DOWN, Directions.WEST : LEFT, Directions.EAST : RIGHT}

        # If the action is north or south, the alternative actions pacman could take are west and east.
        # If there is a wall in any of the 3 directions, return pacman's current state.
        if action == Directions.NORTH or action == Directions.SOUTH:
            PossibleStates[action] = PossibleDirections[action] if PossibleDirections[action] not in Walls else NewState
            PossibleStates[Directions.EAST] = RIGHT if RIGHT not in Walls else NewState
            PossibleStates[Directions.WEST] = LEFT if LEFT not in Walls else NewState
        
        # If the action is east or west, the alternative actions pacman could take are south and north.
        # If there is a wall in any of the 3 directions, return pacman's current state.
        elif action == Directions.EAST or action == Directions.WEST:
            PossibleStates[action] = PossibleDirections[action] if PossibleDirections[action] not in Walls else NewState
            PossibleStates[Directions.NORTH] = UP if UP not in Walls else NewState
            PossibleStates[Directions.SOUTH] = DOWN if DOWN not in Walls else NewState
        
        return PossibleStates

    def MEU(self, state, NewState, U):
        """Returns respectively the best action and the maximum expected utility (MEU) of a state."""

        Walls = self.getWalls(state)
        ExpectedUtilities = {}

        for action in (Directions.EAST, Directions.WEST, Directions.NORTH, Directions.SOUTH):
            legal = self.getPossibleStates(state, NewState, action)
            EU = 0

            # If the state is not a wall, then there is a 80% probability of making the intended move
            # and a 10% probability of making any other two perpendicular moves.
            if NewState not in Walls:
                for dir, pos in legal.items():
                    if action == dir:
                        EU += self.IntendedDirectionProbability*U[pos]
                    else:
                        EU += self.NotIntendedDirectionProbability*U[pos]

            # If somehow pacman is inside of a wall, there is a 100% probability of making the intended move
            # (i.e. getting out of the wall).
            else:
                dir, pos = list(legal.keys())[0], list(legal.values())[0]
                if action == dir:
                    EU += 1.0*U[pos]
                else:
                    EU += 0.0
            
            ExpectedUtilities[action] = EU
        
        # The MEU will be the maximum value of the dictionary.
        MEU = max(ExpectedUtilities.values())
        # The best policy will be the corresponding key.
        BestPolicy = max(ExpectedUtilities, key = ExpectedUtilities.get)

        return BestPolicy, MEU

    def ValueIteration(self, state, Reward, Discount, MaxIters = 500, Precision = 3):
        """This is the value iteration algorithm to compute the utility of every state. It returns a dictionary with all the states as dictionary keys and the utility of each state as key value. The maximum number of iterations for convergence is restricted by `maxIters`, which is 500 by default."""
        
        # We initialise the utility dictionary.
        U = {(x,y): 0.0 for x in range(self.MapWidth) for y in range(self.MapHeight)}
        converge = False
        loops = 0
        
        # Until convergence (or until we reach the maximum allowed number of iterations)...
        while not converge and loops < MaxIters:
            # Make a copy of the previous utility dictionary.
            Old_U = U.copy()

            # For each state, we find the MEU and calculate the updated utility.
            for s in list(U.keys()):
                _, MEU = self.MEU(state, s, Old_U)
                U[s] = round(Reward[s] + Discount*MEU, Precision)
            
            # If all the values from the previous utility dictionary are equal to the current one,
            # then we say that it converges and the loop terminates.
            if all(U[S] == Old_U[S] for S in list(U.keys())):
                converge = True

            loops += 1

        return U
    
    def getBestPolicy(self, state, discount = 0.9):
        """Returns the best action for Pacman to take based of the value iteration algorithm."""
        
        # Update the rewards of each state.
        self.getRewards(state)
        # Retrieve the utility dictionary.
        U = self.ValueIteration(state, self.Rewards, discount)
        current_position = api.whereAmI(state)

        # Get the best action to take in the current state.
        BestAction, _ = self.MEU(state, current_position, U)

        return BestAction

    def getAction(self, state):
        
        legal = api.legalActions(state)

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
            
        action = self.getBestPolicy(state)

        # If the best action is legal, then we follow through.
        # Otherwise, we pass it through api.makeMove, which
        # will select a new move if it's not legal.
        return action if action in legal else api.makeMove(action, legal)
