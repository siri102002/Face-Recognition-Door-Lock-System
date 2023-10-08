import serial.tools.list_ports

# Get a list of available ports
ports = serial.tools.list_ports.comports()

# Print the list of available ports
for port in ports:
    print(port)