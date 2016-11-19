import io
import socket
from socketserver import TCPServer
from http.server import HTTPServer
from OpenSSL import SSL


class SSLConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def __getattr__(self, k):
        return getattr(self.conn, k)

    def shutdown(self, _):
        return self.conn.shutdown()

    def makefile(self, mode, buffering=None, *, encoding=None, errors=None, newline=None):
        sio = socket.SocketIO(self.conn, mode)
        if buffering is None or buffering < 0:
            buffering = io.DEFAULT_BUFFER_SIZE
        if buffering == 0:
            return sio
        if 'r' in mode:
            if 'w' in mode:
                f = io.BufferedRWPair(sio, sio, buffering)
            else:
                f = io.BufferedReader(sio, buffering)
        elif 'w' in mode:
            f = io.BufferedWriter(sio, buffering)
        else:
            raise ValueError('invalid mode: %s' % mode)
        if 'b' not in mode:
            f = io.TextIOWrapper(
                f,
                encoding=encoding,
                errors=errors,
                newline=newline
                )
            f.mode = mode
        return f
        


class TLSServer(TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, *, ctx):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.ctx = ctx

    def get_request(self):
        cli_sock, addr = super().get_request()
        conn = SSLConnectionWrapper(SSL.Connection(self.ctx, cli_sock))
        conn.set_accept_state()
        return conn, addr


class HTTPSServer(TLSServer):
    allow_reuse_address = True

    server_bind = HTTPServer.server_bind
