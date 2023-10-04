import matplotlib.pyplot as plt
import math

def get_user_input(prompt, conversion_type=float):
    """Collect user input and convert to the given type."""
    return conversion_type(input(prompt))

def initialize_parameters():
    """
    Initialize the required parameters for the simulation.
    Returns:
        - total_data: The length of the file in kbyte
        - mss: Maximum Segment Size
        - rtt: Round Trip Time in seconds
        - total_packets: Total number of packets calculated using total_data and mss
        - ssthresh: Slow start threshold values for simulation steps
        - rcwnd: Receiver window sizes for simulation steps
    """
    total_data = get_user_input("Enter file length (kbyte): ", int)
    mss = get_user_input("Enter MSS: ", int)
    total_packets = total_data / mss
    print(f"Total packets: {total_packets}")
    rtt = get_user_input("Enter RTT (seconds) e.g. 0.500: ")
    ssthresh_val = get_user_input("Enter SSHTRESH at T=0 (kbyte): ", int)

    ssthresh = [ssthresh_val / mss] * 65
    rcwnd = [1] * 65

    return total_data, mss, rtt, total_packets, ssthresh, rcwnd

def update_rcwnd(rcwnd, rtt, mss):
    """
    Update rcwnd based on user inputs.
    Args:
        - rcwnd: Receiver window sizes for simulation steps
        - rtt: Round Trip Time in seconds
        - mss: Maximum Segment Size
    Returns:
        - Updated rcwnd values
    """
    while True:
        update_time = get_user_input("Enter time t for new RCWND or 100 to exit: ") / rtt
        if update_time > 65:
            break
        new_val = get_user_input("Enter new value: ", int) / mss
        for idx in range(int(update_time), 65):
            rcwnd[idx] = new_val
    return rcwnd

def get_working_binary(rtt):
    """
    Generate error markers based on user input.
    Args:
        - rtt: Round Trip Time in seconds
    Returns:
        - List of error markers
    """
    working_binary = [0] * 65
    while True:
        start_error = get_user_input("Enter error start time or 100 to end: ") / rtt
        if start_error > 100:
            break
        end_error = get_user_input("Enter error end time: ") / rtt
        for idx in range(int(start_error), int(end_error)):
            working_binary[idx] = -1
    return working_binary

def update_cwnd(cwnd, t, sndwnd, ssthresh, rcwnd):
    """
    Update the congestion window based on current values.
    Args:
        - cwnd: Current congestion window sizes for simulation steps
        - t: Current time step
        - sndwnd: Current send window sizes for simulation steps
        - ssthresh: Slow start threshold values for simulation steps
        - rcwnd: Receiver window sizes for simulation steps
    Returns:
        - Updated cwnd value for the given time step t
    """
    cwnd[t] = cwnd[t-1]
    for _ in range(int(sndwnd[t-1])):
        if cwnd[t] < ssthresh[t]:
            cwnd[t] += 1
        else:
            cwnd[t] += 1 / cwnd[t]

    sndwnd[t] = min(int(rcwnd[t]), int(cwnd[t]))

    if sndwnd[t] == int(cwnd[t]) and cwnd[t] - int(cwnd[t]) > 0.55:
        cwnd[t] = math.ceil(cwnd[t])

    cwnd[t] = round(cwnd[t], 2)
    return cwnd[t]

def simulate_tcp_behavior(total_data, mss, rtt, total_packets, ssthresh, rcwnd):
    """
    Simulate TCP congestion control behavior and plot the results.
    Args:
        - total_data: The length of the file in kbyte
        - mss: Maximum Segment Size
        - rtt: Round Trip Time in seconds
        - total_packets: Total number of packets calculated using total_data and mss
        - ssthresh: Slow start threshold values for simulation steps
        - rcwnd: Receiver window sizes for simulation steps
    """
    working_binary = get_working_binary(rtt)

    cwnd = [1] * 65
    sndwnd = [1] * 65
    back_off = 2
    total_sent = 0
    t = 0

    while total_sent < total_packets and t < 65:
        sndwnd[t] = min(int(rcwnd[t]), int(cwnd[t]))
        flight_size = min(int(sndwnd[t]), int(total_packets - total_sent))

        # Visualization logic
        if flight_size != sndwnd[t]:
            plt.scatter(t, sndwnd[t], c='green')
            plt.text(t+1, sndwnd[t], f"({flight_size})")

        if working_binary[t] == 0:
            back_off = 2
            plt.scatter(t, sndwnd[t], c='black')
            plt.text(t, sndwnd[t], str(sndwnd[t]))
            if sndwnd[t] != int(cwnd[t]):
                plt.scatter(t, cwnd[t], c='grey')
                plt.text(t, cwnd[t], str(cwnd[t]))

            total_sent += flight_size

            if total_sent == total_packets:
                plt.vlines(t+1, 0, 40)
                plt.text(t, 30, "end")
                break

            t += 1
            cwnd[t] = update_cwnd(cwnd, t, sndwnd, ssthresh, rcwnd)

        elif working_binary[t] == -1:
            plt.scatter(t, sndwnd[t], c='red')
            plt.text(t+2, sndwnd[t], " ERROR")
            t += back_off
            back_off *= 2
            cwnd[t] = 1

            for x in range(t, 65):
                ssthresh[x] = max(2, flight_size / 2)

            flight_size = min(int(sndwnd[t]), int(total_data - total_sent))

    while t < 65:
        sndwnd[t] = -1
        t += 1

    for x in range(65):
        if working_binary[x] == -1:
            sndwnd[x] = -1

    # Plotting
    plt.plot(ssthresh, c='blue', linestyle='dotted')
    plt.plot(rcwnd, linestyle='solid', c='black')
    plt.axis([-1, 65, -1, 40])

    x_ticks = list(range(65))
    y_ticks = list(range(45))
    plt.xticks(x_ticks)
    plt.yticks(y_ticks)
    plt.grid(axis='both')

    plt.show()

def main():
    """Main entry point for the program."""
    total_data, mss, rtt, total_packets, ssthresh, rcwnd = initialize_parameters()
    rcwnd = update_rcwnd(rcwnd, rtt, mss)  # Fixed the mss issue
    working_binary = get_working_binary(rtt)
    simulate_tcp_behavior(total_data, mss, rtt, total_packets, ssthresh, rcwnd)

if __name__ == "__main__":
    main()

