import http.server

class PyriHttpServer():
    """
    Provides HTTP and HTTPS server    
    """

    def __init__(self, pyri_core, webui_static_dir, http_port, https_port, https_cert):
        self._core = pyri_core
        self._webui_static_dir
        self._http_port = http_port
        self._https_port = https_port
        self._https_cert = https_cert

    def start(self):
        pass

    def stop(self):
        pass

    