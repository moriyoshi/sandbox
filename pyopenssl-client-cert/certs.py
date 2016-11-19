from dateutil import tz
from certutil import gen_cert, make_subject, certificate_authority, server_cert, client_cert
from datetime import datetime, timedelta
from OpenSSL import crypto

UTC = tz.tzutc()

now = datetime.utcnow().replace(tzinfo=UTC)


address = dict(
    countryName='JP',
    stateOrProvinceName='Tokyo',
    localityName='Shibuya-ku',
    organizationName='XXX'
    )

ca = gen_cert(
    make_subject('CA', **address),
    now, now + timedelta(days=365),
    purpose=certificate_authority
    )
srv_c = gen_cert(
    make_subject('localhost', **address),
    now, now + timedelta(days=365),
    purpose=server_cert,
    signer=ca,
    san=[
        'DNS:localhost.localdomain',
        ]
    )
cli_c = gen_cert(
    make_subject('client', **address),
    now, now + timedelta(days=365),
    purpose=client_cert,
    signer=ca
    )
