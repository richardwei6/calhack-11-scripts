import murata

m = murata.murata('/dev/tty.usbserial-140')


#print("use external sim = ", m.set_sim_select())
#print("enable radio = ", m.enable_radio())
#print("enable cell = ", m.use_cellular())
#print(m.ping("8.8.8.8", 1, 100))

print(m.udp_socket_setup("34.192.142.126"))
print(m.udp_socket_send(b'foo'))
print(m.udp_socket_info())
print(m.udp_socket_close())

m.close()