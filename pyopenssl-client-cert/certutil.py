from OpenSSL import crypto

class PKIEntity:
    def __init__(self, key, cert):
        self.key = key
        self.cert = cert
        self.serial = 1


def to_cert_timestamp(dt):
    if dt.tzinfo is None:
        raise ValueError('naive timezone')
    return dt.strftime('%Y%m%d%H%M%S%z').encode('ascii')

def certificate_authority(x509, **params):
    x509.add_extensions([
        crypto.X509Extension(b'basicConstraints', True, b'CA:TRUE'),
        crypto.X509Extension(b'keyUsage', False, b'digitalSignature,keyCertSign,cRLSign'),
        ])

def server_cert(x509, **params):
    extensions = [
        crypto.X509Extension(b'basicConstraints', True, b'CA:FALSE'),
        crypto.X509Extension(b'keyUsage', False, b'digitalSignature,dataEncipherment,keyEncipherment'),
        crypto.X509Extension(b'extendedKeyUsage', False, b'serverAuth,clientAuth'),
        ]
    san = params.get('san')
    if san is not None:
        extensions.append(crypto.X509Extension(b'subjectAltName', False, ','.join(san).encode('ascii')))
    x509.add_extensions(extensions)

def client_cert(x509, **params):
    x509.add_extensions([
        crypto.X509Extension(b'basicConstraints', True, b'CA:FALSE'),
        crypto.X509Extension(b'keyUsage', False, b'digitalSignature,dataEncipherment,keyEncipherment'),
        crypto.X509Extension(b'extendedKeyUsage', False, b'clientAuth'),
        ])


def make_subject(
        commonName,
        countryName='',
        stateOrProvinceName='',
        localityName='',
        organizationName='',
        organizationalUnitName='',
        emailAddress=None):
    from OpenSSL._util import ffi as _ffi, lib as _lib
    name = crypto.X509Name.__new__(crypto.X509Name)
    name._name = _ffi.gc(_lib.X509_NAME_new(), _lib.X509_NAME_free)
    if countryName:
        name.countryName = countryName
    if stateOrProvinceName:
        name.stateOrProvinceName = stateOrProvinceName
    if localityName:
        name.localityName = localityName
    if organizationName:
        name.organizationName = organizationName
    if organizationalUnitName:
        name.organizationalUnitName = organizationalUnitName
    if commonName:
        name.commonName = commonName
    if emailAddress:
        name.emailAddress = emailAddress
    return name


def gen_cert(subject, not_before, not_after, purpose=server_cert, signer=None, digest='sha256', **params):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    cert.set_version(3)
    cert.set_subject(subject)
    me = PKIEntity(key, cert)
    if signer is None:
        signer = me
    cert.set_pubkey(key)
    cert.set_subject(subject)
    cert.set_issuer(signer.cert.get_subject())
    purpose(cert, **params)
    cert.set_serial_number(signer.serial)
    cert.set_notBefore(to_cert_timestamp(not_before))
    cert.set_notAfter(to_cert_timestamp(not_after))
    cert.sign(signer.key, digest)
    signer.serial += 1
    return me
