import wx
import time

from time import strftime
from threading import Thread

import matplotlib as mpl
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas

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

		# button_start = wx.Button(panel, label="Start")
		# button_start.Bind(wx.EVT_BUTTON, self.start)
		# sizer.Add(button_start, pos=(1 + len(inputs), 1), flag=wx.RIGHT | wx.ALIGN_RIGHT, border=5)

		panel.SetSizer(sizer)

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
		axes.plot(range(len(vals)), vals, "-o", color='r', label='r')
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
