import ssl
import socket

# Server specific SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load DB certificate and key
context.load_cert_chain(certfile="certs/db_cert.pem", keyfile="certs/db_key.pem")

context.load_verify_locations("certs/ca_cert.pem")
context.verify_mode = ssl.CERT_REQUIRED

bindsocket = socket.socket()
bindsocket.bind(('localhost', 8443))
bindsocket.listen(5)
print("Database server running on port 8443")

while True: 
    newsocket, fromaddr = bindsocket.accept()
    try:
        conn = context.wrap_socket(newsocket, server_side=True)

        print("\nClient authenticated:")
        print(conn.getpeercert())
        data = conn.recv(1024)
        print("Received request:", data.decode())

        # Mock DB response
        response = "Password received"
        conn.send(response.encode())
        conn.close()
    
    except ssl.SSLError as e:
        print("SSL error:", e)