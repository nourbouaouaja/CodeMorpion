import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")

BLACK = (0, 0, 0)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 150)
WHITE = (255, 255, 255)
HOVER_COLOR = (0, 255, 180)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Orbitron", 40)

PLAYER_X = "X"
PLAYER_O = "O"
EMPTY = None

board = [[EMPTY for _ in range(3)] for _ in range(3)]
current_player = PLAYER_X
game_over = False

class Particle:
    def __init__(self, x=None, y=None, color=None):
        self.x = x if x is not None else random.randint(0, WIDTH)
        self.y = y if y is not None else random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 1.5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = color if color else (0, 100, 200)
        self.life = 60

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, int(255 * (self.life / 60)))
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

particles = [Particle() for _ in range(100)]

class Button:
    def __init__(self, text, x, y, w, h, base_color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color

    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            glow_strength = 50 + int(50 * math.sin(pygame.time.get_ticks() * 0.01))
            color = (min(self.hover_color[0]+glow_strength, 255),
                     min(self.hover_color[1]+glow_strength, 255),
                     min(self.hover_color[2]+glow_strength, 255))
            self.current_color = color
        else:
            self.current_color = self.base_color

        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, NEON_PINK, self.rect, width=2, border_radius=10)

        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# Fade functions
def fade_out(surface, speed=5):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, speed):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

def fade_in(surface, speed=5):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(255, 0, -speed):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

# Menu screen (includes buttons and background music)
def menu_screen():
    pygame.mixer.music.load('AAAA.mp3')  # Ensure the music file is in the same directory
    pygame.mixer.music.play(-1, 0.0)  # Loop the music indefinitely (-1)

    start_button = Button("Start Game", WIDTH//2 - 100, HEIGHT//2 - 50, 200, 60, NEON_BLUE, HOVER_COLOR)
    quit_button = Button("Quit", WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, NEON_BLUE, HOVER_COLOR)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(mouse_pos):
                    fade_out(WINDOW)  # Fade out before starting the game
                    pygame.mixer.music.stop()  # Stop music when starting the game
                    return  # Start the game
                if quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # Background
        WINDOW.fill(BLACK)

        # Update and draw background particles
        for particle in particles:
            particle.move()
            particle.draw(WINDOW)

        # Title
        title_font = pygame.font.SysFont("Orbitron", 60)
        title_surface = title_font.render("TIC-TAC-TOE CYBERPUNK", True, NEON_PINK)
        title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
        WINDOW.blit(title_surface, title_rect)

        # Draw buttons
        start_button.draw(WINDOW, mouse_pos)
        quit_button.draw(WINDOW, mouse_pos)

        pygame.display.update()

# Draw the game board
def draw_board():
    # Draw the grid lines
    pygame.draw.line(WINDOW, NEON_BLUE, (WIDTH//3, 0), (WIDTH//3, HEIGHT), 5)
    pygame.draw.line(WINDOW, NEON_BLUE, (2 * WIDTH//3, 0), (2 * WIDTH//3, HEIGHT), 5)
    pygame.draw.line(WINDOW, NEON_BLUE, (0, HEIGHT//3), (WIDTH, HEIGHT//3), 5)
    pygame.draw.line(WINDOW, NEON_BLUE, (0, 2 * HEIGHT//3), (WIDTH, 2 * HEIGHT//3), 5)

# Draw the player symbols
def draw_symbols():
    for i in range(3):
        for j in range(3):
            x = i * WIDTH // 3 + WIDTH // 6
            y = j * HEIGHT // 3 + HEIGHT // 6
            if board[i][j] == PLAYER_X:
                pygame.draw.line(WINDOW, NEON_PINK, (x - 40, y - 40), (x + 40, y + 40), 5)
                pygame.draw.line(WINDOW, NEON_PINK, (x + 40, y - 40), (x - 40, y + 40), 5)
            elif board[i][j] == PLAYER_O:
                pygame.draw.circle(WINDOW, NEON_BLUE, (x, y), 40, 5)

# Check for a winner or draw
def check_winner():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]
    
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    return None

# Main game loop (local multiplayer)
def main_game():
    global current_player, game_over, board
    fade_in(WINDOW)  # Fade in at the start of the game
    pygame.mixer.music.stop()  # Stop menu music

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Get the grid position based on mouse click
                i, j = mouse_pos[0] // (WIDTH // 3), mouse_pos[1] // (HEIGHT // 3)

                # Only update the cell if it's empty
                if board[i][j] is None:
                    board[i][j] = current_player
                    winner = check_winner()

                    # Check for a winner or a draw
                    if winner:
                        game_over = True
                        print(f"{winner} wins!")
                    elif all(cell is not None for row in board for cell in row):
                        game_over = True
                        print("It's a draw!")
                    else:
                        # Switch player turn
                        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X

        # Draw the game background and board
        WINDOW.fill(BLACK)
        draw_board()
        draw_symbols()

        # Display the current player's turn
        turn_text = font.render(f"Player {current_player}'s turn", True, NEON_PINK)
        WINDOW.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, HEIGHT - 40))

        # Option to restart the game after a win or draw
        if game_over:
            restart_button = Button("Restart", WIDTH//2 - 100, HEIGHT//2 - 50, 200, 60, NEON_BLUE, HOVER_COLOR)
            quit_button = Button("Quit", WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, NEON_BLUE, HOVER_COLOR)

            restart_button.draw(WINDOW, mouse_pos)
            quit_button.draw(WINDOW, mouse_pos)

            if pygame.mouse.get_pressed()[0]:
                if restart_button.is_clicked(mouse_pos):
                    # Reset the board and game state for a new game
                    board = [[EMPTY for _ in range(3)] for _ in range(3)]
                    current_player = PLAYER_X
                    game_over = False
                elif quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

if __name__ == "__main__":
    menu_screen()
    main_game()
