import datetime

class lecroy_hro66zi():

    # Constructor
    def __init__(self, pyvisa_instr, timeout=10000, debug=False):
        self.scope = pyvisa_instr      # this is the pyvisa instrument
        self.num_analog_channels  = 4  # counted 1 to 4
        self.num_digital_channels = 36 # counted 0 to 35
        self.num_measure_channels = 8  # counted 1 to 8
        self.scope.timeout = timeout   # this is in milliseconds and needed for screen capture
        self.debug = debug

    def get_digital_channel_setup(self):
        digital_channels = {}
        for sweep_channels in range(0, self.num_digital_channels):
            if (int(self.scope.query('VBS? return = app.LogicAnalyzer.Digital1.Digital{0}.Value'.format(sweep_channels)).replace("VBS ","")) == -1):
                label = self.scope.query('VBS? return = app.LogicAnalyzer.Digital1.LineNames.Value').replace("VBS ", "").split(',')[sweep_channels]
                digital_channels[sweep_channels] = label
        return digital_channels

    def set_digital_channel_setup(self, digital_ch_dict):
        # --- Turn off all digital channels ---
        for sweep_channels in range(0, self.num_digital_channels):
            self.scope.write('VBS app.LogicAnalyzer.Digital1.Digital{0}.Value=false'.format(sweep_channels))
        # --- Turn on all listed digital channels and set up ---
        for k, v in digital_ch_dict.items():
            self.scope.write('VBS app.LogicAnalyzer.Digital1.Digital{0}.Value=true'.format(k))
            self.set_digital_label(num=k, label=v) # unique
        self.scope.write('VBS app.LogicAnalyzer.Digital1.View=true')
        self.scope.write('VBS app.LogicAnalyzer.Digital1.VerPosition=4.00')
        self.scope.write('VBS app.LogicAnalyzer.Digital1.LineHeight=0.24') # unique
        self.scope.write('VBS app.LogicAnalyzer.Digital1.Labels="CUSTOM"')

    # unique
    def set_digital_label(self, num, label):
        list_names = self.scope.query('VBS? return = app.LogicAnalyzer.LineNames').rstrip().replace("VBS ", "").strip("()").split(',')
        list_names[num] = label
        new_names = ",".join(list_names)
        self.scope.write('VBS \'app.LogicAnalyzer.Digital1.LineNames="{0}"\''.format(new_names))

    def get_analog_channel_setup(self):
        analog_channels = {}
        for sweep_channels in range(1, self.num_analog_channels+1):
            if (int(self.scope.query('VBS? return = app.Acquisition.C{0}.View'.format(sweep_channels)).replace("VBS ","")) == -1):
                label = ''
                if (int(self.scope.query('VBS? return = app.Acquisition.C{0}.ViewLabels'.format(sweep_channels)).replace("VBS ", "")) == -1):
                    label = str(self.scope.query('VBS? return = app.Acquisition.C{0}.labelsText'.format(sweep_channels)).strip())
                ver_scale = float(self.scope.query('VBS? return = app.Acquisition.C{0}.VerScale'.format(sweep_channels)).strip().replace("VBS ", ""))
                ver_offset = float(self.scope.query('VBS? return = app.Acquisition.C{0}.VerOffset'.format(sweep_channels)).strip().replace("VBS ", ""))
                bandwidth_lim = str(self.scope.query('VBS? return = app.Acquisition.C{0}.BandwidthLimit'.format(sweep_channels)).strip())
                coupling = str(self.scope.query('VBS? return = app.Acquisition.C{0}.Coupling'.format(sweep_channels)).strip())
                analog_channels[sweep_channels] = (label, ver_scale, ver_offset, bandwidth_lim, coupling)
        return analog_channels

    def set_analog_channel_setup(self, analog_ch_dict):
        ch_desc = {
            'label':      0,
            'ver_scale':  1,
            'ver_offset': 2,
            'bw':         3,  # '20MHz', 'Full'
            'coupling':   4,  # 'DC50', 'Gnd', 'DC1M', 'AC1M'
        }
        # --- Turn off all analog channels ---
        for sweep_channels in range(1, self.num_analog_channels+1):
            self.scope.write('VBS app.Acquisition.C{0}.View=False'.format(sweep_channels))

        # --- Turn on all listed analog channels and set up ---
        for k, v in analog_ch_dict.items():
            self.scope.write('VBS app.Acquisition.C{0}.View=True'.format(k))
            self.scope.write('VBS app.Acquisition.C{0}.ViewLabels=True'.format(k))
            self.scope.write('VBS app.Acquisition.C{0}.LabelsText="{1}"'.format(k, v[ch_desc['label']]))
            self.scope.write('VBS app.Acquisition.C{0}.VerScale={1}'.format(k, v[ch_desc['ver_scale']]))
            self.scope.write('VBS app.Acquisition.C{0}.VerOffset={1}'.format(k, v[ch_desc['ver_offset']]))
            self.scope.write('VBS app.Acquisition.C{0}.BandwidthLimit="{1}"'.format(k, v[ch_desc['bw']]))
            self.scope.write('VBS app.Acquisition.C{0}.Coupling="{1}"'.format(k, v[ch_desc['coupling']]))

    def get_horizontal_scale(self):
        return float(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorScale').strip().replace("VBS ", ""))

    def set_horizontal_scale(self, scale=1E-3):
        self.scope.write('VBS app.Acquisition.Horizontal.HorScale=' + str(scale))

    def get_trigger_setup(self):
        trigger_list = []
        trigger_list.append(self.scope.query('VBS? return = app.Acquisition.Trigger.Source').rstrip().replace("VBS ", ""))
        trigger_list.append(self.scope.query('VBS? return = app.Acquisition.Trigger.Type').rstrip().replace("VBS ", ""))
        trigger_list.append(self.scope.query('VBS? return = app.Acquisition.Trigger.Edge.Level').rstrip().replace("VBS ", ""))
        trigger_list.append(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorOffset').rstrip().replace("VBS ", ""))
        trigger_list.append(self.scope.query('VBS? return = app.Acquisition.Trigger.Edge.Slope').rstrip().replace("VBS ", ""))
        trigger_list.append(self.scope.query('VBS? return = app.Acquisition.TriggerMode').rstrip().replace("VBS ", ""))
        return trigger_list

    def set_trigger_setup(self, trigger_list=['C1', 'Edge', '2', '0', 'Positive', 'Auto', '', 'Positive', '0.0002', '0.0001']):
        self.scope.write('VBS app.Acquisition.Trigger.Source="{0}"'.format(trigger_list[0]))
        self.scope.write('VBS app.Acquisition.Trigger.Type="{0}"'.format(trigger_list[1]))
        self.scope.write('VBS app.Acquisition.Trigger.Edge.Level={0}'.format(trigger_list[2]))
        self.scope.write('VBS app.Acquisition.Horizontal.HorOffset={0}'.format(trigger_list[3]))
        self.scope.write('VBS app.Acquisition.Trigger.Edge.Slope="{0}"'.format(trigger_list[4]))
        self.scope.write('VBS app.Acquisition.TriggerMode="{0}"'.format(trigger_list[5]))
        if (trigger_list[0].startswith('C')):
            self.scope.write('VBS app.Acquisition.Trigger.Coupling="AC"'.format(trigger_list[0]))

    def get_measurement_setup(self):
        measure_channels = {}
        for sweep_channels in range(1, self.num_measure_channels+1):
            if (int(self.scope.query('VBS? return = app.Measure.P{0}.View'.format(sweep_channels)).replace("VBS ","")) == -1):
                source = str(self.scope.query('VBS? return = app.Measure.P{0}.Source1'.format(sweep_channels)).strip().replace("VBS ",""))
                measurement = str(self.scope.query('VBS? return = app.Measure.P{0}.ParamEngine'.format(sweep_channels)).strip().replace("VBS ",""))
                measure_channels[sweep_channels] = (source, measurement)
        return measure_channels

    def set_measurement_setup(self, meas_dict):
        meas_desc = { 'source':      0,
                      'measurement': 1 }

        # --- Turn off all measurements ---
        for sweep_measurements in range(1, self.num_measure_channels+1):
            self.scope.write('VBS app.Measure.P{0}.View=False'.format(sweep_measurements))

        # --- Turn on all listed measurements and set up ---
        for k, v in meas_dict.items():
            self.scope.write('VBS app.Measure.P{0}.View=True'.format(k))
            self.scope.write('VBS app.Measure.P{0}.Source1="{1}"'.format(k, v[meas_desc['source']]))
            self.scope.write('VBS app.Measure.P{0}.ParamEngine="{1}"'.format(k, v[meas_desc['measurement']]))

    def get_measurement_val(self, meas_channel=0):
        return float(self.scope.query('VBS? return = app.Measure.P{0}.Out.Result.Value'.format(str(meas_channel))).rstrip().replace("VBS ",""))

    import datetime
    def get_screen_image(self, path_with_filename='', backcolor='BLACK'):
        # valid backcolor can be either 'WHITE' or 'BLACK'
        self.scope.write("CHDR OFF;HCSU BCKG,%s;HCSU DEV,PNG;HCSU PORT,GPIB;SCDP" % backcolor)
        raw_data = self.scope.read_raw()
        if (path_with_filename == ''):
            path_with_filename = "C:\\temp\\python\\lecroy_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        elif '.png' not in path_with_filename:  # append png if not given
            path_with_filename += '.png'
        file_stream = open(path_with_filename, 'wb')
        file_stream.write(raw_data)
        file_stream.close()
        return len(raw_data)

    def set_grid(self, gridmode='Single'):
        """
        Sets the number grids on the display.
        :param gridmode: possible values: 'Single', 'Dual', 'Quad', 'Octal', 'Tandem', 'Quattro', 'Auto'
        :return: None
        """
        self.scope.write('VBS app.Display.GridMode="{}"'.format(gridmode))

    def get_horizontal_divs(self):
        delay = float(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorOffset').rstrip())
        scale = float(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorScale').strip().replace("VBS ", ""))
        return int((1E9 * delay) / (1E9 * scale))

    def set_horizontal_divs(self, div):
        scale = float(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorScale').strip().replace("VBS ", ""))
        self.scope.write('VBS app.Acquisition.Horizontal.HorOffset={0}'.format(div * scale))

    def select_analog_channel_foreground_display(self, analog_channel_num=1):
        self.scope.write('VBS app.Acquisition.C{0}.View=False'.format(analog_channel_num))
        self.scope.write('VBS app.Acquisition.C{0}.View=True'.format(analog_channel_num))

    def channel_absolute_scale_and_offset(self, analog_channel_num, verscale,veroffset):  # absolute scale and absolute offset
        self.scope.write('VBS app.Acquisition.C{0}.VerScale="{1}"'.format(analog_channel_num, verscale))
        self.scope.write('VBS app.Acquisition.C{0}.VerOffset={1}'.format(analog_channel_num, veroffset))
        actual_offset = float(
            self.scope.query('VBS? return = app.Acquisition.C{0}.VerOffset'.format(analog_channel_num)).rstrip().replace("VBS ", ""))
        if (actual_offset < veroffset):
            print("!!! WARNING: your requested offset of " + str(veroffset) + " is different to actual offset of " + str(actual_offset) + " !!!")

    def set_measurement_levelatx(self, meas_num=1, position_divs=0):
        hor_delay = float(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorOffset').rstrip().replace("VBS ", ""))
        hor_scale = float(self.scope.query('VBS? return = app.Acquisition.Horizontal.HorScale').strip().replace("VBS ", ""))
        relative_divs = position_divs - int((1E9 * hor_delay) / (1E9 * hor_scale))
        horvalue = relative_divs * hor_scale
        self.scope.write('VBS app.Measure.P{0}.operator.horvalue={1}'.format(meas_num, horvalue))

    def set_measurement_gate(self, meas_num=1, start_div=0, stop_div=10):  # div 0 is the leftmost, div 10 is the rightmost
        self.scope.write('VBS app.Measure.P{0}.GateStart={1}'.format(meas_num, start_div))
        self.scope.write('VBS app.Measure.P{0}.GateStop={1}'.format(meas_num, stop_div))

    def set_measurement_math(self, meas_num=1, psource1_num=2, psource2_num=3, arithengine='paramDifference'):
        self.scope.write('VBS app.Measure.P{0}.MeasurementType="math"'.format(meas_num))
        self.scope.write('VBS app.Measure.P{0}.PSource1="P{1}"'.format(meas_num, psource1_num))
        self.scope.write('VBS app.Measure.P{0}.PSource2="P{1}"'.format(meas_num, psource2_num))
        self.scope.write('VBS app.Measure.P{0}.ArithEngine="{1}"'.format(meas_num, arithengine))
        self.scope.write('VBS app.Measure.P{0}.View=True'.format(meas_num))
