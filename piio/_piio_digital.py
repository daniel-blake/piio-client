import gobject
import dbus
import dbus.service
import dbus.mainloop.glib



from _event import Event
from _dbus_smartobject import DBusSmartObject,NoConnectionError
from _piio import PiIo, PiIoGroup, PiIoDict

class PiIoGroupDigital (PiIoGroup):
    '''
    Access piio Digital IO Groups
    
    Attributes:
        ButtonPress:     Event(handle) - an event triggers when a button is pressed
        ButtonHold:      Event(handle) - an event triggers when a button is held
        InputChanged:    Event(handle, value) - an event triggers when an input's value changed
        OutputChanged:   Event(handle, value) - an event triggers when an output's value changed
        MbInputChanged:  Event(handle, value) - an event triggers when a multibit input's value changed
        MbOutputChanged: Event(handle, value) - an event triggers when a multibit output's value changed
        PwmValueChanged: Event(handle, value) - an event triggers when a pwm value changed

    Note that the handle provided on these events is the short handle relative to this IO Group.
        
    '''
    def __init__(self,path):
        '''
        Initialize the object for a Digital IO Group connection
        '''
        
        self._dbus_itf_iogroup_digital='nl.miqra.PiIo.IoGroup.Digital'

        # declare events
        self.ButtonPress     = Event() # arguments: handle
        self.ButtonHold      = Event() # arguments: handle
        self.InputChanged    = Event() # arguments: handle, value
        self.OutputChanged   = Event() # arguments: handle, value
        self.MbInputChanged  = Event() # arguments: handle, value
        self.MbOutputChanged = Event() # arguments: handle, value
        self.PwmValueChanged = Event() # arguments: handle, value

        self.buttons = PiIoDict()
        self.inputs = PiIoDict()
        self.outputs = PiIoDict()
        self.mbinputs = PiIoDict()
        self.mboutputs = PiIoDict()
        self.pwms = PiIoDict()


        PiIoGroup.__init__(self,path)

    def _init_busobject(self,busobject):
        PiIoGroup._init_busobject(self,busobject)
        
        # connect_to_signal registers our callback function.
        busobject.connect_to_signal('ButtonPress', self._buttonPress)
        busobject.connect_to_signal('ButtonHold', self._buttonHold)
        busobject.connect_to_signal('InputChanged', self._inputChanged)
        busobject.connect_to_signal('OutputChanged', self._outputChanged)
        busobject.connect_to_signal('MbInputChanged', self._mbInputChanged)
        busobject.connect_to_signal('MbOutputChanged', self._mbOutputChanged)
        busobject.connect_to_signal('PwmValueChanged', self._pwmValueChanged)

        # register buttons 
        # catch an exception that occurs if we're not connected
        try:
            # add buttons if they were not already registered (in case of reconnect
            for handle in self._buttonHandles():
                handle = str(handle)
                if not self.buttons.has_key(handle):
                    o = DigitalButton(self, handle)
                    self.buttons[handle] = o
            
            # add buttons if they were not already registered (in case of reconnect
            for handle in self._inputHandles():
                handle = str(handle)
                if not self.inputs.has_key(handle):
                    o = DigitalInput(self, handle)
                    self.inputs[handle] = o
                
            # add buttons if they were not already registered (in case of reconnect
            for handle in self._ouputHandles():
                handle = str(handle)
                if not self.outputs.has_key(handle):
                    o = DigitalOutput(self, handle)
                    self.outputs[handle] = o

            # add buttons if they were not already registered (in case of reconnect
            for handle in self._mbInputHandles():
                handle = str(handle)
                if not self.mbinputs.has_key(handle):
                    o = DigitalMbInput(self, handle)
                    self.mbinputs[handle] = o

            # add buttons if they were not already registered (in case of reconnect
            for handle in self._mbOuputHandles():
                handle = str(handle)
                if not self.mboutputs.has_key(handle):
                    o = DigitalMbOutput(self, handle)
                    self.mboutputs[handle] = o

            # add buttons if they were not already registered (in case of reconnect
            for handle in self._pwmHandles():
                handle = str(handle)
                if not self.pwms.has_key(handle):
                    o = DigitalPwm(self, handle)
                    self.pwms[handle] = o

        except NoConnectionError as x:
            print "Error: Lost connection to piio-server during initialization"
            
    def _buttonPress(self,handle):
        """ gets called when a button is pressed
        """
        self.buttons[handle]._trigger("ButtonPress");
        self.ButtonPress(handle)

    def _buttonHold(self,handle):
        """ gets called when a button is held
        """
        self.buttons[handle]._trigger("ButtonHold");
        self.ButtonHold(handle)

    def _inputChanged(self,handle, value):
        """ gets called when a single input pin changes value
        """
        self.inputs[handle]._trigger("InputChanged");
        self.InputChanged(handle, value)

    def _outputChanged(self,handle, value):
        """ gets called when a single bit output has it's value changed
        """
        self.outputs[handle]._trigger("OutputChanged");
        self.OutputChanged(handle, value)

    def _mbInputChanged(self,handle, value):
        """ gets called when a multibit input changes value
        """
        self.mbinputs[handle]._trigger("MbInputChanged");
        self.MbInputChanged(handle, value)

    def _mbOutputChanged(self,handle, value):
        """ gets called when a multibit output has it's value changed
        """
        self.mboutputs[handle]._trigger("MbOutputChanged");
        self.MbOutputChanged(handle, value)

    def _pwmValueChanged(self,handle, value):
        """ gets called when a pwm pin has it's value changed
        """
        self.pwms[handle]._trigger("PwmValueChanged");
        self.PwmValueChanged(handle, value)

    def _buttonHandles(self):
        return self._call("Buttons",interface=self._dbus_itf_iogroup_digital)

    def _inputHandles(self):
        return self._call("Inputs",interface=self._dbus_itf_iogroup_digital)

    def _ouputHandles(self):
        return self._call("Outputs",interface=self._dbus_itf_iogroup_digital)

    def _mbInputHandles(self):
        return self._call("MbInputs",interface=self._dbus_itf_iogroup_digital)

    def _mbOuputHandles(self):
        return self._call("MbOutputs",interface=self._dbus_itf_iogroup_digital)

    def _pwmHandles(self):
        return self._call("Pwms",interface=self._dbus_itf_iogroup_digital)

        
PiIo.RegisterClass('nl.miqra.PiIo.IoGroup.Digital', PiIoGroupDigital)

class DigitalIoBase(object):
    '''
    Generic base object for Digital IO units
    '''

    def __init__(self,iogroup,handle):
        self._iogroup = iogroup
        self._handle = handle

    def Name(self):
        '''
        The name of this IO 
        '''
        return self._iogroup.Name() + "." + self.handle;
    
    @property
    def Handle(self):
        '''
        The handle of this IO 
        '''
        return str(self._handle)
    
    @property
    def Value(self):
        '''
        The current value of this IO 
        
        (returns the same as .value)
        '''
        return self._get()
    
    @Value.setter
    def Value(self,val):
        return self._set(val)

    # duplicate property with lowercase name
    @property
    def value(self):
        '''
        The current value of this IO 
        
        (returns the same as .Value)
        '''
        return self._get()
    
    @Value.setter
    def value(self,val):
        return self._set(val)

    # call a function on the IO Group 
    def _call(self, method, *args, **kwargs):
        kwargs['interface'] = self._iogroup._dbus_itf_iogroup_digital
        val = self._iogroup._call(method, *args, **kwargs)
#        print "Return value of {0} is {1}".format(method,val)
        return val

    # call a function on the IO Group that retu
    def _trycall(self, method, *args, **kwargs):
        kwargs['interface'] = self._iogroup._dbus_itf_iogroup_digital
        val = self._iogroup._trycall(method, *args, **kwargs)
#        print "Return value of {0} is {1}".format(method,val)
        return val

    # override this internal setter in child class
    def _set(self,value):
        raise NotImplementedError, "Value assignment not valid for this type of io"
    
    # override this internal getter in child class
    def _get(self,default=None):
        raise NotImplementedError, "Value retrieval not valid for this type of io"

    # override this internal trigger function to respond to events
    def _trigger(self,eventname,value=None):
        raise NotImplementedError, "Event triggering of event '{0}' with value '{1}' not valid for this io type".format(eventname,value)
        
class DigitalButton(DigitalIoBase):
    '''
    Handler class for Buttons
        
    Attributes:
        OnPress:     Event(handle) - an event triggers when this button is pressed
        OnHold:      Event(handle) - an event triggers when this button is held
    '''
    def __init__(self, iogroup, handle):
        DigitalIoBase.__init__(self,iogroup, handle)

        self.OnPress = Event();
        self.OnHold = Event();

    def _get(self,default=None):
        print "Test",self._handle
        return self._call("GetButton",self._handle,default=default)
    
    def _trigger(self,eventname, value=None):
        if value is None and eventname == "ButtonPress":
            self.OnPress()
        elif value is None and eventname == "ButtonHold":
            self.OnHold()
        else:
            DigitalIoBase._trigger(self,eventname,value)

# Handler class for Inputs
class DigitalInput(DigitalIoBase):
    '''
    Handler class for Inputs

    Attributes:
        OnChanged:     Event(handle) - an event triggers when the value is changed
    '''
    def __init__(self, iogroup, handle):
        DigitalIoBase.__init__(self,iogroup, handle)

        self.OnChanged = Event();

    def _get(self,default=None):
        return self._trycall("GetInput",self._handle,default=default)
    
    def _trigger(self,eventname, value=None):
        if eventname == "InputChanged":
            self.OnChanged(value)
        else:
            DigitalIoBase._trigger(self,eventname,value)
            

# Handler class for outputs
class DigitalOutput(DigitalIoBase):
    '''
    Handler class for Outputs

    Attributes:
        OnChanged:     Event(handle) - an event triggers when the value is changed
    '''
    def __init__(self, iogroup, handle):
        DigitalIoBase.__init__(self,iogroup, handle)

        self.OnChanged = Event();

    def _get(self,default=None):
        return self._trycall("GetOutput",self._handle,default=default)
        
    def _set(self, value):
        return self._trycall("SetOutput",self._handle)
    
    def _trigger(self,eventname, value=None):
        if eventname == "OutputChanged":
            self.OnChanged(value)
        else:
            DigitalIoBase._trigger(self,eventname,value)
            
class DigitalMbInput(DigitalIoBase):
    '''
    Handler class for Multibit Inputs

    Attributes:
        OnChanged:     Event(handle) - an event triggers when the value is changed
    '''
    def __init__(self, iogroup, handle):
        DigitalIoBase.__init__(self,iogroup, handle)

        self.OnChanged = Event();

    def _get(self,default=None):
        return self._trycall("GetMbInput",self._handle,default=default)
    
    def _trigger(self,eventname, value=None):
        if eventname == "MbInputChanged":
            self.OnChanged(value)
        else:
            DigitalIoBase._trigger(self,eventname,value)
            
class DigitalMbOutput(DigitalIoBase):
    '''
    Handler class for Multibit Outputs

    Attributes:
        OnChanged:     Event(handle) - an event triggers when the value is changed
    '''
    def __init__(self, iogroup, handle):
        DigitalIoBase.__init__(self,iogroup, handle)

        self.OnChanged = Event();

    def _get(self,default=None):
        return self._trycall("GetMbOutput",self._handle,default=default)
        
    def _set(self, value):
        return self._trycall("SetMbOutput",self._handle)
    
    def _trigger(self,eventname, value=None):
        if eventname == "MbOutputChanged":
            self.OnChanged(value)
        else:
            DigitalIoBase._trigger(self,eventname,value)
            
class DigitalPwm(DigitalIoBase):
    '''
    Handler class for PWMs

    Attributes:
        OnChanged:     Event(handle) - an event triggers when the value is changed
    '''
    def __init__(self, iogroup, handle):
        DigitalIoBase.__init__(self,iogroup, handle)

        self.OnChanged = Event();

    def _get(self,default=None):
        return self._trycall("GetPwm",self._handle,default=default)
        
    def _set(self, value):
        return self._trycall("SetPwm",self._handle)
    
    def _trigger(self,eventname, value=None):
        if eventname == "PwmValueChanged":
            self.OnChanged(value)
        else:
            DigitalIoBase._trigger(self,eventname,value)
