import sys
import copy
import math
import heapq as hq
from datetime import datetime as dt


class Puzzle():
    def __init__(self, tiles=[], parent_puzzle=None, heuristic_cost=0, move_cost=0, total_cost=0, last_move=None):
        self.tiles = tiles
        self.parent_puzzle = parent_puzzle
        self.heuristic_cost = heuristic_cost
        self.move_cost = move_cost
        self.total_cost = total_cost
        self.last_move = last_move

    def __hash__(self):
        return hash(str(self.tiles))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.tiles == other.tiles
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.total_cost < other.total_cost
        return False

    def set_heuristic_cost(self, z_a, z_b, metric, finish_puzzle, search):
        heuristic_cost = 0

        # handle search 3 uniform-cost
        if search == 3:
            if self.parent_puzzle:
                self.move_cost = self.parent_puzzle.move_cost + 1
                self.total_cost = self.move_cost
            else:
                self.total_cost = self.move_cost
        else:
            # Manhatten, Euclidean, etc. Distance
            for x, tiles_row in enumerate(self.tiles):

                for y, tile_value in enumerate(tiles_row):

                    if tile_value:
                        a, b = _get_tile_coordinates(tile_value, finish_puzzle)

                        if metric == 1:
                            # Manhattan Distance
                            heuristic_cost += abs(x - a) + abs(y - b)

                        elif metric == 2:
                            # Euclidean Distance
                            heuristic_cost += math.sqrt((x - a)**2 + (y - b)**2)

                        elif metric == 3:
                            # Chebyshev Distance
                            heuristic_cost += max([abs(x - a), abs(y - b)])

                        elif metric == 4:
                            # Minkowski Distance with p=4
                            heuristic_cost += ((x - a)**4 + (y - b)**4)**0.25

                        elif metric == 5:
                            # Hamming Distance
                            if tile_value != finish_puzzle.tiles[x][y]:
                                heuristic_cost += 1

                        elif metric == 6:
                            # “Canberra Distance
                            if x or a:
                                heuristic_cost += abs(x-a) / (x+a)
                            if y or b:
                                heuristic_cost += abs(y-b) / (y+b)

        self.heuristic_cost = heuristic_cost

        # handle search type 1 standard or 2 greedy
        if search == 2:
            self.total_cost = self.heuristic_cost
        else:
            if self.parent_puzzle:
                self.move_cost = self.parent_puzzle.move_cost + 1
                self.total_cost = heuristic_cost + self.move_cost
            else:
                self.total_cost = heuristic_cost

        return self


def _init_start_finish_puzzles(start_tiles, finish_tiles):
    start_puzzle = Puzzle(tiles=start_tiles)
    finish_puzzle = Puzzle(tiles=finish_tiles)

    return start_puzzle, finish_puzzle, len(start_tiles)


def _get_tile_coordinates(tile, puzzle):
    for a, tiles_row in enumerate(puzzle.tiles):
        for b, tile_value in enumerate(tiles_row):
            if tile_value == tile:
                return a, b


def _find_better_in_close_set(current_puzzle=None, close_set={}):
    return current_puzzle in close_set and close_set[current_puzzle] <= current_puzzle.total_cost


def _get_child_set(puzzle, n):
    child_set = []
    x, y = _get_tile_coordinates(0, puzzle)

    if x+1 < n and puzzle.last_move != 'down':
        tiles = copy.deepcopy(puzzle.tiles)
        tiles[x][y], tiles[x+1][y] = tiles[x+1][y], tiles[x][y]
        child_puzzle = Puzzle(tiles, puzzle)
        child_puzzle.last_move = 'up'
        child_set.append(child_puzzle)
    
    if x-1 >= 0 and puzzle.last_move != 'up':
        tiles = copy.deepcopy(puzzle.tiles)
        tiles[x][y], tiles[x-1][y] = tiles[x-1][y], tiles[x][y]
        child_puzzle = Puzzle(tiles, puzzle)
        child_puzzle.last_move = 'down'
        child_set.append(child_puzzle)
    
    if y+1 < n and puzzle.last_move != 'right':
        tiles = copy.deepcopy(puzzle.tiles)
        tiles[x][y], tiles[x][y+1] = tiles[x][y+1], tiles[x][y]
        child_puzzle = Puzzle(tiles, puzzle)
        child_puzzle.last_move = 'left'
        child_set.append(child_puzzle)
    
    if y-1 >= 0 and puzzle.last_move != 'left':
        tiles = copy.deepcopy(puzzle.tiles)
        tiles[x][y], tiles[x][y-1] = tiles[x][y-1], tiles[x][y]
        child_puzzle = Puzzle(tiles, puzzle)
        child_puzzle.last_move = 'right'
        child_set.append(child_puzzle)

    return child_set


def _get_parent_set(puzzle=None):
    parent_set = []

    while puzzle:
        parent_set.insert(0, puzzle)
        puzzle = puzzle.parent_puzzle

    return parent_set


def _print_solution(puzzle=None, time_complexity=0, size_complexity=0, start_time=0):
    parent_set = _get_parent_set(puzzle)

    for current_puzzle in parent_set:
        for row in current_puzzle.tiles:
            print(' '.join(map(str, row)))
        print()

    print(f'COMPLEXITY TIME {time_complexity}')
    print(f'COMPLEXITY SIZE {size_complexity}')
    print(f'STEPS {len(parent_set) - 1}')
    print(f'TIME {dt.now() - start_time}')


def a(start_tiles, finish_tiles, metric=1, search=1):
    start_time = dt.now()
    start_puzzle, finish_puzzle, n = _init_start_finish_puzzles(start_tiles, finish_tiles)
    z_a, z_b = _get_tile_coordinates(0, finish_puzzle)
    start_puzzle = start_puzzle.set_heuristic_cost(z_a, z_b, metric, finish_puzzle, search)

    open_set = []
    hq.heappush(open_set, start_puzzle)
    close_set = {}
    time_complexity = size_complexity = 0

    while 1:
        if not open_set:
            print('NOT FOUND', start_puzzle.tiles)
            return

        current_puzzle = hq.heappop(open_set)
        
        time_complexity += 1
        if len(open_set)+len(close_set) > size_complexity:
            size_complexity = len(open_set) + len(close_set)

        if current_puzzle == finish_puzzle:
            _print_solution(current_puzzle, time_complexity, size_complexity, start_time)
            return

        if not _find_better_in_close_set(current_puzzle, close_set):
            close_set[current_puzzle] = current_puzzle.total_cost
            child_set = _get_child_set(current_puzzle, n)

            for child_puzzle in child_set:
                hq.heappush(open_set, child_puzzle.set_heuristic_cost(z_a, z_b, metric, finish_puzzle, search))


def _ida_recursive_search(puzzle, max_total_cost, z_a, z_b, complexity_time, complexity_size, metric, finish_puzzle, n, search):
    if puzzle.total_cost > max_total_cost:
        return None, puzzle.total_cost, complexity_time, complexity_size

    complexity_time += 1
    if puzzle == finish_puzzle:
        return puzzle, max_total_cost, complexity_time, complexity_size

    min_total_cost = math.inf
    child_set = _get_child_set(puzzle, n)
    complexity_size += len(child_set)

    for child_puzzle in child_set:
        child_puzzle = child_puzzle.set_heuristic_cost(z_a, z_b, metric, finish_puzzle, search)
        current_puzzle, new_total_cost, complexity_time, complexity_size = _ida_recursive_search(child_puzzle, max_total_cost, z_a, z_b, complexity_time, complexity_size, metric, finish_puzzle, n, search)

        if current_puzzle != None:
            return current_puzzle, None, complexity_time, complexity_size

        if new_total_cost < min_total_cost:
            min_total_cost = new_total_cost

    return None, min_total_cost, complexity_time, complexity_size


def ida(start_tiles, finish_tiles, metric=1, search=1):
    start_time = dt.now()
    start_puzzle, finish_puzzle, n = _init_start_finish_puzzles(start_tiles, finish_tiles)

    z_a, z_b = _get_tile_coordinates(0, finish_puzzle)
    start_puzzle = start_puzzle.set_heuristic_cost(z_a, z_b, metric, finish_puzzle, search)

    max_total_cost = start_puzzle.total_cost
    z_a, z_b = _get_tile_coordinates(0, finish_puzzle)

    complexity_time = 0
    max_size = 0
    while 1:
        complexity_size = 1
        puzzle, new_total_cost, complexity_time, complexity_size = _ida_recursive_search(start_puzzle, max_total_cost, z_a, z_b, complexity_time, complexity_size, metric, finish_puzzle, n, search)

        if max_size < complexity_size:
            max_size = complexity_size

        if puzzle != None:
            _print_solution(puzzle, complexity_time, max_size, start_time)
            return

        if new_total_cost == math.inf:
            return

        max_total_cost = new_total_cost
