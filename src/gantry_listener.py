import time
from zeroconf import ServiceBrowser, Zeroconf


class GantryListener:
    def __init__(self):
        self.gantry_data = {}

    def remove_service(self, zeroconf, type, name):
        pass  # We don't need to handle this event

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            # Check if the hostname matches our criteria
            if "gantry" in name.lower():
                # print(f"Found service {name} at {info.server}")
                print(f"Found service")

                # Get txt stored at key "gantry"
                gantry_name = info.properties.get(b"gantry").decode("utf-8")
                addresses = [".".join(map(str, bytes(addr))) for addr in info.addresses]

                if gantry_name not in self.gantry_data:
                    self.gantry_data[gantry_name] = {
                        "addresses": addresses[0],
                        "port": info.port,
                    }

                print(f"Gantry name: {gantry_name}")
                print(f"Info: {self.gantry_data[gantry_name]}")

    # def __len__(self):
    #     return len(self.gantry_data)


# zeroconf = Zeroconf()
# listener = GantryListener()
# browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

# try:
#     while True:
#         time.sleep(0.1)
# except KeyboardInterrupt:
#     pass
