from gantry_interface import GantryInterface
from gantry_listener import GantryListener
from zeroconf import ServiceBrowser, Zeroconf
import time
import sys
import tty
import termios

cur_waypoint = 0


def getch():
    """
    Gets a single character from STDIN without requiring enter.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch


def record_trajectory(gantry_data: dict):
    # Print in green, entering record mode
    print("\033[92mEntering record mode\033[0m")
    print("Press space to record waypoint")
    print("Press enter to save trajectory")
    print("Press q to exit")

    # Set mode for all gantries to 1
    for _, gantry in gantry_data.items():
        gantry["interface"].set_mode(1)

    while True:
        # Wait for user to press enter
        button = getch()
        # Check if user pressed enter
        if button == "\r":
            # If user pressed enter, break out of loop
            break
        # Check if user pressed q
        if button == "q":
            # If user pressed q, exit
            # Switch to mode 0
            for _, gantry in gantry_data.items():
                gantry["interface"].set_mode(0)
            return

        if button == " ":
            # If user pressed space, record waypoint
            for _, gantry in gantry_data.items():
                import ipdb

                gantry["interface"].add_waypoint()
            print("Waypoint recorded")

    # Print in green, saving trajectory
    print("\033[92mSaving trajectory\033[0m")
    for _, gantry in gantry_data.items():
        gantry["interface"].save_trajectory()


def set_speed(gantry_data: dict):
    # Print in green, enter target speed
    print("\033[92mEnter target speed\033[0m")
    # Get target speed from user
    target_speed = input()
    # convert target speed to float
    target_speed = float(target_speed)

    # Set target speed for all gantries
    for _, gantry in gantry_data.items():
        gantry["interface"].set_target_speed(target_speed)


def go_to_next(gantry_data: dict):
    global cur_waypoint
    # Print in green, setting waypoint
    print(f"\033[92mGoing to next waypoint\033[0m")

    print(f"cur_waypoint: {cur_waypoint}")
    # Set speed multipliers for all gantries
    for _, gantry in gantry_data.items():
        # Get current position
        q0_pos, q1_pos = gantry["interface"].get_position()
        # Get next waypoint
        q0_wp, q1_wp = gantry["interface"].get_next_waypoint()

        # Calculate the distance between the current position and the next waypoint
        q0_dist = q0_wp - q0_pos
        q1_dist = q1_wp - q1_pos

        # Adjust multipliers to get both axes to reach the waypoint at the same time
        # Fastest axis will have a multiplier of 1
        # Slowest axis will have a multiplier of (slowest_speed / fastest_speed)
        # Calculate the speed multiplier for each axis

        q0_multiplier = abs(q0_dist) / max(abs(q0_dist), abs(q1_dist))
        q1_multiplier = abs(q1_dist) / max(abs(q0_dist), abs(q1_dist))

        # Print multipliers, waypoints, distances
        print(f"q0_multiplier: {q0_multiplier}")
        print(f"q1_multiplier: {q1_multiplier}")
        print(f"q0_wp: {q0_wp}")
        print(f"q1_wp: {q1_wp}")
        print(f"q0_dist: {q0_dist}")
        print(f"q1_dist: {q1_dist}")

        # Set the target speed
        gantry["interface"].set_speed_multipler(q0_multiplier, q1_multiplier)

    cur_waypoint += 1
    # Set waypoint for all gantries
    for _, gantry in gantry_data.items():

        gantry["interface"].set_target_waypoint(cur_waypoint)

def go_to_previous(gantry_data: dict, waypoint_index: int):
    global cur_waypoint
    # Print in green, setting waypoint
    print(f"\033[92mGoing to previous waypoint\033[0m")

    # Print cur waypoint
    print(f"cur_waypoint: {cur_waypoint}")
    # Set speed multipliers for all gantries
    for _, gantry in gantry_data.items():
        # Get current position
        q0_pos, q1_pos = gantry["interface"].get_position()
        # Get next waypoint
        q0_wp, q1_wp = gantry["interface"].get_previous_waypoint()

        # Calculate the distance between the current position and the next waypoint
        q0_dist = q0_wp - q0_pos
        q1_dist = q1_wp - q1_pos

        # Adjust multipliers to get both axes to reach the waypoint at the same time
        # Fastest axis will have a multiplier of 1
        # Slowest axis will have a multiplier of (slowest_speed / fastest_speed)
        # Calculate the speed multiplier for each axis

        # print(f"q0_dist: {q0_dist}")
        # print(f"q1_dist: {q1_dist}")

        q0_multiplier = abs(q0_dist) / max(abs(q0_dist), abs(q1_dist))
        q1_multiplier = abs(q1_dist) / max(abs(q0_dist), abs(q1_dist))
        # print(f"q0_multiplier: {q0_multiplier}")
        # print(f"q1_multiplier: {q1_multiplier}")
        # print(f"q0_wp: {q0_wp}")
        # print(f"q1_wp: {q1_wp}")
        # print(f"q0_dist: {q0_dist}")
        # print(f"q1_dist: {q1_dist}")

        # Set the target speed
        gantry["interface"].set_speed_multipler(q0_multiplier, q1_multiplier)
    cur_waypoint -= 1

    # Set waypoint for all gantries
    for _, gantry_data in gantry_data.items():
        gantry["interface"].set_target_waypoint(cur_waypoint)


def trajectory_playback(gantry_data: dict):
    global cur_waypoint

    # Print in green, entering playback mode
    print("\033[92mEntering playback mode\033[0m")
    print("Press d to move to next waypoint")
    print("Press a to move to previous waypoint")
    print("Press q to exit")


    cur_waypoint = 0

    # Set mode for all gantries to 2
    for _, gantry in gantry_data.items():
        gantry["interface"].set_mode(2)
        gantry["interface"].set_target_waypoint(0)


    # Get trajectory length for all gantries, confirm they are the same and save
    # trajectory length
    trajectory_length = None
    for _, gantry in gantry_data.items():
        if trajectory_length is None:
            trajectory_length = gantry["interface"].get_trajectory_length()
        else:
            assert (
                trajectory_length == gantry["interface"].get_trajectory_length()
            ), "Trajectory lengths do not match"

    print("Found trajectory of length ", trajectory_length)
    while True:
        print("cur_waypoint: ", cur_waypoint)
        print("trajectory_length: ", trajectory_length)
        button = getch()

        # Check if user pressed q
        if button == "q":
            # If user pressed q, exit
            # Switch to mode 0
            for _, gantry in gantry_data.items():
                gantry["interface"].set_mode(0)
            return

        # Check if user pressed d
        if button == "d":
            if cur_waypoint == trajectory_length - 1:
                print("Reached end of trajectory")
                continue
            # If user pressed d, move to next waypoint
            go_to_next(gantry_data)
        elif button == "a":
            if cur_waypoint == 0:
                print("Reached beginning of trajectory")
                continue
            # If user pressed a, move to previous waypoint
            go_to_previous(gantry_data, cur_waypoint)


def main():
    # Set up listener
    zeroconf = Zeroconf()
    listener = GantryListener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

    # Print in green text hello
    print(
        "\033[92mSearching for available gantries, press enter once all gantries discovered\033[0m"
    )

    # Wait for user to press enter
    input()
    # Stop searching for gantries
    zeroconf.close()

    # Print in green, connecting to N gantries
    print(
        f"\033[92mConnecting to {len(listener.gantry_data)} gantries, press enter once all gantries connected\033[0m"
    )

    gantries = listener.gantry_data
    for gantry_name, gantry_data in gantries.items():
        # Create a gantry interface for each gantry
        gantry_data["interface"] = GantryInterface()
        # Connect to the gantry
        gantry_data["interface"].connect(gantry_data["addresses"], gantry_data["port"])
        gantry_data["interface"].set_mode(0)

    # Enter trajectory recording mode
    record_trajectory(gantries)

    while True:



        # Enter target speed mode
        set_speed(gantries)

        # Enter trajectory playback mode
        trajectory_playback(gantries)


        for gantry_name, gantry_data in gantries.items():
            gantry_data["interface"].set_mode(0)


        print("Idle mode")
        print("Press enter to resume")
        input()

    # # gantry = GantryInterface()

    # # Connect
    # # gantry.connect("192.168.0.102", 8080)

    # # gantry.set_mode(0)

    # time.sleep(1)

    # gantry.set_mode(1)

    # time.sleep(1)

    # print(gantry.get_position())

    # print(gantry.add_waypoint())
    # print("Move to waypoint, then press enter")
    # input()

    # print(gantry.add_waypoint())

    # time.sleep(1)
    # print("Saving trajectory")
    # print(gantry.save_trajectory())

    # # Switch to playback mode
    # gantry.set_mode(2)

    # # Target speed
    # target_speed = 4
    # gantry.set_target_speed(target_speed)

    # # Wait until settlted
    # print("Press enter when ready")
    # input()

    # while True:
    #     # Get current position
    #     q0_pos, q1_pos = gantry.get_position()
    #     # Get next waypoint
    #     q0_wp, q1_wp = gantry.get_next_waypoint()

    #     # Calculate the distance between the current position and the next waypoint
    #     q0_dist = q0_wp - q0_pos
    #     q1_dist = q1_wp - q1_pos

    #     # Adjust multipliers to get both axes to reach the waypoint at the same time
    #     # Fastest axis will have a multiplier of 1
    #     # Slowest axis will have a multiplier of (slowest_speed / fastest_speed)
    #     # Calculate the speed multiplier for each axis

    #     print(f"q0_dist: {q0_dist}")
    #     print(f"q1_dist: {q1_dist}")
    #     q0_multiplier = abs(q0_dist) / max(abs(q0_dist), abs(q1_dist))
    #     q1_multiplier = abs(q1_dist) / max(abs(q0_dist), abs(q1_dist))

    #     print(f"q0_multiplier: {q0_multiplier}")
    #     print(f"q1_multiplier: {q1_multiplier}")

    #     # Set the target speed
    #     gantry.set_target_speed(2)
    #     gantry.set_speed_multipler(q0_multiplier, q1_multiplier)

    #     # Set the target waypoint
    #     gantry.set_target_waypoint(1)

    #     # Wait until the waypoint is reached
    #     input()

    #     # Get current position
    #     q0_pos, q1_pos = gantry.get_position()
    #     # Get next waypoint
    #     q0_wp, q1_wp = gantry.get_previous_waypoint()

    #     # Calculate the distance between the current position and the next waypoint
    #     q0_dist = q0_wp - q0_pos
    #     q1_dist = q1_wp - q1_pos

    #     # Adjust multipliers to get both axes to reach the waypoint at the same time
    #     # Fastest axis will have a multiplier of 1
    #     # Slowest axis will have a multiplier of (slowest_speed / fastest_speed)
    #     # Calculate the speed multiplier for each axis
    #     print(f"q0_dist: {q0_dist}")
    #     print(f"q1_dist: {q1_dist}")
    #     q0_multiplier = abs(q0_dist) / max(abs(q0_dist), abs(q1_dist))
    #     q1_multiplier = abs(q1_dist) / max(abs(q0_dist), abs(q1_dist))

    #     print(f"q0_multiplier: {q0_multiplier}")
    #     print(f"q1_multiplier: {q1_multiplier}")

    #     # Set the target speed
    #     gantry.set_target_speed(2)
    #     gantry.set_speed_multipler(q0_multiplier, q1_multiplier)

    #     # Set the target waypoint
    #     gantry.set_target_waypoint(0)

    #     # Wait until the waypoint is reached
    #     input()


if __name__ == "__main__":
    main()
