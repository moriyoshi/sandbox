import urllib3
from OpenSSL import crypto, SSL
from client import inject_into_urllib3
from certs import srv_c, cli_c

inject_into_urllib3()


def run_server():
    from http import HTTPStatus
    from threading import Thread
    from http.server import BaseHTTPRequestHandler
    from server import HTTPSServer

    open('cli.crt.pem', 'wb').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cli_c.cert))

    class MyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', '%d' % 7)
            self.end_headers()
            self.wfile.write(b"HEYHEY\n")

    srv_ctx = SSL.Context(SSL.TLSv1_2_METHOD)
    srv_ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, lambda *args: True)
    srv_ctx.use_certificate(srv_c.cert)
    srv_ctx.use_privatekey(srv_c.key)
    srv_ctx.load_verify_locations('cli.crt.pem')

    srv = HTTPSServer(('127.0.0.1', 9443), MyHandler, ctx=srv_ctx)
    Thread(target=srv.serve_forever).start()
    return srv

def run_client():
    with urllib3.PoolManager(cert_file=cli_c.cert, key_file=cli_c.key) as p:
        assert p.request('GET', 'https://127.0.0.1:9443').data == b'HEYHEY\n'


if __name__ == '__main__':
    srv = run_server()
    run_client()
    srv.shutdown()
