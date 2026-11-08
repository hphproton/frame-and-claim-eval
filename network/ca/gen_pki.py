"""Build-time PKI for the internal CA: one root and one issuing CA, both synthetic.

The issuing key stays in this image under /var/lib/ca. It is not copied to any
task container. The root key is discarded after it signs the issuing CA. The
files are written once per image build.
"""
import datetime as dt, os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

OUT = "/var/lib/ca"


def name(common_name):
    return x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "micro1 eval (synthetic)"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])


def write(path, data):
    with open(path, "wb") as handle:
        handle.write(data)


def key_usage():
    return x509.KeyUsage(
        digital_signature=True, content_commitment=False, key_encipherment=False,
        data_encipherment=False, key_agreement=False, key_cert_sign=True, crl_sign=True,
        encipher_only=False, decipher_only=False)


def main():
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    start = now - dt.timedelta(days=30)
    root_key = ec.generate_private_key(ec.SECP256R1())
    root = (
        x509.CertificateBuilder()
        .subject_name(name("micro1 eval internal root"))
        .issuer_name(name("micro1 eval internal root"))
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(now + dt.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(key_usage(), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), critical=False)
        .sign(root_key, hashes.SHA256())
    )
    issuer_key = ec.generate_private_key(ec.SECP256R1())
    issuer = (
        x509.CertificateBuilder()
        .subject_name(name("micro1 eval internal issuing CA"))
        .issuer_name(root.subject)
        .public_key(issuer_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(now + dt.timedelta(days=3000))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(key_usage(), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(issuer_key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), critical=False)
        .sign(root_key, hashes.SHA256())
    )
    pem = serialization.Encoding.PEM
    write(f"{OUT}/root.pem", root.public_bytes(pem))
    write(f"{OUT}/issuer.pem", issuer.public_bytes(pem))
    write(f"{OUT}/issuer.key", issuer_key.private_bytes(
        encoding=pem, format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    os.chmod(f"{OUT}/issuer.key", 0o600)


if __name__ == "__main__":
    main()
