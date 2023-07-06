import logging
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)


class LimeNQRModel(ModuleModel):
    def __init__(self, module) -> None:
        super().__init__(module)

    @property
    def rx_antenna(self):
        return self._rx_antenna
    
    @rx_antenna.setter
    def rx_antenna(self, value):
        self._rx_antenna = value

    @property
    def tx_antenna(self):
        return self._tx_antenna
    
    @tx_antenna.setter
    def tx_antenna(self, value):
        self._tx_antenna = value

    @property
    def rx_gain(self):
        return self._rx_gain

    @rx_gain.setter
    def rx_gain(self, value):
        self._rx_gain = value

    @property
    def tx_gain(self):
        return self._tx_gain
    
    @tx_gain.setter
    def tx_gain(self, value):
        self._tx_gain = value

    @property
    def rx_lpfbw(self):
        return self._rx_lpfbw
    
    @rx_lpfbw.setter
    def rx_lpfbw(self, value):
        self._rx_lpfbw = value

    @property
    def tx_lpfbw(self):
        return self._tx_lpfbw
    
    @tx_lpfbw.setter
    def tx_lpfbw(self, value):
        self._tx_lpfbw = value

    @property
    def rx_freq(self):
        return self._rx_freq
    
    @rx_freq.setter
    def rx_freq(self, value):
        self._rx_freq = value
