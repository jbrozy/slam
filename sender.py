from pythonosc import udp_client


def send(ip, port, namespace, *args):
    client = udp_client.SimpleUDPClient(ip, port)
    client.send_message(namespace, args)


for i in range(0, 1000):
    send("127.0.0.1", 1234, "/ping")
