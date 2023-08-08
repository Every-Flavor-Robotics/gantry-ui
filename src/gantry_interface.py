import requests
from threading import Thread, Event
import uuid
import time

class GantryInterface:
    def __init__(self):
        self.server_url = None
        self._stop_event = Event()
        self._listener_thread = None
        self.connected = False

        self.heartbeat_failure_count = 0
        self.MAX_HEARTBEAT_FAILURES = 5

    def connect(self, ip: str, port: int = 80) -> bool:
        """Connect to the ESP32 web server."""
        self.server_url = f"http://{ip}:{port}"

        # Generate a short session ID
        self.session_id = str(uuid.uuid4())[:8]
        print(f"Session ID: {self.session_id}")

        # Send the session ID to the ESP32
        try:
            response = requests.post(f"{self.server_url}/", json={"session_id": self.session_id}, )
            if response.status_code == 200:
                # Start the heartbeat listener thread
                self._listener_thread = Thread(target=self._heartbeat)
                self._listener_thread.start()
                self.connected = True
                return True
            else:
                print("Failed to connect to the server.")
                print(f"Server responded with status code: {response.status_code}")
        except requests.RequestException:
            print("Failed to connect to the server.")

        return False

    def disconnect(self) -> None:
        """Disconnect from the server and stop the listener thread."""
        # Log that the gantry is disconnected

        self._stop_event.set()
        if self._listener_thread:
            self._listener_thread.join()

        self.connected = False
        print("Disconnected from gantry.")

    def send_data(self, endpoint: str, data: dict) -> None:
        """Send data to the ESP32 web server."""
        try:
            response = requests.post(f"{self.server_url}/{endpoint}", json=data)
            # Handle response if necessary
        except requests.RequestException as e:
            print(f"Failed to send data. Error: {e}")

    def _heartbeat(self) -> None:
        """Private method to continuously poll the server for heartbeats."""

        self._stop_event.clear()
        headers = {"session_id": self.session_id}
        while not self._stop_event.is_set():
            try:
                # Reset heartbeat counter
                self.heartbeat_failure_count = 0

                response = requests.get(f"{self.server_url}/", headers=headers)
                if response.status_code != 200:
                    print("Heartbeat check failed. Disconnected from gantry.")
                    self.connected = False
                    # Stop thread
                    self._stop_event.set()

            except requests.RequestException:
                print("Failed to poll heartbeat.")

                #  Increase the failure count
                self.heartbeat_failure_count += 1

            if(self.heartbeat_failure_count >= self.MAX_HEARTBEAT_FAILURES):
                print("Heartbeat check failed. Disconnected from gantry.")
                self.connected = False

            # Wait for a few seconds before polling again
            self._stop_event.wait(2)
