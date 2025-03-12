import socket
import sys

data_storage = []
prevent_scraping = '--prevent-scraping' in sys.argv

def handle_client_connection(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    headers = request.split('\r\n')
    
    
    print("Received request:")
    print(request)
    
  
    user_agent = None
    for header in headers:
        if header.startswith('User-Agent:'):
            user_agent = header
            break
    
    if prevent_scraping and user_agent and 'curl' in user_agent.lower():
        response = "HTTP/1.1 401 Unauthorized\r\n\r\n"
        client_socket.send(response.encode('utf-8'))
        client_socket.close()
        print("Blocked a curl request with 401 Unauthorized\n")
        return
    
    if request.startswith('POST'):
        content_length = int(next((header.split(": ")[1] for header in headers if header.startswith('Content-Length')), 0))
        body = request.split('\r\n\r\n')[1][:content_length]
        data_storage.append(body)
        client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
    
    elif request.startswith('GET'):
        response_body = '\n'.join(data_storage)
        response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
        client_socket.send(response.encode('utf-8'))
    
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8080))
    server_socket.listen(5)
    print("Listening on port 8080...")
    
    while True:
        client_socket, addr = server_socket.accept()
        handle_client_connection(client_socket)

if __name__ == "__main__":
    start_server()

