import murata
import time

m = murata.murata('/dev/tty.usbserial-130')

print(m.conf_satellite())

m.close()


