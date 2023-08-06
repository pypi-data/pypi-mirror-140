import pyvisa as visa

class ThorlabsPM100A:
    def __init__(self):
        self.rm = visa.ResourceManager()
        self.connected = False
        self.device_identifiers = {'THORLABS','Thorlabs'} #A device will be considered a powermeter if its identity (i.e. the answer to '*IDN?') contains any of these words
        self.being_zeroed = 0 #This flag is set to 1 while the powermeter is being zeroed, in order to temporarly stop any power reading
        self._wavelength = None
        self._auto_power_range = None # boolean variable, True if the powermeter has the auto power range ON, False otherwise
        self._power_range = None
        self._power = None
        self._power_units = None
        self._min_power_range = None
        self._max_power_range = None

        #The properties min_wavelength and max_wavelength are defined as 'standard' variables and not
        # via the the @property, because they never change once we are connected to a given powermeter, 
        # so we can query the powermeter only once (at connection) and avoid additional queries later.
        self.min_wavelength = None 
        self.max_wavelength = None

    @property
    def power(self):
        if not(self.connected):
            self._power , self._power_units = None , ''
            raise RuntimeError("No powermeter is currently connected.")
        if(self.being_zeroed==0):
            Msg1 = self.instrument.query('measure:power?')
            Msg2 = self.instrument.query('power:dc:unit?')
            self._power = float(Msg1)
            self._power_units = str(Msg2).strip('\n') 
        else:
            self._power , self._power_units = None , ''
        return (self._power , self._power_units)

    @property
    def wavelength(self):
        if not(self.connected):
            self._wavelength = None
            raise RuntimeError("No powermeter is currently connected.")
        Msg = self.instrument.query('SENS:CORR:WAV?')
        self._wavelength = int(float(Msg))
        return self._wavelength

    @wavelength.setter
    def wavelength(self, wl):
        #Input variable wl can be either a string or a float or an int
        if not(self.connected):
            self._wavelength = None
            raise RuntimeError("No powermeter is currently connected.")
        try:
            wl = int(wl)
        except:
            raise TypeError("Wavelength value must be a valid integer number")
        if wl<0:
            raise ValueError("Wavelength must be a positive number.")
        if wl<self.min_wavelength or wl>self.max_wavelength:
            raise ValueError(f"Wavelength must between {self.min_wavelength} and {self.max_wavelength}.")
        self.instrument.write('SENS:CORR:WAV ' + str(wl))
        self._wavelength = wl
        return self._wavelength

    def read_min_max_wavelength(self):
        if not(self.connected):
            raise RuntimeError("No powermeter is currently connected.")
        Msg = self.instrument.query('SENS:CORR:WAV? MIN')
        self.min_wavelength = int(float(Msg))
        Msg = self.instrument.query('SENS:CORR:WAV? MAX')
        self.max_wavelength = int(float(Msg))
        return self.max_wavelength, self.min_wavelength

    @property
    def min_power_range(self):
        if not(self.connected):
            self._min_power_range = None
            raise RuntimeError("No powermeter is currently connected.")
        Msg = self.instrument.query('POW:DC:RANG? MIN')
        self._min_power_range = float(Msg)
        return self._min_power_range

    @property
    def max_power_range(self):
        if not(self.connected):
            self._max_power_range = None
            raise RuntimeError("No powermeter is currently connected.")
        Msg = self.instrument.query('POW:DC:RANG? MAX')
        self._max_power_range = float(Msg)
        return self._max_power_range

    @property
    def auto_power_range(self):
        if not(self.connected):
            self._auto_power_range = None
            raise RuntimeError("No powermeter is currently connected.")
        Msg = self.instrument.query('POW:DC:RANG:AUTO?')
        self._auto_power_range = bool(int(Msg))         
        return self._auto_power_range

    @auto_power_range.setter
    def auto_power_range(self, status):
        if not(self.connected):
            raise RuntimeError("No powermeter is currently connected.")
        if not(type(status)==bool):
            raise TypeError("Value of auto_power_range must be either True or False.")
        string = 'ON' if status else 'OFF'
        self.instrument.write('POW:DC:RANG:AUTO ' + string)
        self._auto_power_range = status
        return self._auto_power_range

    @property
    def power_range(self):
        ''' Returns the current power range, defined as the maximum power measureable in the current power range'''
        if not(self.connected):
            self._power_range = None
            raise RuntimeError("No powermeter is currently connected.")
        Msg = self.instrument.query('POW:DC:RANG?')
        self._power_range = float(Msg)
        return self._power_range

    @power_range.setter
    def power_range(self, power):
        if not(self.connected):
            raise RuntimeError("No powermeter is currently connected.")
        if not(type(power)==int or type(power)==float):
            raise TypeError("Value of power_range must be a number.")
        if power<0:
            raise ValueError("Power must be a positive number.")
        self.instrument.write('POW:DC:RANG ' + str(power))
        self._power_range = power
        return self._power_range

    def list_devices(self):
        self.list_all_devices = self.rm.list_resources()
        self.list_valid_devices = [] 
        self.list_IDN = []
        for addr in self.list_all_devices:
            if(not(addr.startswith('ASRL'))):
                try:
                    instrument = self.rm.open_resource(addr)
                    idn = instrument.query('*IDN?').strip()
                    if(any(word in idn for word  in self.device_identifiers)):
                        self.list_IDN.append(idn)   
                        self.list_valid_devices.append(addr)  
                        #self.rm.
                    instrument.before_close()
                    instrument.close()     
                except visa.VisaIOError:
                    pass
        return (self.list_valid_devices,self.list_IDN)
    
    def connect_device(self,device_name):
        self.list_devices()
        if (device_name in self.list_valid_devices):
            try:         
                self.instrument = self.rm.open_resource(device_name, timeout=1)
                Msg = self.instrument.query('*IDN?')
                ID = 1
            except visa.VisaIOError:
                Msg = "Error while connecting."
                ID = 0 
        else:
            Msg = "The specified name is not a valid device."
            ID = -1
        if(ID==1):
            self.connected = True
            self.read_parameters_upon_connection()
        return (Msg,ID)

    def read_parameters_upon_connection(self):
        self.wavelength
        self.read_min_max_wavelength()
        self.power
        self.min_power_range
        self.max_power_range
        self.auto_power_range
        self.power_range

    def disconnect_device(self):
        if(self.connected == True):
            try:   
                self.instrument.control_ren(False)  # Disable remote mode
                self.instrument.close()
                ID = 1
                Msg = 'Succesfully disconnected.'
            except Exception as e:
                ID = 0 
                Msg = e
            if(ID==1):
                self.connected = False
            return (Msg,ID)
        else:
            return ("Device is already disconnected.",-1)

    def set_zero(self):
        if(self.connected):
            try:
                self.BeingZeroed = 1
                ID = self.instrument.write('sense:correction:collect:zero')
                self.BeingZeroed = 0
                ID = 1
            except visa.VisaIOError:
                ID = 0
                pass
        return ('',ID)

    
    def move_to_next_power_range(self,direction,LastPowerRange = None):
        '''#Increase or decrease the power range, based on the value of the input variable direction
        Note: the VISA comnmands of the powermeter do not allow to simply "move" to the next power range, but only to specify the maximum power one would like to measure.
        The powermeter then sets the power range to the smallest available range which can still measure the desired power. This can be tricky to handle because, for example
        the bounds of each power range also depend on the wavelength. So, simply increasing the power by, e.g., a factor of 10, might sometimes fail, i.e. it might either not changethe power range,
        or it might skipp one of the ranges.
        To address this, I here use an adaptive alghoritm which progressively increases (or decreases) the power by a factor smaller than 10 and everytime it checks if the powermeter range has actually changed
        As soon as the powermeter range really changes, it stops.'''

        if not(direction==+1 or direction==-1):
            raise ValueError("The input variable 'direction' must be either +1 (to increase power range) or -1 (to decrease it).") 

        Factor = 10*0.9
        if not(LastPowerRange):
            LastPowerRange = self._power_range
        self.old_powerRange = self._power_range
        self.TargetPowerRange = (LastPowerRange * Factor) if (direction==+1) else (LastPowerRange / Factor)

        if self.TargetPowerRange*Factor < self._min_power_range:
            return
        if self.TargetPowerRange > self._max_power_range:
            return

        self.power_range = self.TargetPowerRange    #Try updating the power range to the new value. The value stored in self.power_range (when retrie it) will actually be one of the valid power ranges
                                                    #allowed by the specific powermeter.
        if self.power_range == self.old_powerRange: #if after setting the desired power, the power range of the powermeters is unchanged, we call again this function
            self.move_to_next_power_range(direction,self.TargetPowerRange)

        