import wx
import os
import time

from time import strftime
from threading import Thread
from ConfigParser import SafeConfigParser

import matplotlib as mpl
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas


do_restart = False

class BrowseFolderButton(wx.Button):

	def __init__(self, *args, **kw):
		super(BrowseFolderButton, self).__init__(*args, **kw)

		self._defaultDirectory = '/'
		self.target = None
		self.Bind(wx.EVT_BUTTON, self.on_botton_clicked)

	def on_botton_clicked(self, e):
		dialog = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

		if dialog.ShowModal() == wx.ID_OK:
			if self.target:
				self.target.SetValue(dialog.GetPath())

		dialog.Destroy()
		e.Skip()

class Settings(wx.Dialog):

	def __init__(self, parent):
		super(Settings, self).__init__(parent)

		self.parent = parent
		self.input_folder = None
		self.input_folder_value = ''

		self.load_config()

		self.init_ui()
		self.SetSize((400, 140))
		self.SetTitle("Settings")

	def init_ui(self):

		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)

		# INPUT FOLDER
		sb = wx.StaticBox(panel, label='Input folder')
		sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.input_folder = wx.TextCtrl(panel, value=self.input_folder_value, size=(250, -1))
		hbox.Add(self.input_folder, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=5)

		browse_button = BrowseFolderButton(panel, label="Browse...")
		browse_button.target = self.input_folder
		hbox.Add(browse_button, flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)

		sbs.Add(hbox)
		vbox.Add(sbs, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

		# # LISTBOX
		# sb = wx.StaticBox(panel, label='Columns')
		# sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

		# self.list_box = wx.ListBox(
		# 	choices=[],
		# 	name='listBox',
		# 	parent=panel,
		# 	pos=wx.Point(8, 48),
		# 	size=wx.Size(184, 256),
		# 	style=0)

		# self.list_box.Append("Andreas")
		# self.list_box.Append("Erich")

		# sbs.Add(self.list_box)

		# vbox.Add(sbs, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

		# # BUTTON BOX
		# hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		# add_button = wx.Button(panel, label='Add')
		# remove_button = wx.Button(panel, label='Remove')
		# hbox2.Add(add_button, proportion=1, flag=wx.RIGHT, border=5)
		# hbox2.Add(remove_button, proportion=1, flag=wx.LEFT, border=5)

		# vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

		# BUTTON BOX
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		ok_button = wx.Button(panel, label='Ok')
		close_button = wx.Button(panel, label='Close')
		hbox2.Add(ok_button, proportion=1, flag=wx.RIGHT, border=0)
		hbox2.Add(close_button, proportion=1, flag=wx.LEFT, border=0)

		vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

		panel.SetSizer(vbox)

		ok_button.Bind(wx.EVT_BUTTON, self.on_save)
		close_button.Bind(wx.EVT_BUTTON, self.on_close)

	def load_config(self):
		print('Loading config data...')
		config = SafeConfigParser()
		config.read('config.ini')

		self.input_folder_value = config.get('main', 'input_folder')

	def on_close(self, e):
		self.Close(True)

	def on_save(self, e):
		print('Saving config data...')
		config = SafeConfigParser()
		config.add_section('main')
		config.set('main', 'input_folder', self.input_folder.GetValue())

		with open('config.ini', 'w') as f:
			config.write(f)
		self.Close(True)
		self.parent.restart()

class Interface(wx.Frame):

	def __init__(self, parent, title):
		super(Interface, self).__init__(parent, title=title, size=(570, 100))

		self.header = None
		self.input_folder_value = ''
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
				'unit': 'Celsius X 10'
			},
			'Humidity': {
				'col': 20,
				'unit': 'R.H.'
			}
		}

		w, h = self.GetClientSize()
		self.SetSize((w, h + len(self.attributes) * (199)))

		self.load_config()

		self.input_files = []
		if self.input_folder_value is not '':
			self.input_files = self.get_input_files(self.input_folder_value)
			print self.input_files
		else:
			print 'ERROR: no input folder defined'

		if self.input_files:
			self.init_ui(self.input_files[self.current_input])
		else:
			self.init_ui(None)

		self.Centre()
		self.Show()
		self.load_input(self.current_input)

	def load_input(self, target_input):
		self.monitors_terminate()

		self.monitors = []
		if self.input_files:
			# updates the filename in GUI and repositions elements
			self.current_filename.SetLabel(self.get_formatted_filename_from_path(self.input_files[target_input]))
			self.panel.Layout()

			self.monitors.append(Monitor(self.update_title, self.input_files[target_input], self.plot_panels, self.attributes))
			self.monitors_start()

	def load_config(self):
		print('Loading config data...')
		config = SafeConfigParser()
		config.read('config.ini')

		self.input_folder_value = config.get('main', 'input_folder')

	def get_input_files(self, path):
		files = []
		for file in sorted(os.listdir(path)):
			if file.endswith(".txt"):
				files.append(path + "/" + file)

		return files

	def get_formatted_filename_from_path(self, path):
		if path:
			appendix = ' (' + str(self.current_input + 1) + '/' + str(len(self.input_files)) + ')'
			return path.split('/')[-1:][0] + appendix

		return '<Error>'

	def init_ui(self, input):
		self.panel = wx.Panel(self)
		sizer = wx.GridBagSizer(len(self.attributes) + 1, 4)

		# for input in inputs:
		# 	self.plot_panels[input] = PlotPanel(panel)

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
		button_cancel = wx.Button(self.panel, label="Exit")
		button_cancel.Bind(wx.EVT_BUTTON, self.close_window)
		sizer.Add(button_cancel, pos=(1 + len(self.attributes), 0), flag=wx.LEFT | wx.ALIGN_LEFT, border=5)

		button_start = wx.Button(self.panel, label="<")
		button_start.Bind(wx.EVT_BUTTON, self.change_input_backward)
		sizer.Add(button_start, pos=(1 + len(self.attributes), 1), flag=wx.LEFT | wx.ALIGN_RIGHT, border=100)

		button_start = wx.Button(self.panel, label=">")
		button_start.Bind(wx.EVT_BUTTON, self.change_input_forward)
		sizer.Add(button_start, pos=(1 + len(self.attributes), 2), flag=wx.ALIGN_LEFT, border=5)

		button_start = wx.Button(self.panel, label="Settings")
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
			print('Last time of recording: ' + str(actual_time))
			self.header.SetLabel('Last time of recording: ' + str(actual_time))

	def close_window(self, event):
		self.Destroy()

	def restart(self):
		global do_restart

		print '\nRestarting...\n\n'

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
		# sizer.SetMinSize((500, 130))
		self.sizer = sizer

	def draw(self, vals, label='', label_x='', label_y=''):
		self.figure.clear()
		axes = self.figure.gca()
		axes.invert_xaxis()
		axes.set_xlabel(label_x)
		axes.set_ylabel(label_y)
		axes.set_title(label)
		axes.text(1.05, 0.5, vals[-1:][0], horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize=15)
		axes.plot(list(reversed(range(len(vals)))), vals, "-o", color='r', label='r')
		self.canvas.draw()

class Monitor:
	def __init__(self, update_title, filename, plot_panels, attributes):
		self.filename = filename
		self.plot_panel = plot_panels
		self.vals = {}
		self.update_title = update_title
		self.alive = True
		self.delay_in_seconds = 1

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
					self.vals[attribute].append(val)

				if reached_end:
					self.update_title()
			except:
				pass

			if not line:
				if not reached_end:
					reached_end = True
					self.update_title()

				# Check for erroneous input
				#
				valid = True
				for attribute in self.attributes:
					if not self.vals[attribute]:
						valid = False
						break

				if not valid:
					self.update_title("Problem with reading some content!")
					print "Thread: breaking!"
					break

				# redraw the plot with the last X values
				for attribute in self.attributes:
					self.plot_panel[attribute].draw(self.vals[attribute][-120:], attribute, "minutes", self.attributes[attribute]['unit'])

				time.sleep(self.delay_in_seconds)
				self.content_file.seek(where)
			else:
				pass
				# print line

		print "Thread: Terminated"

	def run(self):
		self.alive = True
		self.main()

	def terminate(self):
		self.alive = False

def main():
	global do_restart
	app = wx.App()

	while True:
		Interface(None, title='Environment Monitor')
		app.MainLoop()

		if not do_restart:
			break

		do_restart = False


if __name__ == "__main__":
	main()
