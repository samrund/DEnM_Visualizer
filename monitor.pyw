#!/usr/bin/env pythonw

# error output for windows
import sys
PATH_SEPARATOR = '/'
WINDOW_SIZE_ADJUST = 0
if sys.platform == 'win32':
	sys.stderr = open("errlog.txt", "w")
	PATH_SEPARATOR = '\\'
	WINDOW_SIZE_ADJUST = 35

import wx
import os
import time
import json

from time import strftime
from threading import Thread
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from wx.lib.masked import NumCtrl

import matplotlib as mpl
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas

do_restart = False

class Config():

	config_filename = 'config.ini'
	config_section = 'main'
	config_target_input = 'input_files'
	config_target_minutes = 'minutes'
	minutes_default = 120

	@staticmethod
	def get_config_path():
		config = SafeConfigParser()

		path, fl = os.path.split(os.path.realpath(__file__))
		full_path = os.path.join(path, Config.config_filename)

		if not os.path.isfile(full_path):
			open(full_path, 'a').close()
			print('WARNING: No config file found! New config file was created.')

		return (config, full_path)

	@staticmethod
	def load():
		config, full_path = Config.get_config_path()
		print('Loading config file: %s' % (full_path))

		obj = {
			'input_files': [],
			'minutes': Config.minutes_default
		}

		try:
			config.read(full_path)
			input_files_json = json.loads(config.get(Config.config_section, Config.config_target_input))
			for n in input_files_json:
				obj['input_files'].append(n[0] + PATH_SEPARATOR + n[1])
		except (NoOptionError, NoSectionError) as er:
			print(er)

		try:
			obj['minutes'] = json.loads(config.get(Config.config_section, Config.config_target_minutes))
		except (NoOptionError, NoSectionError) as er:
			print(er)

		return obj

	@staticmethod
	def save(input_files, minutes):
		config, full_path = Config.get_config_path()
		print('Saving config data: %s' % (full_path))

		config.add_section(Config.config_section)
		config.set(Config.config_section, Config.config_target_input, json.dumps(input_files))
		config.set(Config.config_section, Config.config_target_minutes, json.dumps(minutes))

		with open(full_path, 'w') as f:
			config.write(f)

class BrowseFileButton(wx.Button):

	def __init__(self, *args, **kw):
		super(BrowseFileButton, self).__init__(*args, **kw)

		self._defaultDirectory = PATH_SEPARATOR
		self.target = None
		self.Bind(wx.EVT_BUTTON, self.on_botton_clicked)

	def on_botton_clicked(self, e):
		dialog = wx.FileDialog(
			self, 'Open TXT file', '', '',
			'TXT files (*.txt)|*.txt', wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

		if dialog.ShowModal() == wx.ID_OK:
			if self.target:
				self.target(dialog.GetPath())

		dialog.Destroy()
		e.Skip()

class Settings(wx.Dialog):

	def __init__(self, parent):
		super(Settings, self).__init__(parent)

		self.parent = parent
		self.input_folder = None
		self.input_folder_value = ''
		self.input_list = None
		self.input_list_index = 0

		self.init_ui()
		self.SetSize((400, 330))
		self.SetTitle('Settings')

		self.load_config()

	def init_ui(self):

		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)

		# ## INPUT FOLDER
		sb = wx.StaticBox(panel, label='Input Files')
		sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

		hbox = wx.BoxSizer(wx.VERTICAL)

		# list
		self.input_list = wx.ListCtrl(panel, size=(-1, 130), style=wx.LC_REPORT | wx.BORDER_SUNKEN)
		self.input_list.InsertColumn(0, 'Folder', width=100)
		self.input_list.InsertColumn(1, 'Filename', width=200)

		hbox.Add(self.input_list, flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		btn_add = BrowseFileButton(panel, label='+', size=(30, -1))
		btn_rem = wx.Button(panel, label='-', size=(30, -1))
		btn_add.target = self.add_line
		btn_rem.Bind(wx.EVT_BUTTON, self.rem_line)
		hbox2.Add(btn_add, flag=wx.RIGHT, border=0)
		hbox2.Add(btn_rem, flag=wx.LEFT, border=0)

		hbox.Add(hbox2, flag=wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT, border=5)

		sbs.Add(hbox)
		vbox.Add(sbs, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

		# ## MINUTES
		min_sb = wx.StaticBox(panel, label='Measured time range')
		min_sbs = wx.StaticBoxSizer(min_sb, orient=wx.VERTICAL)
		min_sb.SetMinSize((340, -1))

		min_hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.measured_minutes = NumCtrl(panel, -1, value=0)
		self.measured_minutes.SetMin(0)
		min_hbox.Add(self.measured_minutes, flag=wx.LEFT, border=0)

		txt = wx.StaticText(panel, label="minutes")
		min_hbox.Add(txt, flag=wx.LEFT, border=10)

		min_sbs.Add(min_hbox)
		vbox.Add(min_sbs, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

		# ## BUTTON BOX
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		ok_button = wx.Button(panel, label='Ok')
		close_button = wx.Button(panel, label='Close')
		hbox2.Add(ok_button, proportion=1, flag=wx.RIGHT, border=0)
		hbox2.Add(close_button, proportion=1, flag=wx.LEFT, border=0)

		vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

		panel.SetSizer(vbox)

		ok_button.Bind(wx.EVT_BUTTON, self.on_save)
		close_button.Bind(wx.EVT_BUTTON, self.on_close)

	def add_line(self, path):
		folder = PATH_SEPARATOR.join(path.split(PATH_SEPARATOR)[:-1])
		filename = PATH_SEPARATOR.join(path.split(PATH_SEPARATOR)[-1:])
		self.input_list.InsertStringItem(self.input_list_index, folder)
		self.input_list.SetStringItem(self.input_list_index, 1, filename)
		self.input_list_index += 1

	def rem_line(self, event):
		selected_count = self.input_list.GetSelectedItemCount()
		selected_index = self.input_list.GetFocusedItem()
		if selected_count == 1 and selected_index != -1:
			self.input_list.Focus(0)
			self.input_list.DeleteItem(selected_index)
			self.input_list_index -= 1
		else:
			wx.MessageBox('', 'No selected file to delete', wx.ICON_EXCLAMATION)

	def load_config(self):
		loaded_data = Config.load()
		for n in loaded_data['input_files']:
			self.add_line(n)

		if loaded_data['minutes']:
			self.measured_minutes.SetValue(loaded_data['minutes'])

	def on_close(self, e):
		self.Close(True)

	def on_save(self, e):
		input_files = []
		count = self.input_list.GetItemCount()
		for row in range(count):
			folder = self.input_list.GetItem(itemId=row, col=0).GetText()
			filename = self.input_list.GetItem(itemId=row, col=1).GetText()
			input_files.append([folder, filename])

		measured_minutes = self.measured_minutes.GetValue()

		Config.save(input_files=input_files, minutes=measured_minutes)
		self.Close(True)
		self.parent.restart()

class Interface(wx.Frame):

	def __init__(self, parent, title):
		super(Interface, self).__init__(parent, title=title, size=(570 + WINDOW_SIZE_ADJUST, 100 + WINDOW_SIZE_ADJUST))

		self.header = None
		self.plot_panels = {}
		self.current_input = 0
		self.monitors = []

		self.attributes = {
			'Light': {
				'col': 10,
				'unit': 'Lux'
			},
			'Temperature': {
				'col': 15,
				'unit': 'Celsius',
				'function': 'x * 0.1'
			},
			'Humidity': {
				'col': 20,
				'unit': 'R.H.'
			}
		}

		w, h = self.GetClientSize()
		self.SetSize((w, h + len(self.attributes) * (199)))

		self.load_config()

		if self.input_files:
			self.init_ui(self.input_files[self.current_input])
		else:
			self.init_ui(None)

		self.Centre()
		self.Show()
		self.load_input(self.current_input)

	def load_config(self):
		self.input_files = []
		loaded_data = Config.load()

		for n in loaded_data['input_files']:
			self.input_files.append(n)

		self.minutes = loaded_data['minutes']

	def load_input(self, target_input):
		self.monitors_terminate()

		self.monitors = []
		if self.input_files:
			# updates the filename in GUI and repositions elements
			self.current_filename.SetLabel(self.get_formatted_filename_from_path(self.input_files[target_input]))
			self.panel.Layout()

			self.monitors.append(Monitor(self.update_title, self.input_files[target_input], self.plot_panels, self.attributes, self.minutes))
			self.monitors_start()

	def get_input_files(self, path):
		files = []
		for file in sorted(os.listdir(path)):
			if file.endswith('.txt'):
				files.append(path + PATH_SEPARATOR + file)

		return files

	def get_formatted_filename_from_path(self, path):
		if path:
			appendix = ' (' + str(self.current_input + 1) + '/' + str(len(self.input_files)) + ')'
			return path.split(PATH_SEPARATOR)[-1:][0] + appendix

		return '<Error>'

	def init_ui(self, input):
		self.panel = wx.Panel(self)
		sizer = wx.GridBagSizer(len(self.attributes) + 1, 4)

		for attribute in self.attributes:
			self.plot_panels[attribute] = PlotPanel(self.panel)

		# BLOCK 0
		# #######

		self.header = None
		if not input:
			self.header = wx.StaticText(self.panel, wx.ID_ANY, label='No input files found. Please change the input folder in Settings.')
			sizer.Add(self.header, pos=(0, 0), span=(1, 3), flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
		else:
			self.header = wx.StaticText(self.panel, wx.ID_ANY, label='Loading data...')
			sizer.Add(self.header, pos=(0, 0), span=(1, 3), flag=wx.LEFT | wx.TOP, border=5)

		self.current_filename = wx.StaticText(self.panel, wx.ID_ANY, label='Loading data...')
		sizer.Add(self.current_filename, pos=(0, 3), span=(1, 1), flag=wx.LEFT | wx.TOP | wx.RIGHT | wx.ALIGN_RIGHT, border=5)

		# BLOCK 1
		# #######

		position = 0
		for attribute in self.attributes:
			sizer.Add(self.plot_panels[attribute], pos=(1 + position, 0), span=(1, 4), flag=wx.ALL, border=5)
			position += 1

		# BLOCK 2
		# #######
		button_cancel = wx.Button(self.panel, label='Exit')
		button_cancel.Bind(wx.EVT_BUTTON, self.close_window)
		sizer.Add(button_cancel, pos=(1 + len(self.attributes), 0), flag=wx.LEFT | wx.ALIGN_LEFT, border=5)

		button_start = wx.Button(self.panel, label='<')
		button_start.Bind(wx.EVT_BUTTON, self.change_input_backward)
		sizer.Add(button_start, pos=(1 + len(self.attributes), 1), flag=wx.LEFT | wx.ALIGN_RIGHT, border=100)

		button_start = wx.Button(self.panel, label='>')
		button_start.Bind(wx.EVT_BUTTON, self.change_input_forward)
		sizer.Add(button_start, pos=(1 + len(self.attributes), 2), flag=wx.ALIGN_LEFT, border=5)

		button_start = wx.Button(self.panel, label='Settings')
		button_start.Bind(wx.EVT_BUTTON, self.show_settings)
		sizer.Add(button_start, pos=(1 + len(self.attributes), 3), flag=wx.RIGHT | wx.ALIGN_RIGHT, border=5)

		self.panel.SetSizer(sizer)

	def change_input_backward(self, event):
		self.current_input -= 1
		if self.current_input < 0:
			self.current_input = len(self.input_files) - 1

		self.load_input(self.current_input)

	def change_input_forward(self, event):
		self.current_input += 1
		if self.current_input >= len(self.input_files):
			self.current_input = 0

		self.load_input(self.current_input)

	def show_settings(self, event):
		modal = Settings(self)
		modal.ShowModal()
		modal.Destroy()

	def update_title(self, text=None):
		if text:
			self.header.SetLabel(str(text))
		else:
			actual_time = strftime("%H:%M:%S")
			self.header.SetLabel('Last time of recording: ' + str(actual_time))

	def close_window(self, event):
		self.Destroy()

	def restart(self):
		global do_restart

		print('Restarting...\n')

		do_restart = True
		self.close_window(None)

	def monitors_terminate(self):
		for monitor in self.monitors:
			monitor.terminate()

	def monitors_start(self):
		for monitor in self.monitors:
			thread = Thread(target=monitor.run)
			thread.daemon = True
			thread.start()


class PlotPanel(wx.Panel):

	def __init__(self, parent, id=-1, dpi=80, **kwargs):
		wx.Panel.__init__(self, parent, id=id, **kwargs)
		self.figure = mpl.figure.Figure(dpi=dpi, figsize=(7, 2.3))
		self.figure.subplots_adjust(top=0.87)
		self.figure.subplots_adjust(bottom=0.2)
		self.figure.subplots_adjust(left=0.1)
		self.figure.subplots_adjust(right=0.92)
		self.canvas = Canvas(self, -1, self.figure)
		self.canvas.draw()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		self.SetSizer(sizer)
		self.sizer = sizer

	def draw(self, vals, label='', label_x='', label_y=''):
		self.figure.clear()
		axes = self.figure.gca()
		axes.invert_xaxis()
		axes.set_xlabel(label_x)
		axes.set_ylabel(label_y)
		axes.set_title(label)
		axes.set_xlim([len(vals) - 1, 0])
		axes.set_ylim(self.get_ylim(vals))
		plot_style = self.get_plot_style(len(vals))
		axes.text(1.05, 0.5, vals[-1:][0], horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize=15)
		axes.plot(list(reversed(range(len(vals)))), vals, plot_style, color='r', label='r')
		self.canvas.draw()

	def get_plot_style(self, length):
		if length > 240:
			return 'b-'
		else:
			return 'o-'

	def get_ylim(self, vals):
		lo = min(vals) - 10
		hi = max(vals) + 10
		return [lo, hi]

class Monitor:

	def __init__(self, update_title, filename, plot_panels, attributes, minutes):
		self.filename = filename
		self.plot_panel = plot_panels
		self.vals = {}
		self.update_title = update_title
		self.alive = True
		self.delay_in_seconds = 1
		self.minutes = minutes

		self.attributes = attributes
		for attribute in attributes:
			self.vals[attribute] = []

		self.content_file = open(self.filename, 'r')

	def main(self):
		line = None
		reached_end = False
		while self.alive:
			where = self.content_file.tell()
			last = line
			line = self.content_file.readline()

			try:
				# get all values and add them to the list
				for attribute in self.attributes:
					val = int(last.split(' ')[2].split('\t')[self.attributes[attribute]['col']])
					# apply lambda function if defined
					if 'function' in self.attributes[attribute]:
						fun = lambda x: eval(self.attributes[attribute]['function'])
						val = fun(val)

					self.vals[attribute].append(val)

				if reached_end:
					self.update_title()

				if not line:
					if not reached_end:
						reached_end = True
						self.update_title()

					# Check for erroneous input
					valid = True
					for attribute in self.attributes:
						if not self.vals[attribute]:
							valid = False
							break

					if not valid:
						self.update_title('Problem with reading some content!')
						print('Thread: breaking!')
						break

					# redraw the plot with the last X values
					for attribute in self.attributes:
						self.plot_panel[attribute].draw(self.vals[attribute][-self.minutes:], attribute, 'minutes', self.attributes[attribute]['unit'])

					time.sleep(self.delay_in_seconds)
					self.content_file.seek(where)
			except:
				pass

		print('Thread: Terminated')

	def run(self):
		self.alive = True
		self.main()

	def terminate(self):
		self.alive = False

def main():
	global do_restart
	app = wx.App()

	while True:
		Interface(None, title='Monitors')
		app.MainLoop()

		if not do_restart:
			break

		do_restart = False


if __name__ == "__main__":
	main()
