import ssl
import socket
import json

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

        # INPUT received
        data = conn.recv(1024).decode()
        print("INPUT (request received from server): ", data)
        request = json.loads(data)

        # Mock response
        response_data = {
            "status": "success", 
            "password": "SquishyDino_Password"
        }

        response = "Password received"
        response = json.dumps(response_data)

        # OUTPUT sent
        print("OUTPUT (response sent to server): ", response)
        conn.send(response.encode())
    
    except ssl.SSLError as e:
        print("SSL error:", e)

    finally:
        conn.close()