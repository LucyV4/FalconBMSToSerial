import sys
import os
from typing import List
from datetime import datetime

from bms_serial import SerialSender, detect_serial_ports
from memreader import check_game_active, get_game_version
from logger import log_info, log_error, log_status, setup_log_timer, clear_log

from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QTabWidget, QWidget, QVBoxLayout, QGridLayout, QTextEdit, QLabel, QSlider
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QFont, QIcon

if getattr(sys, 'frozen', False):
	# Running as bundled by PyInstaller
	base_path = sys._MEIPASS
else:
	# Running from source
	base_path = os.path.abspath(".")

class QTMainTab(QWidget):
	def __init__(self, parent, init_freq: int = 250, init_ports: List[str] = []):
		super().__init__()
		self.parent: MainWindow = parent
  
		# Serial sender instance
		self.serial_active = False
		self.serial_frequency = init_freq
		self.serial_port_names = init_ports
		self.sender = SerialSender(self.serial_port_names)
  
		# Serial sender button
		self.serial_start_stop_button = QPushButton("Start serial")
		self.serial_start_stop_button.clicked.connect(self.start_stop_serial)
		self.serial_start_stop_button.setEnabled(False)
		self.serial_start_stop_label = QLabel("Game not running", alignment=Qt.AlignmentFlag.AlignCenter)
		self.serial_start_stop_label.setStyleSheet("QLabel { color: darkred; font-weight: normal; }")

		# Slider top label
		frequency_label = QLabel("Frequency (ms):", alignment=Qt.AlignmentFlag.AlignCenter)
		self.frequency_slider = QSlider(Qt.Orientation.Horizontal)
		self.frequency_slider.setRange(100, 1000)
		self.frequency_slider.setPageStep(50)
		self.frequency_slider.setSingleStep(50)
		self.frequency_slider.setTickInterval(50)
		self.frequency_slider.setValue(self.serial_frequency)
		self.frequency_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
		self.frequency_slider.valueChanged.connect(self.freq_slider_update)
		self.slider_cur_frequency_label = QLabel(f"{self.serial_frequency} ms", alignment=Qt.AlignmentFlag.AlignCenter)

		# Serial port list
		self.serial_port_list = QTextEdit()
		self.serial_port_list.setPlaceholderText("No serial ports have been added.\n\nAdd one by typing its port, i.e.\nCOM3\n\nIf you have multiple add an enter between each port, i.e.\nCOM3\nCOM4\n\nYou can also click the button below to detect and add all serial ports automatically.")
		self.serial_port_list.setText("\n".join(self.serial_port_names))
		self.serial_port_list.textChanged.connect(self.serial_port_list_update)
		self.serial_port_list.setMaximumWidth(200)
		self.serial_port_detect_button = QPushButton("Detect serial ports")
		self.serial_port_detect_button.clicked.connect(self.detect_serial_ports)

		self.active_label_timer = QTimer()
		self.active_label_timer.timeout.connect(self.update_label_time)
		self.active_label_timer.start(500)

		self.game_running = False
		self.game_active_timer = QTimer()
		self.game_active_timer.timeout.connect(self.update_game_active)
		self.game_active_timer.start(5000)
		self.update_game_active()

		# Grid layour and items
		layout = QGridLayout()
		layout.addWidget(frequency_label, 0, 0, 1, 2)
		layout.addWidget(self.frequency_slider, 1, 0, 2, 2)
		layout.addWidget(self.slider_cur_frequency_label, 3, 0, 1, 2)
		layout.addWidget(self.serial_start_stop_button, 4, 0, 2, 2)
		layout.addWidget(self.serial_start_stop_label, 5, 0, 1, 2)
		layout.addWidget(self.serial_port_list, 0, 2, 5, 1)
		layout.addWidget(self.serial_port_detect_button, 5, 2, 1, 1)

		layout.setColumnStretch(0, 2)
		layout.setColumnStretch(1, 1)

		self.setLayout(layout)

	def freq_slider_update(self, value):
		tick = self.frequency_slider.tickInterval()
		snapped = round(value / tick) * tick
  
		if value != snapped:
			self.frequency_slider.blockSignals(True)
			self.frequency_slider.setValue(snapped)
			self.frequency_slider.blockSignals(False)
		self.serial_frequency = snapped
		self.slider_cur_frequency_label.setText(f"{self.serial_frequency} ms")
		self.parent.settings.setValue("main/frequency", self.serial_frequency)

	def start_stop_serial(self):
		if self.serial_active:
			# Update state
			self.sender.stop()
			self.serial_active = False
			
   			# Update UI elements
			self.serial_start_stop_label.setText("Inactive")
			self.serial_start_stop_label.setStyleSheet("QLabel { color: darkred; font-weight: normal; }")
			self.serial_start_stop_button.setText("Start serial")
			self.frequency_slider.setEnabled(True)
			self.serial_port_list.setEnabled(True)
			self.serial_port_detect_button.setEnabled(True)
		else:
			# Update state
			self.sender = SerialSender(self.serial_port_names)
			self.sender.start(frequency=self.serial_frequency)
			self.serial_active = True
			self.active_start_time = datetime.now()

   			# Update UI elements
			self.serial_start_stop_label.setText("Active (0:00:00)")
			self.serial_start_stop_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
			self.serial_start_stop_button.setText("Stop serial")
			self.frequency_slider.setEnabled(False)
			self.serial_port_list.setEnabled(False)
			self.serial_port_detect_button.setEnabled(False)
   
	def serial_port_list_update(self):
		self.serial_port_names = [port_name.strip() for port_name in self.serial_port_list.toPlainText().split("\n") if port_name.strip()]
		self.parent.settings.setValue("main/ports", "\n".join(self.serial_port_names))
		if self.game_running:
			has_ports = len(self.serial_port_names) > 0
			self.serial_start_stop_button.setEnabled(has_ports)
			if not has_ports: self.serial_start_stop_label.setText("Inactive (no serial ports added)")
			else: self.serial_start_stop_label.setText("Inactive")

	def detect_serial_ports(self):
		log_info(f"Detecting serial ports")
		ports = detect_serial_ports()
		log_info(f"Found ports: {", ".join(ports)}")
		self.serial_port_list.setText("\n".join(ports))

	def update_label_time(self):
		if self.serial_active:
			elapsed = datetime.now() - self.active_start_time
			self.active_hours, remainder = divmod(elapsed.seconds, 3600)
			self.active_minutes, self.active_seconds = divmod(remainder, 60)
			timer_str = f"{self.active_hours:01d}:{self.active_minutes:02d}:{self.active_seconds:02d}"
			self.serial_start_stop_label.setText(f"Active ({timer_str})")
			log_status(f"Sending data ({timer_str})")

	def update_game_active(self):
		if check_game_active():
			if not self.game_running:
				game_version = get_game_version()
				log_info(f"Found connection with Falcon BMS {game_version}")
			self.game_running = True
			self.serial_start_stop_button.setEnabled(True)	
			self.serial_start_stop_label.setText("Inactive")
		else:
			if self.serial_active: self.start_stop_serial()
			self.serial_start_stop_button.setEnabled(False)
			self.serial_start_stop_label.setText("Inactive (game not running)")
			log_error("No connection with Falcon BMS. Is your game running?")
			self.game_running = False
		self.serial_port_list_update()

class QTLogTab(QWidget):
	def __init__(self):
		super().__init__()

		layout = QVBoxLayout()

		self.log_area = QTextEdit()
		self.log_area.setReadOnly(True)
		log_info("App opened")

		font = QFont("Courier New")
		font.setStyleHint(QFont.StyleHint.Monospace)
		font.setWeight(500)
		font.setPointSize(10)
		self.log_area.setFont(font)

		self.clear_log_button = QPushButton("Clear logs")
		self.clear_log_button.clicked.connect(self.clear_logs)

		layout.addWidget(self.log_area)
		layout.addWidget(self.clear_log_button)
		self.setLayout(layout)

		# Start timer to update logs safely
		self.log_timer = setup_log_timer(self.log_area, QApplication.instance())

	def clear_logs(self):
		clear_log(self.log_area)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.settings = QSettings("LucyV", "FalconBMSToSerial")

		init_freq = int(self.settings.value("main/frequency", 250))
		init_ports = str(self.settings.value("main/ports", "")).split("\n")

		tabs = QTabWidget()

		self.log_tab = QTLogTab()
		self.main_tab = QTMainTab(self, init_freq, init_ports)

		tabs.addTab(self.main_tab, "Controls")
		tabs.addTab(self.log_tab, "Logs")

		self.setCentralWidget(tabs)
		self.setWindowTitle("Falcon BMS to Serial")
		icon_path = os.path.join(base_path, "icon.ico")
		self.setWindowIcon(QIcon(icon_path))
		self.resize(800, 500)
		self.show()

try:
	app = QApplication(sys.argv)
	w = MainWindow()
	app.exec()
finally:
	if w.main_tab.serial_active: w.main_tab.sender.stop()