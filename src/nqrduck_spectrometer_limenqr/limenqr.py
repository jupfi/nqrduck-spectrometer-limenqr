from nqrduck.module.module import Module
from nqrduck_spectrometer_limenqr.model import LimeNQRModel
from nqrduck_spectrometer_limenqr.view import LimeNQRView
from nqrduck_spectrometer_limenqr.controller import LimeNQRController

Spectrometer = Module(LimeNQRModel, LimeNQRView, LimeNQRController)