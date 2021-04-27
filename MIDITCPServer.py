import mido
from mido.sockets import PortServer, connect

with PortServer('localhost', 8080) as server:
    clients = []
    while True:
        # Handle connections.
        client = server.accept(block=False)
        if client:
            print('Connection from {}'.format(client.name))
            clients.append(client)

        for i, client in clients:
            if client.closed:
                print('{} disconnected'.format(client.name))
                del clients[i]

        # Receive messages.
        for client in clients:
            for message in client.iter_pending():
                print('Received {} from {}'.format(message, client))
