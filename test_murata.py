import murata

m = murata.murata('/dev/tty.usbserial-140')


#print("use external sim = ", m.set_sim_select())
#print("enable radio = ", m.enable_radio())
#print("enable cell = ", m.use_cellular())
#print(m.ping("8.8.8.8", 1, 100))

print(m.udp_socket_setup("0.tcp.us-cal-1.ngrok.io", 11835))
print(m.udp_socket_send(b'Hello1'))
print(m.udp_socket_send(b'fuck u nipun'))
print(m.udp_socket_info())
print(m.udp_socket_close())

m.close()