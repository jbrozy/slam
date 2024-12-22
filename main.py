from receiver import Receiver

receiver = Receiver("127.0.0.1", 1234)


def pong(*args):
    print("pong", args)


receiver.map("/ping/", pong)
receiver.start()

try:
    while True:
        pass  # Keep the main thread alive
except KeyboardInterrupt:
    receiver.stop()  # Gracefully stop the server
    receiver.join()  # Wait for the thread to finish
