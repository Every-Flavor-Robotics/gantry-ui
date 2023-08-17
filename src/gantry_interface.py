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

    def _send_request(self, method, endpoint, data=None):
        headers = {"session_id": self.session_id}

        # Strip leading slash from endpoint
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        print(f"Sending {method} request to {endpoint} with data: {data}")

        url = f"{self.server_url}/{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)

            if response.status_code != 200:
                print(
                    f"Request to {endpoint} failed with status {response.status_code}: {response.text}"
                )
                return None

            # Check if JSON response
            if response.headers.get("content-type") == "application/json":
                return response.json()
            else:
                return response.text

        except requests.RequestException as e:
            print(f"Failed to send {method} request to {endpoint}. Error: {e}")
            return None

    def connect(self, ip: str, port: int = 8080) -> bool:
        """Connect to the ESP32 web server."""
        self.server_url = f"http://{ip}:{port}"
        self.session_id = str(uuid.uuid4())[:8]
        print(f"Session ID: {self.session_id}")

        response = self._send_request("POST", "/session", {"session_id": self.session_id})


        # Check for 200 response
        if response:
            self._listener_thread = Thread(target=self._heartbeat)
            self._listener_thread.start()
            self.connected = True

            return True
        else:
            print("Failed to connect to the server.")
            return False

    def disconnect(self) -> None:
        """Disconnect from the server and stop the listener thread."""
        self._stop_event.set()
        if self._listener_thread:
            self._listener_thread.join()
        self.connected = False
        print("Disconnected from gantry.")

    def _heartbeat(self) -> None:
        """Private method to continuously poll the server for heartbeats."""
        self._stop_event.clear()

        while not self._stop_event.is_set():
            response = self._send_request("GET", "/session")

            if not response or response.get("status") != "success":
                print("Heartbeat check failed.")
                self.heartbeat_failure_count += 1
            else:
                self.heartbeat_failure_count = 0

            if self.heartbeat_failure_count >= self.MAX_HEARTBEAT_FAILURES:
                print("Disconnected from gantry due to too many heartbeat failures.")
                self.connected = False
                self._stop_event.set()

            # Wait for a few seconds before polling again
            self._stop_event.wait(2)


    def set_pid_position_p_channel_0(self, value: float) -> None:
        """Set the position/p PID value on the ESP32 web server for channel 0."""
        self._send_request("POST", "/pid/ch0/position/p", {"value": value})

    def set_pid_position_p_channel_1(self, value: float) -> None:
        """Set the position/p PID value on the ESP32 web server for channel 1."""
        self._send_request("POST", "/pid/ch1/position/p", {"value": value})

    # Adding methods for all other endpoints
    # ... for channel 0
    def set_pid_position_i_channel_0(self, value: float) -> None:
        self._send_request("POST", "/pid/ch0/position/i", {"value": value})

    def set_pid_position_d_channel_0(self, value: float) -> None:
        self._send_request("POST", "/pid/ch0/position/d", {"value": value})

    def set_pid_velocity_p_channel_0(self, value: float) -> None:
        self._send_request("POST", "/pid/ch0/velocity/p", {"value": value})

    def set_pid_velocity_i_channel_0(self, value: float) -> None:
        self._send_request("POST", "/pid/ch0/velocity/i", {"value": value})

    def set_pid_velocity_d_channel_0(self, value: float) -> None:
        self._send_request("POST", "/pid/ch0/velocity/d", {"value": value})

    # ... for channel 1
    def set_pid_position_i_channel_1(self, value: float) -> None:
        self._send_request("POST", "/pid/ch1/position/i", {"value": value})

    def set_pid_position_d_channel_1(self, value: float) -> None:
        self._send_request("POST", "/pid/ch1/position/d", {"value": value})

    def set_pid_velocity_p_channel_1(self, value: float) -> None:
        self._send_request("POST", "/pid/ch1/velocity/p", {"value": value})

    def set_pid_velocity_i_channel_1(self, value: float) -> None:
        self._send_request("POST", "/pid/ch1/velocity/i", {"value": value})

    def set_pid_velocity_d_channel_1(self, value: float) -> None:
        self._send_request("POST", "/pid/ch1/velocity/d", {"value": value})

    def set_target_waypoint(self, value: int) -> None:
        self._send_request("POST", "/target_waypoint", {"value": value})
