import msgpack
import murata
from murata import socket_type

m = murata.murata('/dev/tty.usbserial-140')


#print("use external sim = ", m.set_sim_select())
#print("enable radio = ", m.enable_radio())
#print("enable cell = ", m.use_cellular())
#print(m.ping("8.8.8.8", 1, 100))

t = {
    "id" : 1,
    "name" : "nipun",
    "student" : True
}

raw = msgpack.packb(t)

print(m.socket_setup(socket_type.tcp, "0.tcp.us-cal-1.ngrok.io", 11835))
print(m.socket_send(raw))
print(m.socket_info())
print(m.socket_close())

m.close()