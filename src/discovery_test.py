import time
from zeroconf import ServiceBrowser, Zeroconf


class GantryListener:
    def remove_service(self, zeroconf, type, name):
        pass  # We don't need to handle this event

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            # Check if the hostname matches our criteria
            if "gantry" in name.lower():
                print(f"Found service {name} at {info.server}")

                # Print the service TXT records
                for key, value in info.properties.items():
                    print(f"{key.decode('utf-8')}: {value.decode('utf-8')}")

                # Print the address and port number
                addresses = [".".join(map(str, bytes(addr))) for addr in info.addresses]
                print(f"Addresses: {addresses}")
                print(f"Port: {info.port}")
                print("-------------")


zeroconf = Zeroconf()
listener = GantryListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    zeroconf.close()
