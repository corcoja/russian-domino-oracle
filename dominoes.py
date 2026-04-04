from random import shuffle
from itertools import combinations_with_replacement, chain
from collections import Counter
# define turn function
def turn_func(func_input, func_pieces):
    # stop if there is no pieces
    if int(func_input) == 0 and len(stock_pieces) == 0:
        return None
    # give piece to player
    elif int(func_input) == 0 and len(stock_pieces) > 0:
        func_pieces.append(stock_pieces[-1])
        stock_pieces.remove(stock_pieces[-1])
        return None
    # place piece right after snake
    if int(func_input) > 0:
        # get piece from player or computer
        piece_to_end = func_pieces[int(func_input) - 1]
        # reverse piece
        if piece_to_end[1] == snake[-1][-1]:
            piece_to_end.reverse()
        # place piece
        snake.append(piece_to_end)
        # remove piece from player or computer
        func_pieces.remove(func_pieces[int(func_input) - 1])
    # place piece left after snake
    else:
        # get piece from player or computer
        piece_to_start = func_pieces[-int(func_input) - 1]
        # reverse piece
        if piece_to_start[0] == snake[0][0]:
            piece_to_start.reverse()
        # place piece
        snake.insert(0, piece_to_start)
        # remove piece from player or computer
        func_pieces.remove(func_pieces[-int(func_input) - 1])
# check if this snake is winning
def win_snake(func_snake):
    if func_snake[0][0] == func_snake[-1][-1] and sum(x.count(func_snake[0][0]) for x in func_snake) == 8:
        return True
# define list of dominoes
dominoes = list(combinations_with_replacement(range(0, 7), 2))
# convert list of tuples to list of lists
dominoes = [list(x) for x in dominoes]
# shuffle dominoes
shuffle(dominoes)
# define coefficient equal to half of the number of dominoes
coefficient = len(dominoes) // 2
# get first half of the dominoes
stock_pieces = dominoes[:coefficient]
# get computer's and player's pieces
computer_pieces = dominoes[coefficient:int(coefficient * 1.5)]
player_pieces = dominoes[int(coefficient * 1.5):]
# find snake
snake = [max([[x, y] for x, y in computer_pieces + player_pieces if x == y])]
# remove snake from computer's or player's pieces
computer_pieces.remove(snake[0]) if snake[0] in computer_pieces else player_pieces.remove(snake[0])
# define who is first
turn_num = 0 if len(player_pieces) > len(computer_pieces) else 1
# start game
while True:
    # show stock, player's and computer's pieces
    print('=' * 70)
    print('Stock size:', len(stock_pieces))
    print('Computer pieces:', len(computer_pieces), '\n')
    print(*snake, '\n', sep='')
    print("Your pieces:")
    for num, piece in enumerate(player_pieces):
        print(f"{num + 1}: {piece}")
    # condition for player's win
    if len(player_pieces) == 0 or win_snake(snake) and turn_num == 0:
        print("\nStatus: The game is over. You won!")
        break
    # condition for computer's win
    if len(computer_pieces) == 0 or win_snake(snake) and turn_num == 1:
        print("\nStatus: The game is over. The computer won!")
        break
    # define snake ends
    connection_keys = [snake[0][0], snake[-1][-1]]
    # condition for draw
    if len(stock_pieces) == 0 and \
            not any(item in connection_keys for item in list(chain(*(player_pieces + computer_pieces)))):
        print("\nStatus: The game is over. It's a draw!")
        break
    # player's turn
    if turn_num % 2 == 0:
        # count turn number
        turn_num += 1
        # show message
        print("\nStatus: It's your turn to make a move. Enter your command.")
        # get player's input
        user_input = input()
        # check if player's input is valid
        if user_input.lstrip("-").isdigit() and int(user_input) in range(-len(player_pieces), len(player_pieces) + 1):
            # provide piece to player
            if int(user_input) == 0:
                turn_func(user_input, player_pieces)
                turn_num -= 1
                continue
            # define current piece
            current_piece = player_pieces[int(user_input) - 1] if int(user_input) > 0 \
                else player_pieces[-int(user_input) - 1]
            # check if piece is valid
            if connection_keys[-1] in current_piece and int(user_input) > 0 or \
                    connection_keys[0] in current_piece and int(user_input) < 0:
                turn_func(user_input, player_pieces)
            else:
                print("Illegal move. Please try again.")
                turn_num -= 1
                continue
        else:
            print("Invalid input. Please try again.")
            turn_num -= 1
            continue
    # computer's turn
    else:
        # show message
        print("\nStatus: Computer is about to make a move. Press Enter to continue...")
        # wait for player's input
        input()
        # count number on pieces in snake and computer's pieces
        count_nums = Counter(chain(*(computer_pieces + snake)))
        # define scores for each piece
        scores = list()
        # iterate through all pieces to get scores
        for piece in computer_pieces:
            score = count_nums[piece[0]] + count_nums[piece[1]]
            scores.append(score)
        # sort pieces by scores
        computer_pieces = [x for _, x in sorted(zip(scores, computer_pieces), reverse=True)]
        # make computer's move
        for piece in computer_pieces:
            # check how to connect snake
            if connection_keys[-1] in piece:
                turn_func(str(computer_pieces.index(piece) + 1), computer_pieces)
                turn_num += 1
                break
            elif connection_keys[0] in piece:
                turn_func(str(-computer_pieces.index(piece) - 1), computer_pieces)
                turn_num += 1
                break
        # provide piece to computer
        else:
            print("Status: Computer has no pieces and will draw one from the stock!\n")
            turn_func('0', computer_pieces)
