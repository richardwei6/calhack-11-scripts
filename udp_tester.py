import socket

def send_message(host, port, message):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((host, port))
        print(f'Connected to server at {host}:{port}')

        # Send the message
        client_socket.sendall(message.encode())
        print(f'Sent message: {message}')

    finally:
        client_socket.close()
        print('Connection closed')

if __name__ == '__main__':
    # Replace with the server's public IP address
    server_ip = '172.56.43.118'
    server_port = 53
    message = 'Hello, Server!'
    
    send_message(server_ip, server_port, message)