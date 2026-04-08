import ssl 
import socket

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

# Mock request
request = "GET password"
conn.send(request.encode())
print("Sent:", request)

# Mock response
response = conn.recv(1024).decode()
print("Received:", response)
conn.close()