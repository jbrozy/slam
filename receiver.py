import threading

from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher


class Receiver(threading.Thread):
    def __init__(self, ip, port):
        super().__init__()
        self.dispatcher = Dispatcher()
        self.server = osc_server.ThreadingOSCUDPServer(
                (ip, port),
                self.dispatcher)
        self.running = False

    def map(self, route, fn):
        self.dispatcher.map(route, fn)

    def run(self):
        self.running = True
        print(f"Serving on {self.server.server_address}")
        while self.running:
            self.server.handle_request()

    def stop(self):
        self.running = False
        print("Stopping server...")
