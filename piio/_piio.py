import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from _event import Event
from _dbus_smartobject import DBusSmartObject,NoConnectionError

class PiIoDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

class PiIo(DBusSmartObject):
    '''
    The main access point for the PIIO system
    
    Attributes:
        OnButtonPress:     Event(handle) - an event triggers when a button is pressed
        OnButtonHold:      Event(handle) - an event triggers when a button is held
        OnInputChanged:    Event(handle, value) - an event triggers when an input's value changed
        OnMbInputChanged:  Event(handle, value) - an event triggers when a multibit input's value changed
    
    Note that the handle provided on these events is the long handle form consisting of [iogroup].[handlename] 
    '''

    _classmap = {}

    @classmethod
    def RegisterClass(cls, interface, class_):
        cls._classmap[interface] = class_

    @classmethod
    def FindClass(cls, interface):
        return cls._classmap[interface];

    def __init__(self):
        '''
        Initialize an object that links to the main piio object
        '''
        # initialize the event
        self.OnButtonPress = Event()
        self.OnButtonHold = Event()
        self.OnInputChanged = Event()
        self.OnMbInputChanged = Event()

        DBusSmartObject.__init__(   self, 
                                    service='nl.miqra.PiIo', 
                                    path='/nl/miqra/PiIo',
                                    interface='nl.miqra.PiIo', 
                                    systembus=True)       

    def _init_busobject(self,busobject):

        # connect_to_signal registers our callback function.
        busobject.connect_to_signal('OnButtonPress', self._onButtonPress)

        # connect_to_signal registers our callback function.
        busobject.connect_to_signal('OnButtonHold', self._onButtonHold)

        # connect_to_signal registers our callback function.
        busobject.connect_to_signal('OnInputChanged', self._onInputChanged)

        # connect_to_signal registers our callback function.
        busobject.connect_to_signal('OnMbInputChanged', self._onMbInputChanged)

    #callback functions for global input events

    def _onButtonPress(self,longhandle):
        """
        gets called when a button is pressed
        """
        self.OnButtonPress(longhandle)

    def _onButtonHold(self,longhandle):
        """
        gets called when a button is held
        """
        self.OnButtonHold(longhandle)

    def _onInputChanged(self,longhandle,value):
        """
        gets called when a single input pin changes value
        """
        self.OnInputChanged(longhandle,value)

    def _onMbInputChanged(self,longhandle,value):
        """
        gets called when a multibit input changes value
        """
        self.OnMbInputChanged(longhandle,value)        

    # public methods
    def IoGroups(self):
        '''
        Get a list of currently valid IO Groups
        '''
        paths = self._trycall("IoGroups",default=[])
        l = []
        for path in paths:
            # first object is to determine interface of group
            g = PiIoGroup(path,silent=True)
            # second object is actual connection
            o = self.__class__.FindClass(g.Interface)(path)
            l.append(o)
        return l

PiIo.RegisterClass("nl.miqra.PiIo", PiIo)

class PiIoGroup(DBusSmartObject):
    '''
    Base class for IO Groups to inherit from
    '''
    def __init__(self,path,silent=False):
        '''
        Initialize the base object for an IO Group connection
        '''
        DBusSmartObject.__init__(  self, 
                                                    service='nl.miqra.PiIo', 
                                                    path=path,
                                                    interface='nl.miqra.PiIo.IoGroup', 
                                                    systembus=True,
                                                    silent=silent)      

    # initalization for group access. will be called on first connect and each reconnect
    # override in child class
    def _init_busobject(self,busobject):
        pass
        
    @property
    def Name(self):
        '''
        The name of this IO Group
        '''
        return str(self._trycall("Name", default=None))

    @property
    def Interface(self):
        '''
        The main interface of this IO Group
        '''
        return str(self._trycall("Interface", default=None))

PiIo.RegisterClass("nl.miqra.PiIo.IoGroup", PiIoGroup)
