from OpenSSL import crypto

def inject_into_urllib3():
    from urllib3 import util
    from urllib3.contrib.pyopenssl import PyOpenSSLContext, HAS_SNI

    class MyPyOpenSSLContext(PyOpenSSLContext):
        def load_cert_chain(self, certfile, keyfile=None, password=None):
            self._ctx.set_passwd_cb(lambda max_length, prompt_twice, userdata: password)
            if isinstance(certfile, crypto.X509):
                self._ctx.use_certificate(certfile)
                if keyfile is None:
                    raise ValueError('keyfile must be specified when certfile is an X509 object')
            else:
                self._ctx.use_certificate_file(certfile)
                if keyfile is None:
                    keyfile = certfile
            if isinstance(keyfile, crypto.PKey):
                self._ctx.use_privatekey(keyfile)
            else:
                self._ctx.use_privatekey_file(keyfile)

    util.ssl_.SSLContext = MyPyOpenSSLContext
    util.HAS_SNI = HAS_SNI
    util.ssl_.HAS_SNI = HAS_SNI
    util.IS_PYOPENSSL = True
    util.ssl_.IS_PYOPENSSL = True
