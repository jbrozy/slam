import threading

from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher


class Receiver(threading.Thread):
    """
    Asynchronous OSC Receiver
    """
    def __init__(self, ip, port):
    """
    Create a OSC Receiver that listens asynchronously
    """
        super().__init__()
        self.dispatcher = Dispatcher()
        self.server = osc_server.ThreadingOSCUDPServer(
                (ip, port),
                self.dispatcher)
        self.running = False

    def map(self, route, fn):
        """
        Maps the given route to the given function
        """
        self.dispatcher.map(route, fn)

    def run(self):
        """
        Run the receiver with threading
        """
        self.running = True
        print(f"Serving on {self.server.server_address}")
        while self.running:
            self.server.handle_request()

    def stop(self):
        self.running = False
        print("Stopping server...")
