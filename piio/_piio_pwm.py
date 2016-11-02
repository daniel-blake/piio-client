import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from _event import Event
from _dbus_smartobject import DBusSmartObject,NoConnectionError
from _piio import PiIo, PiIoGroup, PiIoDict

class PiIoGroupPwm (PiIoGroup):
    '''
    Access piio Digital IO Groups
    
    Attributes:
        PwmValueChanged: Event(handle, value) - an event triggers when a pwm value changed

    Note that the handle provided on these events is the short handle relative to this IO Group.
        
    '''
    def __init__(self,path):
        '''
        Initialize the object for a Digital IO Group connection
        '''
        
        self._dbus_itf_iogroup_pwm='nl.miqra.PiIo.IoGroup.Pwm'

        # declare events
        self.PwmValueChanged = Event() # arguments: handle, value
        self.pwms = PiIoDict()

        PiIoGroup.__init__(self,path)

    def _init_busobject(self,busobject):
        PiIoGroup._init_busobject(self,busobject)
        
        # connect_to_signal registers our callback function.
        busobject.connect_to_signal('PwmValueChanged', self._pwmValueChanged)

        # register pwms 
        # catch an exception that occurs if we're not connected
        try:
            # add pwms if they were not already registered (in case of reconnect
            for handle in self._pwmHandles():
                handle = str(handle)
                if not self.pwms.has_key(handle):
                    o = PwmOutput(self, handle)
                    self.pwms[handle] = o

        except NoConnectionError as x:
            print "Error: Lost connection to piio-server during initialization"
            
    def _pwmValueChanged(self,handle, value):
        """ gets called when a pwm pin has it's value changed
        """
        self.pwms[handle]._trigger("PwmValueChanged");
        self.PwmValueChanged(handle, value)

    def _pwmHandles(self):
        return self._call("Pwms",interface=self._dbus_itf_iogroup_pwm)

PiIo.RegisterClass('nl.miqra.PiIo.IoGroup.Pwm', PiIoGroupPwm)

class PwmOutput(object):
    '''
    Generic base object for Digital IO units
    '''

    def __init__(self,iogroup,handle):
        self._iogroup = iogroup
        self._handle = handle
        self.OnChanged = Event();
		
		
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
    def Min(self):
        '''
        Minimum value of pwm
        '''
        return self._trycall("GetMin",self._handle,default=None)

    @property
    def Max(self):
        '''
        Maximum value of pwm
        '''
        return self._trycall("GetMax",self._handle,default=None)
	
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
        kwargs['interface'] = self._iogroup._dbus_itf_iogroup_pwm
        val = self._iogroup._call(method, *args, **kwargs)
#        print "Return value of {0} is {1}".format(method,val)
        return val

    # call a function on the IO Group that retu
    def _trycall(self, method, *args, **kwargs):
        kwargs['interface'] = self._iogroup._dbus_itf_iogroup_pwm
        val = self._iogroup._trycall(method, *args, **kwargs)
#        print "Return value of {0} is {1}".format(method,val)
        return val

    def _get(self,default=None):
        return self._trycall("GetValue",self._handle,default=default)
        
    def _set(self, value):
        return self._trycall("SetValue",self._handle,value)
    
    def _trigger(self,value=None):
		self.OnChanged(value)
