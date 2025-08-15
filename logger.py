import sys
import queue
import logging

from enum import Enum

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtWidgets import QTextEdit

log_queue = queue.Queue()
last_log_type = None

class LogTypes(Enum):
	INFO = 0
	STATUS = 1
	WARNING = 2
	ERROR = 3

DEBUG_MODE = not getattr(sys, 'frozen', False)

if DEBUG_MODE:
	logging.basicConfig(
		filename='app.log',
		level=logging.DEBUG,
		format='[%(asctime)s] %(levelname)s: %(message)s'
	)
else:
	logging.basicConfig(
		level=logging.INFO,
		format='[%(asctime)s] %(levelname)s: %(message)s'
	)

# Setup standard logging to file
def log_info(msg):
	logging.info(msg)
	log_queue.put((LogTypes.INFO, msg))
	
def log_status(msg):
	log_queue.put((LogTypes.STATUS, msg))

def log_warning(msg):
	logging.warning(msg)
	log_queue.put((LogTypes.WARNING, msg))

def log_error(msg):
	logging.error(msg)
	log_queue.put((LogTypes.ERROR, msg))

def clear_log(text_edit: QTextEdit):
	global last_log_type
	last_log_type = None
	text_edit.setText("")
	log_info("Logs cleared")

def process_log_queue(text_edit: QTextEdit):
	global last_log_type
	while not log_queue.empty():
		type, msg = log_queue.get()
		
		fmt = QTextCharFormat()
		if type == LogTypes.ERROR:
			fmt.setForeground(QColor("red"))
		elif type == LogTypes.WARNING:
			fmt.setForeground(QColor(200, 150, 0))
		else:
			fmt.setForeground(QColor(0, 200, 180))
		
		if last_log_type == None: 
			cursor = text_edit.textCursor()
			cursor.movePosition(cursor.MoveOperation.End)
			cursor.select(cursor.SelectionType.LineUnderCursor)
			lastStatus = cursor.selection().toPlainText()
			cursor.removeSelectedText()
			
			cursor.insertText(f"{type.name}: {msg}", fmt)
			text_edit.setTextCursor(cursor)
			text_edit.ensureCursorVisible()
		elif last_log_type == LogTypes.STATUS:
			cursor = text_edit.textCursor()
			cursor.movePosition(cursor.MoveOperation.End)
			cursor.select(cursor.SelectionType.LineUnderCursor)
			lastStatus = cursor.selection().toPlainText()
			cursor.removeSelectedText()
			
			cursor.insertText(f"{type.name}: {msg}", fmt)
			if type != LogTypes.STATUS and msg != "Stopping serial communication":
				fmt.setForeground(QColor("black"))
				cursor.insertText(f"\n{lastStatus}", fmt)
				type = LogTypes.STATUS
			
			text_edit.setTextCursor(cursor)
			text_edit.ensureCursorVisible()
		else:
			cursor = text_edit.textCursor()
			cursor.movePosition(cursor.MoveOperation.End)
			cursor.insertText(f"\n{type.name}: {msg}", fmt)
			text_edit.setTextCursor(cursor)
			text_edit.ensureCursorVisible()
		last_log_type = type
		

def setup_log_timer(text_edit, app):
	timer = QTimer()
	timer.timeout.connect(lambda: process_log_queue(text_edit))
	timer.start(100)  # Check logs every 100 ms
	return timer