import logging
import tempfile
from pathlib import Path
import numpy as np
from decimal import Decimal
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.base_spectrometer_controller import BaseSpectrometerController
from nqrduck_spectrometer.measurement import Measurement
from nqrduck_spectrometer.pulseparameters import TXPulse, RXReadout

logger = logging.getLogger(__name__)


class LimeNQRController(BaseSpectrometerController):
    def __init__(self, module):
        super().__init__(module)

    def start_measurement(self):
        logger.debug(
            "Starting measurement with spectrometer: %s", self.module.model.name
        )
        # Now we request the pulse sequence set in the pulse programmer module
        pulse_sequence = self.module.model.pulse_programmer.model.pulse_sequence
        logger.debug("Pulse sequence is: %s", pulse_sequence.to_json())

        try:
            from .contrib.limr import limr

            self_path = Path(__file__).parent
            driver_path = str(self_path / "contrib/pulseN_test_USB.cpp")
            lime = limr(driver_path)
        except ImportError as e:
            logger.error("Error while importing limr. %s", e)
        except Exception as e:
            logger.error("Error while loading pulseN_test_USB.cpp: %s", e)

        lime.noi = -1  # No initialisation
        lime.nrp = 1  # Numer of repetitions

        lime = self.update_settings(lime)
        lime = self.translate_pulse_sequence(lime)
        

        lime.nav = self.module.model.averages

        for key in sorted(lime.parsinp):
            val = getattr(lime, key)
            if val != []:
                # logger.debug("Attribute: %s, Value: %s, Descr.: %s" % key, val, lime.parsinp[key][1])
                logger.debug(key + ": " + str(val) + " " + lime.parsinp[key][1])

        # Create temp folder for .hdf files
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name)
        logger.debug("Created temporary directory: %s", path)
        lime.spt = path
        lime.fpa = "temp"

        # Write to statusbar
        self.module.nqrduck_signal.emit("statusbar_message", "Started Measurement")

        logger.debug("Starting measurement")
        lime.run()

        logger.debug("Reading hdf file")
        lime.readHDF()

        rx_begin, rx_stop = self.translate_rx_event(lime)
        logger.debug("RX event starts at: %s and ends at: %s", rx_begin, rx_stop)

        # evaluation range, defines: blanking time and window length
        evran = [rx_begin, rx_stop]

        # np.where sometimes does not work out, so it is put in a try except
        # always check the console for errors
        try:
            evidx = np.where((lime.HDF.tdx > evran[0]) & (lime.HDF.tdx < evran[1]))[0]
        except:
            logger.error("Error while reading the measurement data")
            self.module.nqrduck_signal.emit("measurement_error", "Error with measurement data. Did you set an RX event?")
            return -1

        # time domain x and y data
        tdx = lime.HDF.tdx[evidx] - lime.HDF.tdx[evidx][0]
        tdy = lime.HDF.tdy[evidx] / lime.nav

        fft_shift = self.module.model.get_setting_by_name(self.module.model.FFT_SHIFT).value

        if fft_shift:
            fft_shift = self.module.model.if_frequency
        else:
            fft_shift = 0

        measurement_data = Measurement(
            tdx,
            tdy,
            self.module.model.target_frequency,
            frequency_shift=fft_shift,
        )

        # Emit the data to the nqrduck core
        logger.debug("Emitting measurement data")
        self.module.nqrduck_signal.emit("statusbar_message", "Finished Measurement")

        self.module.nqrduck_signal.emit("measurement_data", measurement_data)

    def update_settings(self, lime):
        """This method sets the parameters of the limr object according to the settings set in the spectrometer module.

        Args:
            lime (limr): The limr object that is used to communicate with the pulseN driver

        Returns:
            limr: The updated limr object"""

        logger.debug(
            "Updating settings for spectrometer: %s for measurement",
            self.module.model.name,
        )
        lime.t3d = [0, 0, 0, 0]
        for category in self.module.model.settings.keys():
            for setting in self.module.model.settings[category]:
                logger.debug("Setting %s has value %s", setting.name, setting.value)
                # Acquisiton settings
                if setting.name == self.module.model.SAMPLING_FREQUENCY:
                    lime.sra = setting.get_setting()
                # Careful this doesn't only set the IF frequency but the local oscillator frequency
                elif setting.name == self.module.model.IF_FREQUENCY:
                    lime.lof = (
                        self.module.model.target_frequency - setting.get_setting()
                    )
                    self.module.model.if_frequency = setting.get_setting()
                elif setting.name == self.module.model.ACQUISITION_TIME:
                    lime.tac = setting.get_setting()
                # Gate settings
                elif setting.name == self.module.model.GATE_ENABLE:
                    lime.t3d[0] = int(setting.value)
                elif setting.name == self.module.model.GATE_PADDING_LEFT:
                    lime.t3d[1] = int(setting.get_setting())
                elif setting.name == self.module.model.GATE_SHIFT:
                    lime.t3d[2] = int(setting.get_setting())
                elif setting.name == self.module.model.GATE_PADDING_RIGHT:
                    lime.t3d[3] = int(setting.get_setting())
                # RX/TX settings
                elif setting.name == self.module.model.TX_GAIN:
                    lime.tgn = setting.get_setting()
                elif setting.name == self.module.model.RX_GAIN:
                    lime.rgn = setting.get_setting()
                elif setting.name == self.module.model.RX_LPF_BW:
                    lime.rlp = setting.get_setting()
                elif setting.name == self.module.model.TX_LPF_BW:
                    lime.tlp = setting.get_setting()
                # Calibration settings
                elif setting.name == self.module.model.TX_I_DC_CORRECTION:
                    lime.tdi = setting.get_setting()
                elif setting.name == self.module.model.TX_Q_DC_CORRECTION:
                    lime.tdq = setting.get_setting()
                elif setting.name == self.module.model.TX_I_GAIN_CORRECTION:
                    lime.tgi = setting.get_setting()
                elif setting.name == self.module.model.TX_Q_GAIN_CORRECTION:
                    lime.tgq = setting.get_setting()
                elif setting.name == self.module.model.TX_PHASE_ADJUSTMENT:
                    lime.tpc = setting.get_setting()
                elif setting.name == self.module.model.RX_I_DC_CORRECTION:
                    lime.rdi = setting.get_setting()
                elif setting.name == self.module.model.RX_Q_DC_CORRECTION:
                    lime.rdq = setting.get_setting()
                elif setting.name == self.module.model.RX_I_GAIN_CORRECTION:
                    lime.rgi = setting.get_setting()
                elif setting.name == self.module.model.RX_Q_GAIN_CORRECTION:
                    lime.rgq = setting.get_setting()
                elif setting.name == self.module.model.RX_PHASE_ADJUSTMENT:
                    lime.rpc = setting.get_setting()

        return lime

    def translate_pulse_sequence(self, lime):
        """This method sets the parameters of the limr object according to the pulse sequence set in the pulse programmer module#
        This is only relevant for the tx pulse parameters. General settings are set in the update_settings method and the rx event is
        handled in the translate_rx_event method.

        Args:
            lime (limr): The limr object that is used to communicate with the pulseN driver

        Returns:
            limr: The updated limr object
        """
        events = self.module.model.pulse_programmer.model.pulse_sequence.events

        for event in events:
            logger.debug("Event %s has parameters: %s", event.name, event.parameters)
            for parameter in event.parameters.values():
                logger.debug(
                    "Parameter %s has options: %s", parameter.name, parameter.options
                )

                if (
                    parameter.name == self.module.model.TX
                    and parameter.get_option_by_name(TXPulse.RELATIVE_AMPLITUDE).value
                    > 0
                ):
                    pulse_shape = parameter.get_option_by_name(
                        TXPulse.TX_PULSE_SHAPE
                    ).value
                    pulse_amplitude = abs(pulse_shape.get_pulse_amplitude(event.duration))

                    # Apply the relative amplitude
                    pulse_amplitude *= parameter.get_option_by_name(TXPulse.RELATIVE_AMPLITUDE).value

                    # Calculate the number of samples
                    num_samples = int(float(event.duration) * lime.sra)

                    # Create the time vector for the pulse duration
                    tdx = np.linspace(0, float(event.duration), num_samples, endpoint=False)

                    # Create the full complex exponential for modulation
                    # This represents a rotating vector (phasor) at your IF
                    shift_signal = np.exp(1j * 2 * np.pi * self.module.model.if_frequency * tdx)

                    # pulse_amplitude is your desired pulse envelope, defined earlier
                    # Let's assume that pulse_amplitude is a real-valued vector with values corresponding to the amplitude of each sample

                    # Apply the shift by multiplying with the complex exponential
                    pulse_complex = pulse_amplitude * shift_signal

                    # Calculate amplitude and phase from the complex signal
                    modulated_amplitude = np.abs(pulse_complex)
                    modulated_phase = np.angle(pulse_complex)  # This returns the phase in radians

                    # For SDRs that require phase between 0 and 2*pi
                    modulated_phase = np.unwrap(modulated_phase)  # To correct discontinuities
                    modulated_phase = (modulated_phase + 2 * np.pi) % (2 * np.pi)  # Shift to [0, 2*pi] range

                    # Apply the shift by multiplying the time domain signal
                    pulse_amplitude = (modulated_amplitude)

                    # Clip the pulse amplitude to a minimum and maximum value of -0.99 and 0.99
                    # this is kind of ugly but it prevents some kind of issue with the pulse clipping
                    # I'm not sure why this happens but it seems to be related to the pulse shape
                    # rectangular pulses seem to be the most effected by this
                    pulse_amplitude = np.clip(pulse_amplitude, -0.99, 0.99)

                    if len(lime.pfr) == 0:
                        # Add the TX pulse to the pulse frequency list (lime.pfr)
                        lime.pfr = [
                            float(self.module.model.if_frequency)
                            for i in range(len(pulse_amplitude))
                        ]
                        # Add the duration of the TX pulse to the pulse duration list (lime.pdr)
                        lime.pdr = [
                            float(pulse_shape.resolution)
                            for i in range(len(pulse_amplitude))
                        ]
                        # Add the TX pulse amplitude to the pulse amplitude list (lime.pam)
                        lime.pam = list(pulse_amplitude)
                        # Add the pulse offset to the pulse offset list (lime.pof)
                        # This leads to a default offset of 300 samples for the first pulse
                        lime.pof = [self.module.model.OFFSET_FIRST_PULSE]
                        lime.pof += [
                            int(pulse_shape.resolution * Decimal(lime.sra))
                            for i in range(len(pulse_amplitude) -1)
                        ]
                        lime.pph = list(modulated_phase)
                        # Add the TX pulse phase to the pulse phase list (lime.pph) -> not yet implemented
                    else:
                        logger.debug("Adding TX pulse to existing pulse sequence")
                        lime.pfr += [
                                float(self.module.model.if_frequency)
                                for i in range(len(pulse_amplitude))
                        ]
    
                        lime.pdr += [
                                float(pulse_shape.resolution)
                                for i in range(len(pulse_amplitude))
                        ]
        
                        # Setting pulse amplitude
                        lime.pam += list(pulse_amplitude)
                        # Setting pulse phase
                        lime.pph += list(modulated_phase)
                        # Get the length of the previous event without a tx pulse
                        blank = []
                        previous_events = events[: events.index(event)]
                        # Firstuful this is ugly as hell and needs to be refactored
                        # Secondly this just sets the pulse offsets.
                        for prev_event in previous_events[::-1]:
                            logger.debug(
                                "Previous event: %s with duration: %s",
                                prev_event.name,
                                prev_event.duration,
                            )
                            for parameter in prev_event.parameters.values():
                                if (
                                    parameter.name == self.module.model.TX
                                    and parameter.get_option_by_name(
                                        TXPulse.RELATIVE_AMPLITUDE
                                    ).value
                                    == 0
                                ):
                                    blank.append(float(prev_event.duration))
                                elif (
                                    parameter.name == self.module.model.TX
                                    and parameter.get_option_by_name(
                                        TXPulse.RELATIVE_AMPLITUDE
                                    ).value
                                    > 0
                                ):
                                    break
                            else:
                                continue
                            break

                        logger.debug("Found blanks: %s", blank)

                        prev_duration = lime.pdr[-2] + sum(blank)

                        logger.debug("Setting pulse offset to: %s", prev_duration)
                        lime.pof.append(int(np.ceil(prev_duration * lime.sra)))
                        lime.pof += [
                            int(float(pulse_shape.resolution) * lime.sra)
                            for i in range(len(pulse_amplitude) - 1)
                        ]

            # The last event is the repetition time event
            lime.trp = float(event.duration)

        lime.npu = len(lime.pfr)
        return lime

    def translate_rx_event(self, lime):
        """This method translates the RX event of the pulse sequence to the limr object.

        Args:
            lime (limr): The limr object that is used to communicate with the pulseN driver


        Returns:
            tuple: A tuple containing the start and stop time of the RX event in µs"""
        # This is a correction factor for the RX event. The offset of the first pulse is 2.2µs longer than from the specified samples.
        #CORRECTION_FACTOR = 2.4e-6
        CORRECTION_FACTOR = self.module.model.get_setting_by_name(self.module.model.RX_OFFSET).value
        events = self.module.model.pulse_programmer.model.pulse_sequence.events

        previous_events_duration = 0
        offset = 0
        rx_duration = 0
        for event in events:
            logger.debug("Event %s has parameters: %s", event.name, event.parameters)
            for parameter in event.parameters.values():
                logger.debug(
                    "Parameter %s has options: %s", parameter.name, parameter.options
                )

                if (
                    parameter.name == self.module.model.RX
                    and parameter.get_option_by_name(RXReadout.RX).value
                ):
                    # Get the length of all previous events
                    previous_events = events[: events.index(event)]
                    previous_events_duration = sum(
                        [event.duration for event in previous_events]
                    )
                    # Get the offset of the first pulse
                    offset = self.module.model.OFFSET_FIRST_PULSE * (1 / lime.sra)
                    rx_duration = event.duration

        rx_begin = float(previous_events_duration) + offset + CORRECTION_FACTOR
        if rx_duration:
            rx_stop = rx_begin + float(rx_duration)
            return rx_begin * 1e6, rx_stop * 1e6

        else:
            return None, None

    def set_frequency(self, value: float):
        """This method sets the target frequency of the spectrometer.

        Args:
            value (float): The target frequency in MHz
        """
        logger.debug("Setting frequency to: %s", value)
        try:
            self.module.model.target_frequency = float(value)
            logger.debug("Successfully set frequency to: %s", value)
        except ValueError:
            logger.warning("Could not set frequency to: %s", value)
            self.module.nqrduck_signal.emit(
                "notification", ["Error", "Could not set frequency to: " + value]
            )
            self.module.nqrduck_signal.emit("failure_set_frequency", value)

    def set_averages(self, value: int):
        """This method sets the number of averages for the spectrometer.

        Args:
            value (int): The number of averages"""
        logger.debug("Setting averages to: %s", value)
        try:
            self.module.model.averages = int(value)
            logger.debug("Successfully set averages to: %s", value)
        except ValueError:
            logger.warning("Could not set averages to: %s", value)
            self.module.nqrduck_signal.emit(
                "notification", ["Error", "Could not set averages to: " + value]
            )
            self.module.nqrduck_signal.emit("failure_set_averages", value)
