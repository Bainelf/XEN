import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 27000))
print("👁️ RADAR BRUT ACTIF - J'affiche TOUT ce qui passe...")
while True:
    data, _ = s.recvfrom(4096)
    print(data.decode('utf-8', errors='ignore').strip())
