# python interface for the Murata ALT1250 module
# communicates over serial @ 115200 baud
# implements https://docs.monogoto.io/ntn-satellite-network/murata-alt1250-satellite-ntn-network
# Serial port on MACOS = /dev/tty.usbserial-130

import serial
import time
import murata_consts

class murata:
    def __init__(self, port, baudrate=115200):
        while 1:
            try:
                self.ser = serial.Serial(port, baudrate, timeout=None)
            except serial.serialutil.SerialException as e:
                print("device not connected")
                time.sleep(0.3)
                continue
            break

        # wait for dev to init
        print("device needs to init")
        r = ''
        while r != murata_consts.MURATA_BOOT:
            r = self._read(remove_echo=False)
            print("waiting for device to start = ", r)
            time.sleep(0.5)

        print("device successfully init")
        time.sleep(murata_consts.MURATA_BOOT_WAIT) # https://stackoverflow.com/a/35885723/

    def close(self):
        self.ser.close()

    ### --- Read/Write Helper Functions

    # remove echo is only necessary if you write before you read
    def _read(self, remove_echo=True):
        if remove_echo:
            _ = self.ser.readline()
        r = self.ser.readline()
        print("READ: ", r)
        return r

    def _check_success(self):
        return self._read() == murata_consts.MURATA_OK
    
    def _write(self, command):
        self.ser.write(str.encode(command+'\r'))
        time.sleep(0.25) # let command propogate

    def _write_raw(self, raw_command):
        self.ser.write(raw_command)
        time.sleep(0.25) # let command propogate

    ### --- Interaction Functions

    def ping(self):
        self._write('AT')
        return self._check_success()
    
    def reboot(self):
        self._write('ATZ')
        
        if self._check_success():
            while self._read() != murata_consts.MURATA_BOOT:
                print("waiting for correct response for reboot")
                time.sleep(0.5)
            print("reboot successful")
            time.sleep(murata_consts.MURATA_BOOT_WAIT)
            return True
        return False
    
    def set_sim_select(self):
        self._write('AT%SETCFG="SIM_INIT_SELECT_POLICY","0"') # set sim selection to 0 (external)
        if self._check_success():
            return self.reboot()
        return False
    
    def see_sim_select(self):
        self._write('AT%GETCFG="SIM_INIT_SELECT_POLICY"')
        return self._read()
    
    def disable_radio(self):
        self._write('AT+CFUN=0')
        return self._check_success()
    
    def enable_radio(self):
        self._write('AT+CFUN=1')
        return self._check_success()

    def conf_satellite(self):
        # set the NTN parameter
        ntn_commands = ['AT%SETACFG="radiom.config.multi_rat_enable","true"',
                        'AT%SETACFG="radiom.config.preferred_rat_list","none"', 
                        'AT%SETACFG="radiom.config.auto_preference_mode","none"',
                        'AT%SETACFG="locsrv.operation.locsrv_enable","true"',
                        'AT%SETACFG="locsrv.internal_gnss.auto_restart","enable"',
                        'AT%SETACFG="modem_apps.Mode.AutoConnectMode","true"']
        
        for c in ntn_commands:
            self._write(c)
            if not self._check_success():
                return False

        if not self.reboot():
            return False
        
        self._write('AT%RATACT="NBNTN","1"')
        if not self._check_success():
            return False
        
        if not self.disable_radio():
            return False
        
        ntn_commands_2 = ['AT%PDNSET=1,"DATA.MONO","IP"',
                          'AT%SETSYSCFG=SW_CFG.nb_band_table.band#1,ENABLE;23',
                          'AT%NTNCFG="POS","IGNSS","0"']
        
        for c in ntn_commands_2:
            self._write(c)
            if not self._check_success():
                return False

        if not self.reboot():
            return False

        # Network activation

        if not self.disable_radio():
            return False

        act_commands = ['AT%IGNSSEV="FIX",1',
                        'AT%NOTIFYEV="SIB31",1'
                        'AT+CEREG=2'
                        'AT%IGNSSACT=1']

        for c in act_commands:
            self._write(c)
            if not self._check_success():
                return False
            
        # ADD DELAY HERE
        print("AWAIT Satellite connection")
        time.sleep(10)

        if not self.enable_radio():
            return False
        
        r = self._read(remove_echo=False)
        while r != b'':
            print("SATELLITE: ", r)
            r = self._read(remove_echo=False)

        return True
    
    def use_cellular(self):
        self._write('AT%RATACT="CATM","1"')
        return self._check_success()
    
    def use_satellite(self):
        self._write('AT%RATACT="NBNTN","1"')
        return self._check_success()
    
    def check_sim(self):
        self._write('AT+CPIN?')
        while 1:
            print("sim = ", self.ser.read_all())
            time.sleep(1)
        return True

    ## --- Sending messages/pinging

    def _validIP(self, addr):
        parts = addr.split(".")
        if len(parts) != 4:
            return False
        for item in parts:
            if not 0 <= int(item) <= 255:
                return False
        return True

    # addr is str
    # count, packet_size, timeout is int
    # return type is three vars: [is_valid, x, y]
    def ping(self, addr, count, packet_size, timeout=10):
        if not self._validIP(addr):
            print("INVALID IP")
            return False

        command = 'AT%PINGCMD=0,'
        command += '"' + addr + '",'
        command += str(count) + ','
        command += str(packet_size) + ','
        command += str(timeout)

        self._write(command)

        r = self._read(False) # first message is echo
        print("First = ", r)
        r = self._read(False) # second message is either OK or ping response 
        print("Second = ", r)
        if r == murata_consts.MURATA_OK: # no response was recieved
            return False, -1, -1



        return True, -1, -1
        



        

        




    

    
    
