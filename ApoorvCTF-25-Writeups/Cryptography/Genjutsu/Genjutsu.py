from sympy import primerange
import random
import heapq
from collections import deque
from art import *


def generate_grid(size):
    grid = [[random.randint(0, 9) for col in range(size)] for row in range(size)]
    grid[0][0] = 0
    return grid

def affine_encrypt(n, a, b, mod=101):
    return (a * n + b) % mod

def build_encrypted_grid(grid, a, b, mod=101):
    size = len(grid)
    encry_grid = []
    for y in range(size):
        row = []
        for x in range(size):
            enc_val = affine_encrypt(grid[y][x], a, b, mod)
            row.append(str(enc_val).zfill(2))
        encry_grid.append(row)
    return encry_grid

def str_grid(encry_grid, player_pos=None):
    size = len(encry_grid)
    display = []
    for y in range(size):
        row_disp = []
        for x in range(size):
            if player_pos and (x, y) == player_pos:
                row_disp.append("Pa")
            else:
                row_disp.append(encry_grid[y][x])
        display.append(" ".join(row_disp))
    return "\n".join(display)

def opt_xor(grid, start=(0, 0), end=None):
    size = len(grid)
    if end is None:
        end = (size - 1, size - 1)

    heap = [(grid[0][0], 0, 0, [(0, 0)])]  
    best_xor = { (0, 0): grid[0][0] }

    while heap:
        xor_val, x, y, path = heapq.heappop(heap)

        if (x, y) == end:
            return xor_val 

        for dx, dy in [(0, 1), (1, 0)]:  
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                new_xor = xor_val ^ grid[ny][nx]

                if (nx, ny) not in best_xor or new_xor < best_xor[(nx, ny)]:
                    best_xor[(nx, ny)] = new_xor
                    heapq.heappush(heap, (new_xor, nx, ny, path + [(nx, ny)]))

    return None, []  


def play_maze():
    size = 10
    grid = generate_grid(size)
    a = random.choice(list(primerange(2, 12)))
    b = 0
    encry_grid = build_encrypted_grid(grid, a, b, mod=101)
    optimal_xor = opt_xor(grid)

    Art = text2art("Genjutsu")
    print(Art)
    print("Welcome to Genjutsu Labyrinth!")
    print("Your goal is to navigate from the top-left to the bottom-right successfully")
    print("Note: Your current position is denoted by Pa. The first cell has a value 0")
    print("-------------------------------------------------\n")
    print(str_grid(encry_grid, player_pos=(0, 0)))
    print("\nUse S/D to move down or right. Type 'exit' to quit.")

    x, y = 0, 0
    current_xor = grid[0][0]  

    while (x, y) != (size - 1, size - 1):
        move = input("Enter move (S/D): ").strip().upper()
        if move == "EXIT":
            print("Game exited.")
            return
        dx, dy = 0, 0
        if move == "S":
            dy = 1
        elif move == "D":
            dx = 1
        elif move == "W" or move == "A":
            print("You cannot move upwards or leftwards! Use S/D")
        else:
            print("Invalid move! Use S/D.")
            continue
        
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < size and 0 <= new_y < size:
            x, y = new_x, new_y
            current_xor ^= grid[y][x]
            print(f"Moved to {(y, x)}. Current XOR: {current_xor}")
        else:
            print("You hit the edge of the grid!")

        print("\n" + str_grid(encry_grid, player_pos=(x, y)))

    print("\nYou've reached the exit!")
    print(f"Your final XOR: {current_xor}")
    if current_xor == optimal_xor:
        print("Congratulations! You've found the flag: apoorvctf{G3NJUTSU_M4ST3R}")
    else:
        print("Not the optimal path! Try again to minimize the XOR.")

play_maze()
