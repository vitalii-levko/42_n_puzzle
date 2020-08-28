from datetime import datetime as dt
import copy


def get_pos(i, puzzle):
    for y, row in enumerate(puzzle):
        for x, col in enumerate(row):
            if puzzle[y][x] == i:
                return y, x

def get_inversion_dict(puzzle):
    inversion_dict = dict()
    for check_row in range(len(puzzle)):
        for check_col in range(len(puzzle[0])):
            to_check = puzzle[check_row][check_col]
            inversion_dict[to_check] = list()
            for row in range(len(puzzle)):
                if row >= check_row:
                    for col in range(len(puzzle[0])):
                        if (col >= check_col or (col < check_col and row != check_row)) and to_check != puzzle[row][col]:
                            inversion_dict[to_check].append(puzzle[row][col])
    return inversion_dict

def can_solve(puzzle, good_state):
    good_row, good_col = get_pos(0 , good_state)
    row, col = get_pos(0 , puzzle)
    dist = abs(good_col - col) + abs(good_row - row)
    inversion_dict = get_inversion_dict(good_state)
    count_inverse = 0
    for check_row in range(len(puzzle)):
        for check_col in range(len(puzzle[0])):
            to_check = puzzle[check_row][check_col]
            for row in range(len(puzzle)):
                if row >= check_row:
                    for col in range(len(puzzle[0])):
                        if (col >= check_col or (col < check_col and row != check_row)) and to_check in inversion_dict[puzzle[row][col]]:
                            count_inverse += 1                  
    if (count_inverse % 2 == 0 and dist % 2 == 0) or (count_inverse % 2 != 0 and dist % 2 != 0):
        return True
    return False

def count_metric(puzzle, good_state, metric):
    if puzzle[0][0] == -1:
        return 1000
    all_dist = 0
    for i in range(len(puzzle) * len(puzzle[0])):
        good_row, good_col = get_pos(i, good_state)
        row, col = get_pos(i , puzzle)
        if metric == 1:
            all_dist += abs(good_col - col) + abs(good_row - row)
        if metric == 2:
            all_dist += ((good_col - col)**2 + (good_row - row)**2)**0.5
        if metric == 3:
            all_dist += max(abs(good_col - col), abs(good_row - row))
        if metric == 4:
            all_dist += ((good_col - col)**4 + (good_row - row)**4)**0.25
        if metric == 5:
            if good_col != col or good_row != row:
                all_dist += 1
        if metric == 6:
            if good_col or col:
                all_dist += abs(good_col - col) / (good_col + col)
            if good_row or row:
                all_dist += abs(good_row - row) / (good_row + row)
    return all_dist

def make_moves(puzzle, good_state, metric):
    row, col = get_pos(0, puzzle)
    ln = len(puzzle)
    buff = puzzle[row][col]
    moves = list()
    if col != 0:
        left_puzzle = copy.deepcopy(puzzle)
        left_puzzle[row][col] = left_puzzle[row][col - 1]
        left_puzzle[row][col - 1] = buff
        moves.append([left_puzzle, 'left', count_metric(left_puzzle, good_state, metric)])
    if col != ln - 1:
        right_puzzle = copy.deepcopy(puzzle)
        right_puzzle[row][col] = right_puzzle[row][col + 1]
        right_puzzle[row][col + 1] = buff
        moves.append([right_puzzle, 'right', count_metric(right_puzzle, good_state, metric)])
    if row != 0:
        up_puzzle = copy.deepcopy(puzzle)
        up_puzzle[row][col] = up_puzzle[row - 1][col]
        up_puzzle[row - 1][col] = buff
        moves.append([up_puzzle, 'up', count_metric(up_puzzle, good_state, metric)])
    if row != ln - 1:
        down_puzzle = copy.deepcopy(puzzle)
        down_puzzle[row][col] = down_puzzle[row + 1][col]
        down_puzzle[row + 1][col] = buff      
        moves.append([down_puzzle, 'down', count_metric(down_puzzle, good_state, metric)])
    return moves

def npuzzle(puzzle, good_state, metric, search):
    root = {'state':puzzle, 'metrics':[count_metric(puzzle, good_state, metric), 0, True], 'path':[puzzle]}
    queue = [root]
    if search == 1:
        weight_to_check = root['metrics'][0] + root['metrics'][1]
    elif search == 2:
        weight_to_check = root['metrics'][0]
    elif search == 3:
        weight_to_check = root['metrics'][1]
    minimal = root['metrics'][0]
    finish = True
    start = dt.now()
    ctime = 0
    csize = 0
    all_puzzles = {}
    while finish:
        current_root = queue.pop(0)
        ctime += 1
        if (len(queue) + len(all_puzzles)) > csize:
            csize = len(queue) + len(all_puzzles)
        moves = make_moves(current_root['state'], good_state, metric)
        for move in moves:
            root = {'state':move[0], 'metrics':[move[2], current_root['metrics'][1] + 1], 'path':current_root['path'] + [move[0]]}
            if search == 1:
                score = root['metrics'][0] + root['metrics'][1]
            elif search == 2:
                score = root['metrics'][0]
            elif search == 3:
                score = root['metrics'][1]
            if str(move[0]) not in all_puzzles or (str(move[0]) in all_puzzles and all_puzzles[str(move[0])] > score):
                all_puzzles[str(move[0])] = score
                l = len(queue)
                if l == 0:
                    queue.append(root)
                else:
                    for i, item in enumerate(queue):
                        if search == 1:
                            item_score = item['metrics'][0] + item['metrics'][1]
                        elif search == 2:
                            item_score = item['metrics'][0]
                        elif search == 3:
                            item_score = item['metrics'][1]
                        if score <= item_score:
                            queue.insert(i, root)
                            break
                        else:
                            continue
                    if l == len(queue):
                        queue.append(root)
        if queue[0]['state'] == good_state:
            finish = False
            final_path = queue[0]['path']
    current_root = root
    for move in final_path:
        for row in move:
            print(' '.join(map(str, row)))
        print('')
    print("COMPLEXITY TIME: " + str(ctime))   
    print("COMPLEXITY SIZE: " + str(csize))
    print("STEPS: " + str(len(final_path) - 1))
    print("TIME: " + str(dt.now() - start))
