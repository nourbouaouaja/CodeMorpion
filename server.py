import socket
import threading

board = [[None, None, None], [None, None, None], [None, None, None]]
player_turn = 'X'  
client1 = None
client2 = None

def handle_client(client, player):
    global player_turn
    while True:
        move = client.recv(1024).decode('utf-8')
        if not move:
            break
        row, col = map(int, move.split(','))
        if board[row][col] is None:
            board[row][col] = player_turn
            print(f"Player {player_turn} moved: {row}, {col}")
            player_turn = 'O' if player_turn == 'X' else 'X'
            send_board(client1)
            send_board(client2)
        if check_win():
            send_message(client, f"Player {player_turn} wins!")
            break
    client.close()

def send_board(client):
    board_state = str(board)
    client.send(board_state.encode('utf-8'))

def send_message(client, message):
    client.send(message.encode('utf-8'))

def check_win():
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not None:
            return True
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return True
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return True
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return True
    return False

def start_server():
    global client1, client2
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))  
    server.listen(2) 
    print("Server listening on port 5555...")

    client1, addr1 = server.accept()
    print(f"Player 1 connected from {addr1}")
    client1.send("You are Player 1 (X)".encode('utf-8'))
    send_board(client1)

    client2, addr2 = server.accept()
    print(f"Player 2 connected from {addr2}")
    client2.send("You are Player 2 (O)".encode('utf-8'))
    send_board(client2)

    threading.Thread(target=handle_client, args=(client1, 'X')).start()
    threading.Thread(target=handle_client, args=(client2, 'O')).start()

if __name__ == "__main__":
    start_server()
