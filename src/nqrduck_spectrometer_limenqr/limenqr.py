"""BaseSpectrometer for Lime NQR spectrometer."""

from nqrduck_spectrometer.base_spectrometer import BaseSpectrometer
from .model import LimeNQRModel
from .view import LimeNQRView
from .controller import LimeNQRController

LimeNQR = BaseSpectrometer(LimeNQRModel, LimeNQRView, LimeNQRController)
