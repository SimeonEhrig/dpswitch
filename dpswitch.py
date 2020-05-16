#!/bin/python3

import json, sys, subprocess, re
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel
from PyQt5.QtCore import Qt

from typing import Dict

class DisplayModeButton():
    """ Each object of the class couple a display mode with a button

    """
    def __init__(self, name : str, config : Dict ,label : QLabel):
        """Create a button object

        :param name: name of the mode and the button
        :type name: str
        :param config: json config for the mode
        :type config: Dict
        :param label: A QLabel object which is used to print output and errors
        :type label: QLabel

        """
        self.name = name
        self.json = config
        self.label = label
        self.button = QPushButton(name)
        self.button.clicked.connect(self.callback)
        # if True, the label text is red, otherwise black
        self.error = False
        self.logger_text = ''

    # the logger functions make it easy to compose output and error messages
    # from anywhere in the class
    def logger_add(self, text : str, error=False):
        """Add a new text line to the output

        :param text: the message
        :type text: str
        :param error: if the True, the text is printed red
        :type error: Bool

        """
        if error:
            self.error = True
        self.logger_text += text + '\n'

    def logger_print(self):
        """Set the current logger_text as label text

        """
        if self.error:
            self.label.setStyleSheet('color: red')
        else:
            self.label.setStyleSheet('color: black')
        self.label.setText(self.logger_text)


    def logger_reset(self):
        """Delete the logger_text and set error to False

        """
        self.error = False
        self.logger_text = ''

    def enableDisplay(self, json : Dict):
        """Enable a display with the parameters specified by the Json

        :param json: parameter for the monitor
        :type json: Dict

        """
        command = ['xrandr',
                   '--output',
                   json['display'],
                   '--mode',
                   json['resolution'],
                   '--rate',
                   json['rate']]

        if 'position' in json:
            pos = json['position'][0]
            if pos == 'left':
                command.append('--left-of')
            if pos == 'right':
                command.append('--right-of')
            if pos == 'above':
                command.append('--above')
            if pos == 'below':
                command.append('--below')
            command.append(json['position'][1])

        self.logger_add(' '.join(command))

        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()
        error_code = process.wait()

        if error or error_code:
            self.logger_add(error.decode('utf-8'), True)

    def setPrimaryDisplay(self, name : str):
        """Set a enabled display as primary

        :param name: name of the display
        :type name: str

        """
        command = ['xrandr',
                   '--output',
                   name,
                   '--primary']

        self.logger_add(' '.join(command))

        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()
        error_code = process.wait()

        if error or error_code:
            self.logger_add(error.decode('utf-8'), True)


    def disableDisplay(self, name : str):
        """Disable a display specified by the name

        :param name: name of the display
        :type name: str

        """
        command = ['xrandr',
                   '--output',
                   name,
                   '--off']

        self.logger_add(' '.join(command))

        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()
        error_code = process.wait()

        if error or error_code:
            self.logger_add(error.decode('utf-8'), True)

    def callback(self):
        """Function, which is registered the at the button click. Change the
        monitor configuration.

        """
        self.logger_reset()

        # to avoid time-consuming switching on and off of displays, first
        # determine which display is enabled
        info_process = subprocess.Popen(['xrandr'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        info_output, info_error = info_process.communicate()

        # store the names of the enabled displays
        enabledDisplays = []
        for line in info_output.decode('utf-8').split('\n'):
            # each enabled display has the keyword 'connection' and a resolution
            # e.g.: HDMI-A-0 connected primary 1920x1080+0+0 (normal left
            # inverted right x axis y axis) 1600mm x 900mm
            if re.match(r'[0-9a-zA-Z\-]* (connected|connected primary) [0-9]*x[0-9]*\+[0-9]*\+[0-9]+', line):
                enabledDisplays.append(line.split(" ")[0])

        displays = self.json if isinstance(self.json, list) else [self.json]

        # depending on the configuration, decide which display have to be switched off
        disableDisplays = enabledDisplays[:]
        for d in displays:
            for e in enabledDisplays:
                if e == d['display']:
                    disableDisplays.remove(e)

        self.logger_add('Mode: ' + str(self.name))

        # enable or change config of displays
        for d in displays:
            self.enableDisplay(d)

        # set primary display
        for d in displays:
            if 'primary' in d:
                self.setPrimaryDisplay(d['display'])

        # disable all not needed displays
        for d in disableDisplays:
            self.disableDisplay(d)

        self.logger_print()

def main(configPath : str):
    """Create a GUI and run the main loop

    :param configPath: path to the config json
    :type configPath: str

    """

    ############################################################################
    # create static GUI elements
    ############################################################################
    app = QApplication([])
    app.setApplicationName('dpswitch')
    window = QWidget()
    layout = QGridLayout()
    statusbar = QLabel()

    ############################################################################
    # load configuration from json file
    ############################################################################
    configJson = None
    try:
        with open(str(configPath)) as configFile:
            try:
                configJson = json.load(configFile)
                configFile.close()
            except Exception as e:
                statusbar.setStyleSheet('color: red')
                statusbar.setText('Error: Parsing JSON\n' + str(e))
    except Exception as e:
        statusbar.setStyleSheet('color: red')
        statusbar.setText('Error: Open JSON file\n' + str(e))

    ############################################################################
    # replace display names with ports
    ############################################################################
    if configJson is not None:
        for config_name in configJson["configs"]:
            configs = configJson["configs"][config_name] if isinstance(configJson["configs"][config_name], list) else [configJson["configs"][config_name]]
            for d in configs:
                d['display'] = configJson["displays"][d["display"]]["port"]
                if 'position' in d:
                        d['position'][1] = configJson["displays"][d['position'][1]]["port"]

    ############################################################################
    # create dynamic GUI elements for each mode
    ############################################################################
    if configJson is not None:
        buttonRow = 0
        buttons = []
        for mode in configJson["configs"]:
            buttons.append(DisplayModeButton(mode, configJson["configs"][mode], statusbar))
            layout.addWidget(buttons[-1] .button, 1, buttonRow)
            buttonRow += 1

    layout.addWidget(statusbar, 2, 0, -1, -1, Qt.AlignLeft)

    ############################################################################
    # run main loop
    ############################################################################
    window.setLayout(layout)
    window.show()
    app.exec_()

if __name__ == '__main__':
    configPath = '/etc/dpswitch/config.json' if len(sys.argv) < 2 else sys.argv[1]
    main(configPath)
