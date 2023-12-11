from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    # NotImplemented()
    """
    Perform the Minimax algorithm to find the best move in a game.

    Parameters:
    - game (Game): The game instance.
    - state (S): The current state of the game.
    - heuristic (HeuristicFunction): The heuristic function to evaluate non-terminal states.
    - max_depth (int): The maximum depth to explore the game tree. If set to -1, it explores the entire tree.

    Returns:
    - Tuple[float, A]: The best evaluation value and the corresponding best action.
    """

    agent = game.get_turn(state)
    terminal, values = game.is_terminal(state)

    if terminal:
        return values[agent], None

    if max_depth == 0:
        if agent == 0:
            return heuristic(game, state, agent), None
        else:
            return -heuristic(game, state, agent), None

    # Get all the actions and the resulting states
    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]

    if agent == 0:  # Player's turn (max node)
        best_value = float('-inf')
        best_action = None

        for action, successor_state in actions_states:
            # Recursive call to minimax for each successor state
            value, _ = minimax(game, successor_state, heuristic, max_depth - 1)

            # Update the best value and action
            if value > best_value:
                best_value = value
                best_action = action

        return best_value, best_action

    else:  # Monster's turn (min node)
        best_value = float('inf')
        best_action = None

        for action, successor_state in actions_states:
            # Recursive call to minimax for each successor state
            value, _ = minimax(game, successor_state, heuristic, max_depth - 1)

            # Update the best value and action
            if value < best_value:
                best_value = value
                best_action = action

        return best_value, best_action
    
# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    # NotImplemented()
    """
    Perform the Alpha-Beta Pruning algorithm to find the best move in a game.

    Parameters:
    - game (Game): The game instance.
    - state (S): The current state of the game.
    - heuristic (HeuristicFunction): The heuristic function to evaluate non-terminal states.
    - max_depth (int): The maximum depth to explore the game tree. If set to -1, it explores the entire tree.

    Returns:
    - Tuple[float, A]: The best evaluation value and the corresponding best action.
    """

    def alphabeta_helper(state, alpha, beta, depth):
        """
        Helper function for the Alpha-Beta Pruning algorithm.

        Parameters:
        - state (S): The current state of the game.
        - alpha (float): The alpha value for pruning.
        - beta (float): The beta value for pruning.
        - depth (int): The remaining depth to explore.

        Returns:
        - Tuple[float, A]: The evaluation value and the corresponding action.
        """

        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)

        if terminal:
            return values[agent], None

        if depth == 0:
            if agent == 0:
                return heuristic(game, state, agent), None
            else:
                return -heuristic(game, state, agent), None

        if agent == 0:
            max_eval = float('-inf')
            max_action = None

            for action in game.get_actions(state):
                eval, _ = alphabeta_helper(game.get_successor(state, action), alpha, beta, depth - 1)

                if eval > max_eval:
                    max_eval = eval
                    max_action = action

                alpha = max(alpha, eval)

                if beta <= alpha:
                    break

            return max_eval, max_action

        else:
            min_eval = float('inf')
            min_action = None

            for action in game.get_actions(state):
                eval, _ = alphabeta_helper(game.get_successor(state, action), alpha, beta, depth - 1)

                if eval < min_eval:
                    min_eval = eval
                    min_action = action

                beta = min(beta, eval)

                if beta <= alpha:
                    break

            return min_eval, min_action

    return alphabeta_helper(state, float('-inf'), float('inf'), max_depth)

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    """
    Perform the Alpha-Beta Pruning algorithm with move ordering to find the best move in a game.

    Parameters:
    - game (Game): The game instance.
    - state (S): The current state of the game.
    - heuristic (HeuristicFunction): The heuristic function to evaluate non-terminal states.
    - max_depth (int): The maximum depth to explore the game tree. If set to -1, it explores the entire tree.

    Returns:
    - Tuple[float, A]: The best evaluation value and the corresponding best action.
    """

    def alphabeta_helper(state, alpha, beta, depth):
        """
        Helper function for the Alpha-Beta Pruning algorithm with move ordering.

        Parameters:
        - state (S): The current state of the game.
        - alpha (float): The alpha value for pruning.
        - beta (float): The beta value for pruning.
        - depth (int): The remaining depth to explore.

        Returns:
        - Tuple[float, A]: The evaluation value and the corresponding action.
        """

        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)

        if terminal:
            if agent == 0:
                return values[agent], None
            else:
                return -values[agent], None

        if depth == 0:
            if agent == 0:
                return heuristic(game, state, agent), None
            else:
                return -heuristic(game, state, agent), None

        actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]

        if agent == 0:
            sorted_actions_states = sorted(actions_states, key=lambda x: heuristic(game, x[1], agent), reverse=True)

            max_eval = float('-inf')
            max_action = None

            for action, state in sorted_actions_states:
                eval, _ = alphabeta_helper(state, alpha, beta, depth - 1)
                if eval > max_eval:
                    max_eval = eval
                    max_action = action
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, max_action

        else:
            sorted_actions_states = sorted(actions_states, key=lambda x: -heuristic(game, x[1], agent), reverse=False)

            min_eval = float('inf')
            min_action = None

            for action, state in sorted_actions_states:
                eval, _ = alphabeta_helper(state, alpha, beta, depth - 1)
                if eval < min_eval:
                    min_eval = eval
                    min_action = action
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, min_action

    return alphabeta_helper(state, float('-inf'), float('inf'), max_depth)

# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    # NotImplemented()
    """
    Perform the Expectimax algorithm to find the best move in a game.

    Parameters:
    - game (Game): The game instance.
    - state (S): The current state of the game.
    - heuristic (HeuristicFunction): The heuristic function to evaluate non-terminal states.
    - max_depth (int): The maximum depth to explore the game tree. If set to -1, it explores the entire tree.

    Returns:
    - Tuple[float, A]: The best evaluation value and the corresponding best action.
    """

    def expectimax_helper(state, depth):
        """
        Helper function for the Expectimax algorithm.

        Parameters:
        - state (S): The current state of the game.
        - depth (int): The remaining depth to explore.

        Returns:
        - Tuple[float, A]: The evaluation value and the corresponding action.
        """

        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)

        if terminal: 
            if agent == 0: 
                return values[agent], None  # If it is terminal, return the value for the player
            else:
                return -values[agent], None  # If it is terminal, return the negative of the value for the monster

        if depth == 0:
            if agent == 0:
                return heuristic(game, state, agent), None  # If it is the player's turn (max node), return the heuristic value
            else:
                return -heuristic(game, state, agent), None  # If it is the monster's turn (chance node), return the negative of the heuristic value

        if agent == 0:
            max_eval = float('-inf')
            max_action = None
            for action in game.get_actions(state):
                eval, _ = expectimax_helper(game.get_successor(state, action), depth - 1) 
                if eval > max_eval:
                    max_eval = eval
                    max_action = action
            return max_eval, max_action

        else:
            total_eval = 0
            for action in game.get_actions(state):
                eval, _ = expectimax_helper(game.get_successor(state, action), depth - 1)
                total_eval += eval  # Sum the values of the heuristic function of all the actions

            # Assuming all nodes have equal probability of being chosen 
            # we can return any action since they all have the same value
            return total_eval / len(game.get_actions(state)), action  # Return the average value of the heuristic function

    return expectimax_helper(state, max_depth)
