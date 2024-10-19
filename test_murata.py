import murata

m = murata.murata('/dev/tty.usbserial-130')


#print("use external sim = ", m.set_sim_select())
#print("enable radio = ", m.enable_radio())
#print("enable cell = ", m.use_cellular())
print(m.ping("8.8.8.8", 1, 100))

m.close()


None