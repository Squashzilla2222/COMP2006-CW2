from cryptography import x509 # x509 is the standard format for TLS when making certs
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

# Builds the Public Key Infrastructure (PKI)

# Creates certs folder
os.makedirs("certs", exist_ok=True)

def create_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Save private key
def write_key(key, filename):
    with open(filename, "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))

# Save certificate in PEM format
def write_cert(cert, filename):
    with open(filename, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

# Create personal Certificate Authority (CA)
def create_ca():
    key = create_key()

    # The CA is self-signed (subject = issuer)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"Personal CA")])

    cert = (x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key()) # Link cert to CA public key
            .serial_number(x509.random_serial_number()) # Unique identifier for cert
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)) # Valid for 1 year
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True) 
            .add_extension(x509.KeyUsage(digital_signature=True, key_encipherment=True, key_cert_sign=True, key_agreement=False, content_commitment=False, data_encipherment=False, encipher_only=False, decipher_only=False, crl_sign=True), critical=True) # Allows CA to sign other certificates
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .sign(key, hashes.SHA256()) # CA self-signs cert
            )
    
    # Save CA
    write_key(key, "certs/ca_key.pem")
    write_cert(cert, "certs/ca_cert.pem")

    return key, cert

# Create the signed certificate function
def create_cert(common_name, ca_key, ca_cert, cert_file, key_file):
    key = create_key()

    # What actually gets checked during authentication
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    cert = (x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject) # CA signs certs establishing a chain of trust
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=True, key_encipherment=True, key_cert_sign=False, key_agreement=True, content_commitment=False, data_encipherment=False, encipher_only=False, decipher_only=False, crl_sign=False), critical=True) # Allows TLS authentication
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False) # Links cert back to CA
            .sign(ca_key, hashes.SHA256())
            )
    
    write_key(key, key_file)
    write_cert(cert, cert_file)

# run to generate certificate
if __name__ == "__main__":
    ca_key, ca_cert = create_ca()

    create_cert("database", ca_key, ca_cert, "certs/db_cert.pem", "certs/db_key.pem")
    create_cert("server", ca_key, ca_cert, "certs/server_cert.pem", "certs/server_key.pem")
    print("Certificates generated successfully.")