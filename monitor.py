import wx
import time

from threading import Thread

import matplotlib as mpl
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas

class Interface(wx.Frame):

	def __init__(self, parent, title, inputs):
		super(Interface, self).__init__(parent, title=title, size=(530, 60 + len(inputs) * 175))

		self.plot_panels = {}
		self.init_ui(inputs)
		self.Centre()
		self.Show()

		self.monitors = []
		for input in inputs:
			self.monitors.append(Monitor(input, self.plot_panels))

	def init_ui(self, inputs):
		panel = wx.Panel(self)
		sizer = wx.GridBagSizer(len(inputs) + 1, 2)

		for input in inputs:
			self.plot_panels[input] = PlotPanel(panel)

		# BLOCK 1
		# #######

		for n in range(len(inputs)):
			sizer.Add(self.plot_panels[inputs[n]], pos=(n, 0), span=(1, 2), flag=wx.ALL, border=5)

		# BLOCK 2
		# #######
		button_cancel = wx.Button(panel, label="Exit")
		button_cancel.Bind(wx.EVT_BUTTON, self.close_window)
		sizer.Add(button_cancel, pos=(len(inputs), 0), flag=wx.LEFT | wx.ALIGN_LEFT, border=5)

		button_start = wx.Button(panel, label="Start")
		button_start.Bind(wx.EVT_BUTTON, self.start)
		sizer.Add(button_start, pos=(len(inputs), 1), flag=wx.RIGHT | wx.ALIGN_RIGHT, border=5)

		panel.SetSizer(sizer)

	def close_window(self, event):
		self.Destroy()

	def start(self, event):
		for monitor in self.monitors:
			thread = Thread(target=monitor.start)
			thread.start()

class PlotPanel(wx.Panel):
	def __init__(self, parent, id=-1, dpi=None, **kwargs):
		wx.Panel.__init__(self, parent, id=id, **kwargs)
		self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
		self.canvas = Canvas(self, -1, self.figure)
		self.canvas.draw()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		self.SetSizer(sizer)
		sizer.SetMinSize((500, 100))
		self.sizer = sizer

	def draw(self, vals):
		self.figure.clear()
		axes = self.figure.gca()
		axes.plot(range(len(vals)), vals, "-o", color='r', label='r')
		self.canvas.draw()

class Monitor:
	def __init__(self, filename, plot_panels):
		self.filename = filename
		self.plot_panel = plot_panels[filename]
		self.vals = []

		self.content_file = open(self.filename, 'r')

	def start(self):
		line = None
		while 1:
			where = self.content_file.tell()
			last = line
			line = self.content_file.readline()

			try:
				light = int(last.split(' ')[2].split('\t')[10])
				self.vals.append(light)
			except:
				pass

			if not line:
				self.plot_panel.draw(self.vals[-10:])

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
