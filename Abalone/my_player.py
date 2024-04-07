from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState

MAX_PIECES = 14
CENTER_HEX = (8, 4)
DEPTH = 1

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
        

    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Function to implement the logic of the player.
        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments
        Returns:
            Action: selected feasible action
        """
        initial_actions = current_state.get_possible_actions()
        sorted_actions = sorted(initial_actions, key=self.evaluate_action_priority, reverse=True)
        best_action = None
        best_score = float('-inf')

        for action in sorted_actions:
            next_state = action.get_next_game_state()
            score = self.minimax(next_state, DEPTH, True)

            if score > best_score:
                best_score = score
                best_action = action
        print(best_action)
        return best_action
    
    def minimax(self, state: GameStateAbalone, depth: int, is_maximizing: bool) -> int:
        """
        Minimax algorithm implementation.
        Args:
            state (GameState): Current game state
            depth (int): Depth of the tree
            is_maximizing (bool): True if the player is maximizing
        Returns:
            int: The score of the best action
        """
        if depth == 0 or state.is_done():
            return self.get_score(state)

        if is_maximizing:
            best_score = float('-inf')
            for action in state.get_possible_actions():
                next_state = action.get_next_game_state()
                score = self.minimax(next_state, depth - 1, False)
                best_score = max(best_score, score)
        else:
            best_score = float('inf')
            for action in state.get_possible_actions():
                next_state = action.get_next_game_state()
                score = self.minimax(next_state, depth - 1, True)
                best_score = min(best_score, score)
        return best_score
    
    def get_score(self, state: GameStateAbalone) -> int:
        """
        Get the score of the state.
        Args:
            state (GameState): The current game state
        Returns:
            int: The score of the state
        """
        piece_count_weight = 10.0
        center_control_weight = 3.0
        adjacency_weight = 1.0

        pieces_count_heuristic = self.pieces_count(state)
        center_proximity_heuristic = self.center_proximity_count(state)
        adjacency_heuristic = self.adjacency_count(state)

        score = piece_count_weight * pieces_count_heuristic + center_control_weight * center_proximity_heuristic + adjacency_weight * adjacency_heuristic
        
        return score
    
    def evaluate_action_priority(self, action: Action) -> int:
        """
        Prioritize actions based on the change in piece counts. Moves that result in a better piece count difference are preferred.
        Args:
            action (Action): The action to evaluate
        Returns:
            int: The priority of the action
        """
        current_state = action.get_current_game_state()
        next_state = action.get_next_game_state()

        current_score = self.pieces_count(current_state)
        next_score = self.pieces_count(next_state)

        return next_score - current_score


    def pieces_count(self, state: GameStateAbalone) -> int:
        """
        Get our player pieces count vs opponent pieces count.
        Args:
            state (GameState): The current game state
        Returns:
            int: The difference between player pieces and opponent pieces
        """
        player_pieces = MAX_PIECES - abs(state.get_player_score(self))
        opponent_pieces = MAX_PIECES - abs(next(value for key, value in state.get_scores().items() if key != self.get_id()))
        return player_pieces - opponent_pieces

    def center_proximity_count(self, state: GameStateAbalone) -> int:
        """
        Get the proximity of the player pieces to the center.
        Args:
            state (GameState): The current game state
        Returns:
            int: The proximity of the player pieces to the center
        """
        distances_player = 0
        distances_opponent = 0

        pieces = [(coordinates, piece.__dict__) for coordinates, piece in state.get_rep().env.items()]

        for coordinates, piece_info in pieces:
            dist_to_center = hex_manhattan_distance(coordinates, CENTER_HEX)
            if piece_info["owner_id"] == self.get_id():
                distances_player += dist_to_center
            else:
                distances_opponent += dist_to_center

        return distances_opponent - distances_player
    
    def adjacency_count(self, state: GameStateAbalone) -> int:
        """
        Get the adjacency heuristic of the player.
        Args:
            state (GameState): The current game state
        Returns:
            int: The adjacency heuristic of the player
        """
        neighbors_player = 0
        neighbors_adversary = 0

        for coordinates, piece in state.get_rep().env.items():
            if piece is None:
                continue

            owner_id = piece.get_owner_id()

            neighbors = state.get_neighbours(coordinates[0], coordinates[1]).values()

            for _, neighbor_coordinates in neighbors:
                if neighbor_coordinates in state.get_rep().env:
                    neighbor_piece = state.get_rep().env[neighbor_coordinates]
                    if neighbor_piece and neighbor_piece.get_owner_id() == owner_id:
                        if owner_id == self.get_id():
                            neighbors_player += 1
                        else:
                            neighbors_adversary += 1

            return neighbors_player - neighbors_adversary

def hex_manhattan_distance(hex1, hex2):
    cube1 = offset_to_cube(hex1)
    cube2 = offset_to_cube(hex2)
    return cube_distance(cube1, cube2)

def cube_distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))

def offset_to_cube(hex):
    x = hex[0] - (hex[1] - (hex[1]&1)) // 2
    z = hex[1]
    y = -x-z
    return (x, y, z)