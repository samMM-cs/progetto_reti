import socket

HOST = '0.0.0.0'
PORT = 5555
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print("Server S1 in listening mode on port", PORT)
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Ricevuto: {data.decode()}")
            conn.sendall(data)       # Invia i dati ricevuti (echo)
