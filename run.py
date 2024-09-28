#! venv/bin/python3.11

from podbean_client.podbean.podbean import PodbeanClient

if __name__ == '__main__':
    client = PodbeanClient()
    client.run()