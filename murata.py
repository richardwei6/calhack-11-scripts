# python interface for the Murata ALT1250 module
# communicates over serial @ 115200 baud
# implements https://docs.monogoto.io/ntn-satellite-network/murata-alt1250-satellite-ntn-network
# Serial port on MACOS = /dev/tty.usbserial-130

import serial
import time
import murata_consts

class murata:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=2)

        # wait for dev to init
        print("device needs to init")
        r = ''
        while r != murata_consts.MURATA_BOOT:
            r = self._read(remove_echo=False)
            print("waiting for device to start = ", r)
            time.sleep(0.5)

        print("device successfully init")

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
            return True
        return False
    
    def set_sim_select(self):
        self._write('AT%SETCFG="SIM_INIT_SELECT_POLICY","0"') # set sim selection to 0 (external)
        if self._check_success():
            return self.reboot()
        return False
    
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
            if not self._check_success:
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
            if not self._check_success:
                return False

        if not self.reboot():
            return False

        # Network activation

        if not self.disable_radio():
            return False

        act_commands = ['AT%IGNSSEV="FIX",1',
                        'AT%NOTIFYEV="SIB31",1'
                        'AT+CEREG=2'
                        'AT%IGNSSACT=1'
                        'AT+CFUN=1']

        for c in act_commands:
            self._write(c)
            if not self._check_success:
                return False
            
        r = self.read(remove_echo=False)
        print("final read = " + r)
        return r != b''
        

        




    

    
    
