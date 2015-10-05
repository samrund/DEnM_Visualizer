import wx
import time

from time import strftime
from threading import Thread
from ConfigParser import SafeConfigParser

import matplotlib as mpl
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas

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

	def __init__(self, *args, **kw):
		super(Settings, self).__init__(*args, **kw)

		self.target_folder = None
		self.target_folder_value = ''

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
		self.target_folder = wx.TextCtrl(panel, value=self.target_folder_value, size=(250, -1))
		hbox.Add(self.target_folder, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=5)

		browse_button = BrowseFolderButton(panel, label="Browse...")
		browse_button.target = self.target_folder
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

		self.target_folder_value = config.get('main', 'input_folder')

	def on_close(self, e):
		self.Close(True)

	def on_save(self, e):
		print('Saving config data...')
		config = SafeConfigParser()
		config.add_section('main')
		config.set('main', 'input_folder', self.target_folder.GetValue())

		with open('config.ini', 'w') as f:
			config.write(f)
		self.Close(True)

class Interface(wx.Frame):

	def __init__(self, parent, title, inputs):
		super(Interface, self).__init__(parent, title=title, size=(570, 65 + len(inputs) * 170 + 25))

		self.header = None

		self.plot_panels = {}
		self.init_ui(inputs)
		self.Centre()
		self.Show()

		self.monitors = []
		for input in inputs:
			self.monitors.append(Monitor(self.update_title, input, self.plot_panels))

		self.start()

	def init_ui(self, inputs):
		panel = wx.Panel(self)
		sizer = wx.GridBagSizer(len(inputs) + 1, 3)

		for input in inputs:
			self.plot_panels[input] = PlotPanel(panel)

		# BLOCK 0
		# #######

		self.header = wx.StaticText(panel, wx.ID_ANY, label='Loading data...')
		sizer.Add(self.header, pos=(0, 0), span=(1, 2), flag=wx.LEFT | wx.TOP, border=5)

		# BLOCK 1
		# #######

		for n in range(len(inputs)):
			sizer.Add(self.plot_panels[inputs[n]], pos=(1 + n, 0), span=(1, 2), flag=wx.ALL, border=5)

		# BLOCK 2
		# #######
		button_cancel = wx.Button(panel, label="Exit")
		button_cancel.Bind(wx.EVT_BUTTON, self.close_window)
		sizer.Add(button_cancel, pos=(1 + len(inputs), 0), flag=wx.LEFT | wx.ALIGN_LEFT, border=5)

		button_start = wx.Button(panel, label="Settings")
		button_start.Bind(wx.EVT_BUTTON, self.show_settings)
		sizer.Add(button_start, pos=(1 + len(inputs), 1), flag=wx.RIGHT | wx.ALIGN_RIGHT, border=5)

		panel.SetSizer(sizer)

	def show_settings(self, event):
		modal = Settings(None)
		modal.ShowModal()
		modal.Destroy()

	def update_title(self):
		actual_time = strftime("%H:%M:%S")
		print('Last time of recording: ' + str(actual_time))
		self.header.SetLabel('Last time of recording: ' + str(actual_time))

	def close_window(self, event):
		self.Destroy()

	def start(self):
		for monitor in self.monitors:
			thread = Thread(target=monitor.start)
			thread.daemon = True
			thread.start()

class PlotPanel(wx.Panel):
	def __init__(self, parent, id=-1, dpi=80, **kwargs):
		wx.Panel.__init__(self, parent, id=id, **kwargs)
		self.figure = mpl.figure.Figure(dpi=dpi, figsize=(7, 2))
		self.figure.subplots_adjust(bottom=0.25)
		self.figure.subplots_adjust(left=0.1)
		self.canvas = Canvas(self, -1, self.figure)
		self.canvas.draw()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		self.SetSizer(sizer)
		# sizer.SetMinSize((500, 130))
		self.sizer = sizer

	def draw(self, vals, label_x='', label_y=''):
		self.figure.clear()
		axes = self.figure.gca()
		axes.invert_xaxis()
		axes.set_xlabel(label_x)
		axes.set_ylabel(label_y)
		axes.text(1.05, 0.5, vals[-1:][0], horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize=15)
		axes.plot(list(reversed(range(len(vals)))), vals, "-o", color='r', label='r')
		self.canvas.draw()

class Monitor:
	def __init__(self, update_title, filename, plot_panels):
		self.filename = filename
		self.plot_panel = plot_panels[filename]
		self.vals = []
		self.update_title = update_title

		self.content_file = open(self.filename, 'r')

	def start(self):
		line = None
		reached_end = False
		while 1:
			where = self.content_file.tell()
			last = line
			line = self.content_file.readline()

			try:
				light = int(last.split(' ')[2].split('\t')[10])
				self.vals.append(light)

				if reached_end:
					self.update_title()
			except:
				pass

			if not line:
				if not reached_end:
					reached_end = True
					self.update_title()

				self.plot_panel.draw(self.vals[-120:], "minutes", "light")

				time.sleep(1)
				self.content_file.seek(where)
			else:
				pass
				# print line

def main():
	app = wx.App()
	inputs = ['Monitor10.txt', 'Monitor11.txt', 'Monitor14.txt']
	Interface(None, title='Environment Monitor', inputs=inputs)
	app.MainLoop()

if __name__ == "__main__":
	main()
