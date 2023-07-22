from nqrduck_spectrometer.base_spectrometer_view import BaseSpectrometerView


class LimeNQRView(BaseSpectrometerView):
    def __init__(self, module):
        super().__init__(module)

        self.widget = self.load_settings_ui()
        
