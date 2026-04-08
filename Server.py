import ssl 
import socket
import json

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = False

# Load server certificate
context.load_cert_chain(certfile="certs/server_cert.pem", keyfile="certs/server_key.pem")

context.load_verify_locations(cafile="certs/ca_cert.pem")
conn = context.wrap_socket(socket.socket(), server_hostname="database")

# Debug
print("Using CA file:", "certs/ca_cert.pem")

print("Connecting to database...")
conn.connect(('localhost', 8443))

# Input sent
request_data = {
    "action": "GET", 
    "username": "SquishyDino"
}

request = json.dumps(request_data)
conn.send(request.encode())
print("INPUT (request sent to DB): ", request)

# OUTPUT response
response = conn.recv(1024).decode()
print("OUTPUT (response received from DB): ", response)
conn.close()