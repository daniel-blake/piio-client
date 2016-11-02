import _piio
import _piio_digital
import _piio_pwm

piio = _piio.PiIo()

__all__ = ['piio']

for _g in piio.IoGroups():
    if not _g.Name in globals():
        globals()[_g.Name] = _g
        __all__.append(_g.Name)
    else:
        print "piio error: Cannot register IO Group '{0}' because it conflicts with an existing python variable with the same name".format(_g.Name)
    
   