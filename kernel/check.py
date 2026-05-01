import random
from typing import List, Tuple

class Cube2x2:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = {
            'U': [['W'] * 2 for _ in range(2)],
            'D': [['Y'] * 2 for _ in range(2)],
            'F': [['G'] * 2 for _ in range(2)],
            'B': [['B'] * 2 for _ in range(2)],
            'L': [['O'] * 2 for _ in range(2)],
            'R': [['R'] * 2 for _ in range(2)],
        }
    
    def is_solved(self) -> bool:
        for face in self.state.values():
            color = face[0][0]
            for row in face:
                for c in row:
                    if c != color:
                        return False
        return True
    
    def rotate_face(self, face: str):
        original = [row[:] for row in self.state[face]]
        n = 2
        for i in range(n):
            for j in range(n):
                self.state[face][j][n-1-i] = original[i][j]
    
    def rotate_face_ccw(self, face: str):
        for _ in range(3):
            self.rotate_face(face)
    
    def rotate_U(self):
        self.rotate_face('U')
        temp = self.state['F'][0][:]
        self.state['F'][0] = self.state['R'][0][:]
        self.state['R'][0] = self.state['B'][0][:]
        self.state['B'][0] = self.state['L'][0][:]
        self.state['L'][0] = temp
    
    def rotate_U_prime(self):
        for _ in range(3):
            self.rotate_U()
    
    def rotate_D(self):
        self.rotate_face('D')
        temp = self.state['F'][1][:]
        self.state['F'][1] = self.state['L'][1][:]
        self.state['L'][1] = self.state['B'][1][:]
        self.state['B'][1] = self.state['R'][1][:]
        self.state['R'][1] = temp
    
    def rotate_D_prime(self):
        for _ in range(3):
            self.rotate_D()
    
    def rotate_R(self):
        self.rotate_face('R')
        temp = [self.state['U'][0][1], self.state['U'][1][1]]
        self.state['U'][0][1], self.state['U'][1][1] = self.state['F'][0][1], self.state['F'][1][1]
        self.state['F'][0][1], self.state['F'][1][1] = self.state['D'][0][1], self.state['D'][1][1]
        self.state['D'][0][1], self.state['D'][1][1] = self.state['B'][1][0], self.state['B'][0][0]
        self.state['B'][0][0], self.state['B'][1][0] = temp[1], temp[0]
    
    def rotate_R_prime(self):
        for _ in range(3):
            self.rotate_R()
    
    def rotate_L(self):
        self.rotate_face('L')
        temp = [self.state['U'][0][0], self.state['U'][1][0]]
        self.state['U'][0][0], self.state['U'][1][0] = self.state['B'][1][1], self.state['B'][0][1]
        self.state['B'][0][1], self.state['B'][1][1] = self.state['D'][1][0], self.state['D'][0][0]
        self.state['D'][0][0], self.state['D'][1][0] = self.state['F'][0][0], self.state['F'][1][0]
        self.state['F'][0][0], self.state['F'][1][0] = temp[0], temp[1]
    
    def rotate_L_prime(self):
        for _ in range(3):
            self.rotate_L()
    
    def rotate_F(self):
        self.rotate_face('F')
        temp = [self.state['U'][1][0], self.state['U'][1][1]]
        self.state['U'][1][0], self.state['U'][1][1] = self.state['L'][1][0], self.state['L'][0][0]
        self.state['L'][0][0], self.state['L'][1][0] = self.state['D'][0][1], self.state['D'][0][0]
        self.state['D'][0][0], self.state['D'][0][1] = self.state['R'][1][1], self.state['R'][0][1]
        self.state['R'][0][1], self.state['R'][1][1] = temp[0], temp[1]
    
    def rotate_F_prime(self):
        for _ in range(3):
            self.rotate_F()
    
    def rotate_B(self):
        self.rotate_face('B')
        temp = [self.state['U'][0][0], self.state['U'][0][1]]
        self.state['U'][0][0], self.state['U'][0][1] = self.state['R'][0][0], self.state['R'][1][0]
        self.state['R'][0][0], self.state['R'][1][0] = self.state['D'][1][1], self.state['D'][1][0]
        self.state['D'][1][0], self.state['D'][1][1] = self.state['L'][0][1], self.state['L'][1][1]
        self.state['L'][0][1], self.state['L'][1][1] = temp[1], temp[0]
    
    def rotate_B_prime(self):
        for _ in range(3):
            self.rotate_B()
    
    def apply_move(self, move: str):
        if move == 'U':
            self.rotate_U()
        elif move == "U'":
            self.rotate_U_prime()
        elif move == 'D':
            self.rotate_D()
        elif move == "D'":
            self.rotate_D_prime()
        elif move == 'R':
            self.rotate_R()
        elif move == "R'":
            self.rotate_R_prime()
        elif move == 'L':
            self.rotate_L()
        elif move == "L'":
            self.rotate_L_prime()
        elif move == 'F':
            self.rotate_F()
        elif move == "F'":
            self.rotate_F_prime()
        elif move == 'B':
            self.rotate_B()
        elif move == "B'":
            self.rotate_B_prime()
    
    def get_sticker(self, cubie_pos: Tuple[int, int, int], face: str) -> str:
        x, y, z = cubie_pos
        
        if face == 'U' and y == 1:
            row = 0 if z == 1 else 1
            col = 0 if x == -1 else 1
            return self.state['U'][row][col]
        elif face == 'D' and y == -1:
            row = 0 if z == -1 else 1
            col = 0 if x == -1 else 1
            return self.state['D'][row][col]
        elif face == 'F' and z == 1:
            row = 0 if y == 1 else 1
            col = 0 if x == -1 else 1
            return self.state['F'][row][col]
        elif face == 'B' and z == -1:
            row = 0 if y == 1 else 1
            col = 0 if x == 1 else 1
            return self.state['B'][row][col]
        elif face == 'L' and x == -1:
            row = 0 if y == 1 else 1
            col = 0 if z == -1 else 1
            return self.state['L'][row][col]
        elif face == 'R' and x == 1:
            row = 0 if y == 1 else 1
            col = 0 if z == 1 else 1
            return self.state['R'][row][col]
        
        return None


COLORS = {
    'W': (255, 255, 255),
    'Y': (255, 255, 0),
    'R': (255, 0, 0),
    'O': (255, 165, 0),
    'G': (0, 200, 0),
    'B': (0, 100, 255),
}

POSSIBLE_MOVES = ['U', "U'", 'D', "D'", 'R', "R'", 'L', "L'", 'F', "F'", 'B', "B'"]

def scramble_cube(cube: Cube2x2, num_moves: int = 25) -> List[str]:
    applied_moves = []
    last_move = None
    
    opposites = {
        'U': 'D', 'D': 'U',
        'L': 'R', 'R': 'L',
        'F': 'B', 'B': 'F',
    }
    
    for _ in range(num_moves):
        valid_moves = []
        for m in POSSIBLE_MOVES:
            base = m.rstrip("'")
            if last_move:
                last_base = last_move.rstrip("'")
                if base == last_base:
                    continue
                if opposites.get(base) == last_base:
                    continue
            valid_moves.append(m)
        
        move = random.choice(valid_moves)
        cube.apply_move(move)
        applied_moves.append(move)
        last_move = move
    
    return applied_moves
