import mido

# List all available MIDI input ports
print("Available MIDI input ports:")
input_ports = mido.get_input_names()
for i, port in enumerate(input_ports):
    print(f"{i}: {port}")

# Check if there are any available input ports
if not input_ports:
    print("No MIDI input ports found.")
    exit()

# Open the first available MIDI input port
input_port_name = input_ports[0]
with mido.open_input(input_port_name) as input_port:
    print(f"Listening on {input_port_name}...")

    # Continuously read and print MIDI messages
    isMicMuted = [
        True,
        True,
        True,
        True,
        True,
        True
    ]
    for message in input_port:
        print(message)
        if message.control == 27 and message.value == 1:
            print(f"You toggled mic number {message.channel + 1}")
            isMicMuted[message.channel] = not isMicMuted[message.channel]
            print(isMicMuted)
