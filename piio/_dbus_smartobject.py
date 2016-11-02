import dbus
import dbus.service
import dbus.mainloop.glib
import _event

class NoConnectionError(Exception):
    pass

class DBusSmartObject:
    def __init__(self,service,path,interface,systembus=False, silent=False):
        # store service name and object path
        self._service = service
        self._object_path = path
        self._interface = interface
        self._silent = silent
        
        if systembus == True:
            self._bus_type = dbus.Bus.TYPE_SYSTEM
        else:
            self._bus_type = dbus.Bus.TYPE_SESSION

        # prepare flex object
        self._bus = None
        self._busobject = None
        self._beenconnected = False

        # set up the glib main loop.
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # connect to the dbus object to get information about existing connections
        self._dbus = dbus.Bus(dbus.Bus.TYPE_SYSTEM)
        self._dbus_object = self._dbus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')

        # contains interface name of dbus interface
        self._dbus_interface='org.freedesktop.DBus'

        # connect_to_signal registers our callback function.
        self._dbus_object.connect_to_signal('NameOwnerChanged', self._onNameOwnerChanged)

        # start initializing the connection
        self._initialize_new_connection()

    def close(self):
        if self._bus is not None:
            self._bus = None
            self._busobject = None

        if self._dbus is not None:
            self._dbus = None

    def _init_busobject(self,busobject):
        ''' Override in child class to initialize bus signals on connect and reconnect
        '''
        pass

    def _on_connection_lost(self):
        ''' Override in child class to handle connection lost
        '''
        pass

    def _on_connection_made(self):
        ''' Override in child class to handle connection made
        '''
        pass

    def _on_connection_regained(self):
        ''' Override in child class to handle connection regained
        '''
        pass

    def _initialize_new_connection(self):
        # test if service is available on the selected bus. Skip otherwise
        if self._dbus_object.NameHasOwner(self._service, dbus_interface=self._dbus_interface):

            if not self._silent:
                print "Initializing new connection to {0}:{1}".format(self._service,self._object_path)

            self._bus = dbus.Bus(self._bus_type)
            self._busobject = self._bus.get_object(self._service, self._object_path)
            self._init_busobject(self._busobject)
            self._on_connection_made()

            if self._beenconnected == True:
                self._on_connection_regained()
            else:
                self._beenconnected = True
        else:
            if not self._silent:
                print "Could not create connection to {0}:{1}".format(self._service,self._object_path)
            # bus object is not available - so disconnect the bus
            
            if self._bus is not None:
                self._bus = None
                self._busobject = None

    def _close_existing_connection(self):
        if self._bus is not None:
            if not self._silent:
                print "Lost connection to {0}:{1}".format(self._service,self._object_path)
            #self._bus.close()
            self._bus = None
            self._busobject = None
            self._on_connection_lost()

    def _onNameOwnerChanged(self,name,old_adr,new_adr):
        ''' Detects changes in service availablility
        '''
        if name == self._service:
            if old_adr == "":   # Service just became available
                self._initialize_new_connection()
            elif new_adr == "": # Service just became unavailable
                self._close_existing_connection()
            else:   # service changed address
                self._initialize_new_connection()
            
    def _call(self, method, *args, **kwargs):
        ''' Call a function on the registred dbus object
            When 'interface' is specified as a keyword argument, that interface is used for the call,
            otherwise the default interface for this object is used.
            Throws NoConnectionError when a dbus connection to the object is currently not available
        '''
        if kwargs.has_key("interface"):
            interface = kwargs["interface"]
        else:
            interface = self._interface
            
        if self._busobject is not None:
            #print "Attempting to call {0}".format(method)
            method = self._busobject.get_dbus_method(method,dbus_interface=interface)

            #print "Got method - calling with arguments: {0}".format(args)
            return method(*args)
        else:
            raise NoConnectionError("Currently no connection to service {0}:{1}".format(self._service,self._object_path))
            

    def _trycall(self,method, *args, **kwargs):
        ''' Call a function on the registred dbus object
            When 'interface' is specified as a keyword argument, that interface is used for the call,
            otherwise the default interface for this object is used.
            When 'default' is specified as a keyword argument, that is the value returned in case a
            dbus connection is not available. Otherwise None is returned.
            Does not throw any exception
        '''
        # see if we have an default return value in case of error
        if 'default' in kwargs:
            default = kwargs['default']
            del kwargs['default']
        else:
            default = None
        try:
            return self._call(method, *args, **kwargs)
        except NoConnectionError as x:
            if not self._silent:
                print "Could not call {0} because there is currently no connection to {1}:{2}".format(method,self._service,self._object_path)
            return default
            
    def connected(self):
        if self._busobject is not None:
            return True
        else:
            return False
        