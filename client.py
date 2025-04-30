import socket
import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Tic-Tac-Toe')

WHITE = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
X_COLOR = (242, 85, 96)
O_COLOR = (28, 170, 156)

board = [[None, None, None], [None, None, None], [None, None, None]]
player_turn = 'X'

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost',5555))
    return client

def draw_grid():
    pygame.draw.line(screen, LINE_COLOR, (200, 0), (200, 600), 5)
    pygame.draw.line(screen, LINE_COLOR, (400, 0), (400, 600), 5)
    pygame.draw.line(screen, LINE_COLOR, (0, 200), (600, 200), 5)
    pygame.draw.line(screen, LINE_COLOR, (0, 400), (600, 400), 5)

def draw_marks():
    font = pygame.font.Font(None, 150)
    for row in range(3):
        for col in range(3):
            if board[row][col]:
                text = font.render(board[row][col], True, X_COLOR if board[row][col] == 'X' else O_COLOR)
                screen.blit(text, (col * 200 + 50, row * 200 + 50))

def update_board(client):
    global board
    board_state = client.recv(1024).decode('utf-8')
    board = eval(board_state)  

client = connect_to_server()
while True:
    screen.fill(WHITE)
    draw_grid()
    draw_marks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = y // 200, x // 200
            if board[row][col] is None and player_turn == 'X': 
                client.send(f"{row},{col}".encode('utf-8'))
                update_board(client)
                player_turn = 'O'
    
    pygame.display.update()
