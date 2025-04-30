import pygame
import sys
import random
import socket
import threading
import json
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 900
LINE_WIDTH = 5
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // 3

BLACK = (0, 0, 0)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (150, 0, 255)
DARK_BG = (10, 10, 30)
GRID_COLOR = (0, 100, 255, 150)
HOVER_GLOW = (0, 255, 180)
GLOW_COLORS = {
    "X": NEON_PINK,
    "O": NEON_BLUE,
    "win": NEON_GREEN
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber-Tac-Toe 2077")

class DummySound:
    def play(self): pass

try:
    move_sound = pygame.mixer.Sound("sounds/move.wav")
    win_sound = pygame.mixer.Sound("sounds/win.wav")
    error_sound = pygame.mixer.Sound("sounds/error.wav")
    button_sound = pygame.mixer.Sound("sounds/button.wav")
except:
    move_sound = win_sound = error_sound = button_sound = DummySound()

try:
    font_large = pygame.font.Font("fonts/cyberpunk.ttf", 48)
    font_medium = pygame.font.Font("fonts/cyberpunk.ttf", 32)
    font_small = pygame.font.Font("fonts/cyberpunk.ttf", 24)
except:
    font_large = pygame.font.SysFont('Arial', 48, bold=True)
    font_medium = pygame.font.SysFont('Arial', 32)
    font_small = pygame.font.SysFont('Arial', 24)

class Particle:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(HEIGHT, HEIGHT + 100)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.0)
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(150, 255),
            random.randint(50, 150)
        )
        self.life = random.randint(30, 90)
    
    def update(self):
        self.y -= self.speed
        self.life -= 1
        if self.life <= 0 or self.y < -10:
            self.reset()
    
    def draw(self, surface):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class CyberButton:
    def __init__(self, x, y, width, height, text, base_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.glow_intensity = 0
    
    def draw(self, surface):
      
        if self.is_hovered:
            self.glow_intensity = min(self.glow_intensity + 10, 50)
            glow_surf = pygame.Surface((self.rect.width+20, self.rect.height+20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.hover_color[:3], self.glow_intensity), 
                             (10, 10, self.rect.width, self.rect.height), 
                             border_radius=10)
            surface.blit(glow_surf, (self.rect.x-10, self.rect.y-10))
        else:
            self.glow_intensity = max(self.glow_intensity - 10, 0)
        
     
        color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, NEON_PINK, self.rect, 2, border_radius=10)
       
        text_surf = font_medium.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                button_sound.play()
                return True
        return False

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.current_player = "X"
        self.game_mode = None
        self.player_symbol = None
        self.connection = None
        self.server_socket = None
        self.client_socket = None
        self.host = "localhost"
        self.port = 5555
        self.ai_difficulty = "Quantum AI"
        self.game_over = False
        self.waiting_for_opponent = False
        self.status_message = "CHOOSE GAME MODE"
        self.mode_selection = True
        self.difficulty_selection = False
        self.symbol_selection = False
        self.particles = [Particle() for _ in range(150)]
        self.winning_line = None
        self.ai_thinking = False
        self.last_move_time = 0
        self.move_effects = []
        self.create_buttons()
       
        self.win_animation_time = 0
        self.ai_think_start = 0
        self.grid_pulse = 0

    def create_buttons(self):
        btn_width, btn_height = 400, 60
        self.mode_buttons = [
            CyberButton(WIDTH//2 - btn_width//2, 200, btn_width, btn_height, 
                      "NEON DUEL (1v1)", NEON_BLUE, HOVER_GLOW),
            CyberButton(WIDTH//2 - btn_width//2, 280, btn_width, btn_height, 
                      "AI OVERLORD (vs CPU)", NEON_BLUE, HOVER_GLOW),
            CyberButton(WIDTH//2 - btn_width//2, 360, btn_width, btn_height, 
                      "CYBER BATTLE (HOST)", NEON_BLUE, HOVER_GLOW),
            CyberButton(WIDTH//2 - btn_width//2, 440, btn_width, btn_height, 
                      "CYBER BATTLE (JOIN)", NEON_BLUE, HOVER_GLOW)
        ]
        
        self.difficulty_buttons = [
            CyberButton(WIDTH//2 - btn_width//2, 200, btn_width, btn_height, 
                       "BASIC DRONE", NEON_GREEN, HOVER_GLOW),
            CyberButton(WIDTH//2 - btn_width//2, 280, btn_width, btn_height, 
                       "QUANTUM AI", NEON_GREEN, HOVER_GLOW),
            CyberButton(WIDTH//2 - btn_width//2, 360, btn_width, btn_height, 
                       "NEURAL NETWORK", NEON_GREEN, HOVER_GLOW)
        ]
        
        self.symbol_buttons = [
            CyberButton(WIDTH//2 - 220, 250, 200, 120, "X", 
                       NEON_PINK, (255, 100, 255)),
            CyberButton(WIDTH//2 + 20, 250, 200, 120, "O", 
                       NEON_BLUE, (100, 255, 255))
        ]
        
        self.reset_button = CyberButton(WIDTH//2 - 220, HEIGHT-120, 200, 50, 
                                      "RESET", NEON_BLUE, HOVER_GLOW)
        self.menu_button = CyberButton(WIDTH//2 + 20, HEIGHT-120, 200, 50, 
                                     "MENU", NEON_PURPLE, (200, 0, 255))
        self.back_button = CyberButton(20, HEIGHT-70, 120, 50, 
                                     "BACK", NEON_PURPLE, (200, 0, 255))

    def draw_board(self):
      
        self.grid_pulse = (self.grid_pulse + 0.01) % (2 * math.pi)
        pulse_alpha = 100 + int(50 * math.sin(self.grid_pulse))
        
        grid_surface = pygame.Surface((WIDTH, 3*SQUARE_SIZE), pygame.SRCALPHA)
  
        for i in range(1, 3):
            pygame.draw.line(grid_surface, (*GRID_COLOR[:3], pulse_alpha), 
                            (i*SQUARE_SIZE, 0), (i*SQUARE_SIZE, 3*SQUARE_SIZE), 
                            LINE_WIDTH+2)
            for j in range(3):
                pygame.draw.line(grid_surface, (*GRID_COLOR[:3], 30), 
                                (i*SQUARE_SIZE+j-1, 0), (i*SQUARE_SIZE+j-1, 3*SQUARE_SIZE), 
                                LINE_WIDTH)

        for i in range(1, 3):
            pygame.draw.line(grid_surface, (*GRID_COLOR[:3], pulse_alpha), 
                            (0, i*SQUARE_SIZE), (WIDTH, i*SQUARE_SIZE), 
                            LINE_WIDTH+2)
            for j in range(3):
                pygame.draw.line(grid_surface, (*GRID_COLOR[:3], 30), 
                                (0, i*SQUARE_SIZE+j-1), (WIDTH, i*SQUARE_SIZE+j-1), 
                                LINE_WIDTH)
        
        screen.blit(grid_surface, (0, 0))
        current_time = pygame.time.get_ticks()
        for i in range(9):
            row = i // 3
            col = i % 3
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            
            if self.board[i] == "X":
                
                if current_time - self.last_move_time < 500 and i == self.last_move:
                    for size in range(65, 30, -5):
                        alpha = min(255, size * 4)
                        pygame.draw.line(screen, (*NEON_PINK[:3], alpha), 
                                        (center_x - size, center_y - size), 
                                        (center_x + size, center_y + size), 
                                        LINE_WIDTH+3)
                        pygame.draw.line(screen, (*NEON_PINK[:3], alpha), 
                                        (center_x + size, center_y - size), 
                                        (center_x - size, center_y + size), 
                                        LINE_WIDTH+3)
                
                for size in range(45, 30, -5):
                    alpha = size - 30
                    pygame.draw.line(screen, (*NEON_PINK[:3], alpha), 
                                    (center_x - size, center_y - size), 
                                    (center_x + size, center_y + size), 
                                    LINE_WIDTH+3)
                    pygame.draw.line(screen, (*NEON_PINK[:3], alpha), 
                                    (center_x + size, center_y - size), 
                                    (center_x - size, center_y + size), 
                                    LINE_WIDTH+3)
                
                pygame.draw.line(screen, NEON_PINK, 
                                (center_x - 40, center_y - 40), 
                                (center_x + 40, center_y + 40), 
                                LINE_WIDTH+5)
                pygame.draw.line(screen, NEON_PINK, 
                                (center_x + 40, center_y - 40), 
                                (center_x - 40, center_y + 40), 
                                LINE_WIDTH+5)
            
            elif self.board[i] == "O":
                pulse = int(5 * math.sin(current_time * 0.005))
                if current_time - self.last_move_time < 500 and i == self.last_move:
                    for radius in range(65, 30, -5):
                        alpha = min(255, radius * 4)
                        pygame.draw.circle(screen, (*NEON_BLUE[:3], alpha), 
                                         (center_x, center_y), radius + pulse, 
                                         LINE_WIDTH+3)
                
                for radius in range(45, 30, -5):
                    alpha = radius - 30
                    pygame.draw.circle(screen, (*NEON_BLUE[:3], alpha), 
                                     (center_x, center_y), radius + pulse, 
                                     LINE_WIDTH+3)
                
                pygame.draw.circle(screen, NEON_BLUE, 
                                 (center_x, center_y), 40 + pulse, 
                                 LINE_WIDTH+5)
        
        if self.game_over and self.winning_line:
            start_pos, end_pos = self.winning_line
            win_alpha = min(255, 100 + int(155 * abs(math.sin(current_time * 0.005))))
            pygame.draw.line(screen, (*NEON_GREEN[:3], win_alpha), 
                            start_pos, end_pos, LINE_WIDTH+5)
            
            if random.random() < 0.4:
                progress = random.random()
                spark_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                spark_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                spark_size = random.randint(2, 5)
                pygame.draw.circle(screen, BLACK, (int(spark_x), int(spark_y)), spark_size)

    def check_winner(self):
       
        for row in range(3):
            if self.board[row*3] == self.board[row*3+1] == self.board[row*3+2] != " ":
                start_pos = (30, (row + 0.5) * SQUARE_SIZE)
                end_pos = (WIDTH - 30, (row + 0.5) * SQUARE_SIZE)
                self.winning_line = (start_pos, end_pos)
                return self.board[row*3]
        
        for col in range(3):
            if self.board[col] == self.board[col+3] == self.board[col+6] != " ":
                start_pos = ((col + 0.5) * SQUARE_SIZE, 30)
                end_pos = ((col + 0.5) * SQUARE_SIZE, 3*SQUARE_SIZE - 30)
                self.winning_line = (start_pos, end_pos)
                return self.board[col]
        
        if self.board[0] == self.board[4] == self.board[8] != " ":
            start_pos = (30, 30)
            end_pos = (WIDTH - 30, 3*SQUARE_SIZE - 30)
            self.winning_line = (start_pos, end_pos)
            return self.board[0]
        if self.board[2] == self.board[4] == self.board[6] != " ":
            start_pos = (WIDTH - 30, 30)
            end_pos = (30, 3*SQUARE_SIZE - 30)
            self.winning_line = (start_pos, end_pos)
            return self.board[2]
        
        if " " not in self.board:
            return "Tie"
        
        return None

    def make_move(self, position):
        if self.board[position] == " " and not self.game_over:
            self.board[position] = self.current_player
            self.last_move = position
            self.last_move_time = pygame.time.get_ticks()
            move_sound.play()
            
            winner = self.check_winner()
            if winner:
                self.game_over = True
                if winner == "Tie":
                    self.status_message = "SYSTEM STALEMATE"
                else:
                    self.status_message = f"PLAYER {winner} DOMINATES"
                    win_sound.play()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                if self.game_mode == "online" and self.current_player != self.player_symbol:
                    self.waiting_for_opponent = True
                    self.send_move(position)
                else:
                    self.waiting_for_opponent = False
            
            return True
        else:
            error_sound.play()
            return False

    def easy_ai_move(self):
        available_moves = [i for i, spot in enumerate(self.board) if spot == " "]
        return random.choice(available_moves) if available_moves else None

    def medium_ai_move(self):
      
        for i in range(9):
            if self.board[i] == " ":
                self.board[i] = "O"
                if self.check_winner() == "O":
                    self.board[i] = " "
                    return i
                self.board[i] = " "
       
        for i in range(9):
            if self.board[i] == " ":
                self.board[i] = "X"
                if self.check_winner() == "X":
                    self.board[i] = " "
                    return i
                self.board[i] = " "
   
        return self.easy_ai_move()

    def hard_ai_move(self):
        best_score = -float('inf')
        best_move = None
        
        for i in range(9):
            if self.board[i] == " ":
                self.board[i] = "O"
                score = self.minimax(self.board, 0, False)
                self.board[i] = " "
                if score > best_score:
                    best_score = score
                    best_move = i
        
        return best_move if best_move is not None else self.easy_ai_move()

    def minimax(self, board, depth, is_maximizing):
        result = self.check_winner()
        if result == "O":
            return 1
        elif result == "X":
            return -1
        elif result == "Tie":
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] == " ":
                    board[i] = "O"
                    score = self.minimax(board, depth + 1, False)
                    board[i] = " "
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == " ":
                    board[i] = "X"
                    score = self.minimax(board, depth + 1, True)
                    board[i] = " "
                    best_score = min(score, best_score)
            return best_score

    def ai_move(self):
        if self.ai_difficulty == "Basic Drone":
            return self.easy_ai_move()
        elif self.ai_difficulty == "Quantum AI":
            return self.medium_ai_move()
        else:
            return self.hard_ai_move()

    def host_game(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.status_message = f"AWAITING CONNECTION ON PORT {self.port}..."
        
        threading.Thread(target=self.accept_connection, daemon=True).start()
        
        self.player_symbol = "X"
        self.current_player = "X"
        self.game_mode = "online"

    def accept_connection(self):
        self.client_socket, addr = self.server_socket.accept()
        self.status_message = f"CONNECTION ESTABLISHED: {addr[0]}"
        self.waiting_for_opponent = False

    def join_game(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            self.status_message = "CONNECTED TO SERVER"
            
            self.player_symbol = "O"
            self.current_player = "X"
            self.game_mode = "online"
            self.waiting_for_opponent = True
        except Exception as e:
            self.status_message = f"CONNECTION FAILED: {str(e)}"
            self.mode_selection = True
            self.game_mode = None

    def send_move(self, position):
        data = json.dumps({"move": position})
        self.client_socket.send(data.encode())

    def receive_move(self):
        try:
            data = self.client_socket.recv(1024).decode()
            if not data:
                return None
            return json.loads(data)["move"]
        except:
            return None

    def reset_game(self):
        self.board = [" " for _ in range(9)]
        self.game_over = False
        self.current_player = "X"
        self.waiting_for_opponent = False
        self.winning_line = None
        if self.game_mode == "online" and self.player_symbol == "O":
            self.waiting_for_opponent = True
        self.status_message = "SYSTEM RESET"

    def draw_menu(self):
       
        screen.fill(DARK_BG)
        for particle in self.particles:
            particle.update()
            particle.draw(screen)
        
        title_text = "CYBER-TAC-TOE 2077"
        for i in range(10, 0, -2):
            title = font_large.render(title_text, True, (*NEON_PINK[:3], i*25))
            screen.blit(title, (WIDTH//2 - title.get_width()//2 + 2, 50 + 2))
        title = font_large.render(title_text, True, NEON_PINK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
       
        status = font_medium.render(self.status_message, True, NEON_BLUE)
        screen.blit(status, (WIDTH//2 - status.get_width()//2, 120))
        
        mouse_pos = pygame.mouse.get_pos()
        
        if self.mode_selection:
            for button in self.mode_buttons:
                button.check_hover(mouse_pos)
                button.draw(screen)
        elif self.difficulty_selection:
            for button in self.difficulty_buttons:
                button.check_hover(mouse_pos)
                button.draw(screen)
        elif self.symbol_selection:
            for button in self.symbol_buttons:
                button.check_hover(mouse_pos)
                button.draw(screen)
        
        self.back_button.check_hover(mouse_pos)
        self.back_button.draw(screen)

    def draw_game(self):
 
        screen.fill(DARK_BG)
        for particle in self.particles:
            particle.update()
            particle.draw(screen)
        
        self.draw_board()
        
        status_bg = pygame.Surface((WIDTH - 40, 60), pygame.SRCALPHA)
        status_bg.fill((0, 0, 0, 150))
        pygame.draw.rect(status_bg, (*NEON_BLUE[:3], 50), (0, 0, WIDTH-40, 60), 2)
        screen.blit(status_bg, (20, HEIGHT-150))
        
        if self.waiting_for_opponent:
            status_text = "AWAITING OPPONENT..."
            status_color = NEON_BLUE
          
            loading_width = int((pygame.time.get_ticks() % 2000) / 2000 * (WIDTH-100))
            pygame.draw.rect(screen, NEON_BLUE, (50, HEIGHT-100, loading_width, 5))
        elif self.game_over:
            status_text = self.status_message
            status_color = NEON_GREEN
        else:
            status_text = f"PLAYER {self.current_player}'S TURN"
            status_color = NEON_PINK if self.current_player == "X" else NEON_BLUE
        
        status = font_medium.render(status_text, True, status_color)
        screen.blit(status, (WIDTH//2 - status.get_width()//2, HEIGHT-140))
    
        mouse_pos = pygame.mouse.get_pos()
        self.reset_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)
        self.reset_button.draw(screen)
        self.menu_button.draw(screen)
        
        if self.ai_thinking and self.game_mode == "ai" and self.current_player != self.player_symbol:
            thinking_text = font_small.render("AI PROCESSING...", True, NEON_GREEN)
            screen.blit(thinking_text, (WIDTH//2 - thinking_text.get_width()//2, HEIGHT-80))
          
            binary = "".join(random.choice("01") for _ in range(16))
            binary_text = font_small.render(binary, True, (*NEON_GREEN[:3], 100))
            screen.blit(binary_text, (WIDTH//2 - binary_text.get_width()//2, HEIGHT-50))

    def return_to_menu(self):
        self.mode_selection = True
        self.difficulty_selection = False
        self.symbol_selection = False
        self.game_mode = None
        self.status_message = "CHOOSE GAME MODE"
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        self.reset_game()

game = TicTacToe()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        mouse_pos = pygame.mouse.get_pos()
        
        if game.mode_selection or game.difficulty_selection or game.symbol_selection:
            
            if game.back_button.is_clicked(mouse_pos, event):
                if game.difficulty_selection or game.symbol_selection:
                    game.mode_selection = True
                    game.difficulty_selection = False
                    game.symbol_selection = False
                    game.status_message = "CHOOSE GAME MODE"
            
            elif game.mode_selection:
                for i, button in enumerate(game.mode_buttons):
                    if button.is_clicked(mouse_pos, event):
                        if i == 0:
                            game.game_mode = "friend"
                            game.player_symbol = "X"
                            game.current_player = "X"
                            game.mode_selection = False
                            game.status_message = "PLAYER X'S TURN"
                        elif i == 1:
                            game.game_mode = "ai"
                            game.difficulty_selection = True
                            game.mode_selection = False
                            game.status_message = "SELECT AI DIFFICULTY"
                        elif i == 2:
                            game.host_game()
                            game.mode_selection = False
                        elif i == 3:
                            game.join_game()
                            game.mode_selection = False
            
            elif game.difficulty_selection:
                for i, button in enumerate(game.difficulty_buttons):
                    if button.is_clicked(mouse_pos, event):
                        game.ai_difficulty = button.text
                        game.symbol_selection = True
                        game.difficulty_selection = False
                        game.status_message = "SELECT YOUR SYMBOL"
            
            elif game.symbol_selection:
                for i, button in enumerate(game.symbol_buttons):
                    if button.is_clicked(mouse_pos, event):
                        game.player_symbol = "X" if i == 0 else "O"
                        game.current_player = "X"
                        game.symbol_selection = False
                        game.status_message = "PLAYER X'S TURN"
        
        elif not game.game_over and not game.waiting_for_opponent:
          
            if mouse_pos[1] < 3 * SQUARE_SIZE:
                clicked_row = mouse_pos[1] // SQUARE_SIZE
                clicked_col = mouse_pos[0] // SQUARE_SIZE
                position = clicked_row * 3 + clicked_col
                
                if game.board[position] == " ":
                    if game.game_mode == "friend":
                        game.make_move(position)
                    elif game.game_mode == "ai":
                        if game.current_player == game.player_symbol:
                            game.make_move(position)
                            if not game.game_over and game.current_player != game.player_symbol:
                              
                                game.ai_thinking = True
                                pygame.time.delay(500) 
                                ai_position = game.ai_move()
                                if ai_position is not None:
                                    game.make_move(ai_position)
                                game.ai_thinking = False
                    elif game.game_mode == "online":
                        if game.current_player == game.player_symbol:
                            game.make_move(position)
            
            if game.reset_button.is_clicked(mouse_pos, event):
                game.reset_game()
            
            if game.menu_button.is_clicked(mouse_pos, event):
                game.return_to_menu()
        
        elif game.game_over:
           
            if game.reset_button.is_clicked(mouse_pos, event):
                game.reset_game()
            
            if game.menu_button.is_clicked(mouse_pos, event):
                game.return_to_menu()
    
    if game.game_mode == "online" and game.waiting_for_opponent and not game.game_over:
        position = game.receive_move()
        if position is not None:
            game.make_move(position)
            game.waiting_for_opponent = False
    
    if game.mode_selection or game.difficulty_selection or game.symbol_selection:
        game.draw_menu()
    else:
        game.draw_game()
    
    pygame.display.update()

pygame.quit()
sys.exit()