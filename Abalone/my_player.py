from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError


class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)

    def minimax(self, current_state, depth, alpha, beta, maximizing_player):
        print("Depth: ", depth, "Maximizing:", maximizing_player, "Is Done:", current_state.is_done())

        if depth == 0 or current_state.is_done():
            eval = self.evaluate(current_state)
            print("Base case reached with evaluation:", eval)
            return self.evaluate(current_state)
        
        if maximizing_player:
            max_eval = float('-inf')
            print(f"Maximizing depth {depth}")
            for action in current_state.get_possible_actions():
                next_state = action.get_next_game_state()
                eval = self.minimax(next_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)  # Update alpha
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            print(f"Minimizing depth {depth}")
            for action in current_state.get_possible_actions():
                next_state = action.get_next_game_state()
                eval = self.minimax(next_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)  # Update beta
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval

    def evaluate(self, state):
        # Implement your evaluation logic here
        # For now, it just counts the number of possible actions (simple heuristic)
        return len(state.get_possible_actions())


        
         
    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        best_score = float('-inf')
        best_action = None
        alpha = float('-inf')
        beta = float('inf')
        
        for action in current_state.get_possible_actions():
            next_state = action.get_next_game_state()
            score = self.minimax(next_state, 3, alpha, beta, False)  # Starting with a depth of 3 for example
            if score > best_score:
                best_score = score
                best_action = action
        
        return best_action
