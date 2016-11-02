#!/usr/bin/env python

# event.py
#
# (C) 2011 Bram Kuijvenhoven

'''
Provides generic event object that allows callback registration to events. 

'''

class Event(object):
    '''
    Generic event object providing callback registration.
    
    Event listeners are callables.
    The semantics of the argument list to the callbacks is not hardcoded in this class;
    instead is it implied by the context where this Event object lives.
    Registration and unregistration are done by the += and -= operators.
    A callable can only be registered once and only be unregistered once.
    The event is fired by calling the event object itself with the desired parameters.    
    
    Example:
    
        >>> def listener(message):
        ...    print message;
        >>> event = Event();
        >>> event("x");
        >>> event += listener;
        >>> event("x");
        x
        >>> event -= listener;
        >>> event("x");

    '''
    def __init__(self):
        self.listeners = [];
    def __iadd__(self, listener):
        """
        Add new event listener.
        @param listener: callable; will be called whenever the event fires.
        @return: self.
        @raise ValueError: if the listener has already been registered for this event. 
        """
        if listener in self.listeners:
            raise ValueError("Listener already registered to event");
        self.listeners.append(listener);
        return self;
    def __isub__(self, listener):
        """
        Remove previously registered event listener.
        @param listener: previously registered event listener.
        @return: self.
        @raise ValueError: if the listener is not registered for this event.
        """
        if listener not in self.listeners:
            raise ValueError("Listener not registered to event");
        self.listeners.remove(listener);
        return self;
    def __call__(self, *args, **kwargs):
        """
        Fire event, passing the specified arguments to all listeners.
        Each listener will be called with listener(*args, **kwargs).
        """
        for listener in list(self.listeners):
            listener(*args, **kwargs);
