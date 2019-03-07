import copy
import random
import sys
import time


def set_fg_color(color):
    if sys.platform in ["linux", "linux2"]:
        colors = {
            "red": 91, "green": 92, "yellow": 93, "blue": 94, "white": 97
        }
        if type(color) is str and color in colors:
            color = colors[color]
        print("\033[1;%s;49m" % color, end="")


def get_grid():
    grid = []
    while grid == []:
        set_fg_color("blue")
        game_type = input("Choose game type (file, random or saved): ")
        if game_type in ["file", "random", "saved"]:
            if game_type == "saved":
                grid = read_file("saved_grid.txt")
                if grid == []:
                    print()
                    continue
            while grid == []:
                set_fg_color("blue")
                diff = input(
                    "\n" + "Choose difficulty (easy, medium or hard): ")
                if diff in ["easy", "medium", "hard", "finished"]:
                    if game_type == "file":
                        grid = read_file(diff + ".txt")
                    else:
                        grid = create_sudoku(diff)
                else:
                    set_fg_color("red")
                    print("\n" + "Wrong difficulty, try again")
        else:
            set_fg_color("red")
            print("\n" + "Wrong game type, try again" + "\n")
    return grid


def read_file(filename):
    grid = []
    try:
        with open(filename) as f:
            lines = f.read().split("\n")
            for line in lines:
                nested_list = line.split()
                nested_list = [int(item) for item in nested_list]
                grid.append(nested_list)
        return grid
    except (FileNotFoundError, ValueError):
        set_fg_color("red")
        print("\n" + "Invalid file path or file format")
        return []


def print_grid(grid, orig_grid):
    print()
    for i in range(9):
        if i > 0 and i % 3 == 0:
            print()
        for j in range(9):
            if j > 0 and j % 3 == 0:
                print("  ", end="")
            if orig_grid[i][j] != 0:
                set_fg_color("yellow")
            elif grid[i][j] == 0:
                set_fg_color("white")
            else:
                set_fg_color("green")
            print("%d " % grid[i][j], end="")
        print()


def get_input():
    while True:
        set_fg_color("blue")
        try:
            input_value = input("\n" + "[row] [column] [number to write]: ")
            if input_value == "quit":
                return input_value
            input_values = input_value.split()
            i = 0
            while i < 3:
                input_values[i] = int(input_values[i])
                if input_values[i] not in range(10):
                    break
                i += 1
            if i < 3:
                set_fg_color("red")
                print("\n" + "Numbers have to be between"
                      + "0 and 9, please try again")
            else:
                return input_values
        except (ValueError, IndexError):
            set_fg_color("red")
            print("\n" + "Wrong input, try again")


def calculate_start(row_or_column):
    if row_or_column in range(0, 3):
        return 0
    if row_or_column in range(3, 6):
        return 3
    return 6


def box_contains_number(number, grid, row_start, column_start):
    for i in range(row_start, row_start + 3):
        for j in range(column_start, column_start + 3):
            if number == grid[i][j]:
                return True
    return False


def create_sudoku(diff):
    grid_backup = list()
    nestedlist = list()
    for i in range(9):
        nestedlist.append(0)
    for i in range(9):
        grid_backup.append(nestedlist.copy())
    set_fg_color("white")
    print("\n" + "Generating random sudoku...", end="")
    generated = False
    while not generated:
        grid = copy.deepcopy(grid_backup)
        generated = generate_complete_sudoku(grid)
    print()
    if diff == "easy":
        how_many = 41
    elif diff == "medium":
        how_many = 53
    elif diff == "hard":
        how_many = 60
    else:
        how_many = 1
    remove_numbers(grid, how_many)
    return grid


def generate_complete_sudoku(grid):
    for i in range(9):
        for j in range(9):
            numbers = [k for k in range(1, 10)]
            repeat = True
            while repeat:
                if numbers == []:
                    return False
                rnd = random.randint(0, len(numbers) - 1)
                if numbers[rnd] in grid[i]:
                    numbers.remove(numbers[rnd])
                    continue
                iterator = 0
                while iterator < 9 and numbers[rnd] != grid[iterator][j]:
                    iterator += 1
                if iterator < 9:
                    numbers.remove(numbers[rnd])
                    continue
                row_start = calculate_start(i)
                column_start = calculate_start(j)
                if box_contains_number(
                        numbers[rnd], grid, row_start, column_start):
                    numbers.remove(numbers[rnd])
                    continue
                grid[i][j] = numbers[rnd]
                repeat = False
    return True


def remove_numbers(grid, how_many):
    if how_many in range(82):
        while how_many > 0:
            row = random.randint(0, 8)
            column = random.randint(0, 8)
            if grid[row][column] != 0:
                grid[row][column] = 0
                how_many -= 1
    else:
        set_fg_color("red")
        print("\n" + "Invalid function input")


def edit_grid(grid, orig_grid):
    game_won = False
    while not game_won:
        print_grid(grid, orig_grid)
        input_values = get_input()
        if input_values == "quit":
            break
        row = input_values[0] - 1
        column = input_values[1] - 1
        number = input_values[2]

        if orig_grid[row][column] != 0:
            set_fg_color("red")
            print("\n" + "This number can't be changed")
        elif number == 0:
            grid[row][column] = 0
        elif number in grid[row]:
            set_fg_color("red")
            print("\n" + "Row %d can't have another %d" % (row + 1, number))
        else:
            iterator = 0
            while iterator < 9 and not number == grid[iterator][column]:
                iterator += 1
            if iterator < 9:
                set_fg_color("red")
                print(
                    "\n" + "Column %d can't have another %d"
                    % (column + 1, number))
            else:
                row_start = calculate_start(row)
                column_start = calculate_start(column)
                if box_contains_number(number, grid, row_start, column_start):
                    set_fg_color("red")
                    print("\n" + "Box can't have another %d" % number)
                else:
                    grid[row][column] = number
                    game_won = check_if_won(grid)


def check_if_won(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return False
    return True


def save_game(filename, grid, seconds):
    row = ""
    with open(filename, "w") as f:
        for i in grid:
            row += " ".join([str(j) for j in i]) + "\n"
        if seconds > 0:
            row += f"{seconds:.0f}"
        else:
            row = row[:-1]
        f.write(row)


def print_win_message():
    color_id = 91
    message = "You win! Congratulations!".upper()
    print()
    for c in message:
        set_fg_color(color_id)
        print(c + "  ", end="")
        if color_id == 96:
            color_id = 91
        else:
            color_id += 1
    print("\n")


def show_clear_time(seconds):
    minutes = seconds // 60
    seconds -= minutes * 60
    hours = minutes // 60
    minutes -= hours * 60
    set_fg_color("white")
    print("Clear time: %d hours, %d minutes, %d seconds"
          % (hours, minutes, seconds) + "\n")


def main():
    orig_grid = []
    saved_seconds = 0
    while orig_grid == []:
        grid = get_grid()
        if len(grid) > 9:
            orig_grid = read_file("saved_orig_grid.txt")
            saved_seconds = grid[-1][0]
            del grid[-1]
        else:
            orig_grid = copy.deepcopy(grid)
    start = time.time()
    edit_grid(grid, orig_grid)
    seconds = time.time() - start + saved_seconds
    if check_if_won(grid):
        print_grid(grid, orig_grid)
        print_win_message()
        show_clear_time(seconds)
    else:
        answer = input("\n" + "Would you like to save your progress? ")
        if "yes" in answer.lower():
            save_game("saved_grid.txt", grid, seconds)
            save_game("saved_orig_grid.txt", orig_grid, 0)
            set_fg_color("white")
            print("\n" + "Your game has been saved!" + "\n")


if __name__ == "__main__":
    main()
