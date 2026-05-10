import pyarrow.flight as flight
import os

socket_path = "/tmp/dummie_flight.sock"
location = f"grpc+unix://{socket_path}"

print(f"Connecting to {location}...")
try:
    client = flight.connect(location)
    ticket = flight.Ticket(b"RETURN 1")
    reader = client.do_get(ticket)
    print("SUCCESS: Connected and received response.")
except Exception as e:
    print(f"FAIL: {e}")
