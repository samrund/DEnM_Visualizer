#!/usr/bin/env python3

# error output for windows
import sys
PATH_SEPARATOR = '/'
if sys.platform == 'win32':
    sys.stderr = open("errlog.txt", "w")


import os
import json
import time
import matplotlib as mpl
mpl.use('TkAgg')

from time import strftime
from threading import Thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# import with python 2 compatibility
try:
    from configparser import SafeConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.filedialog as filedialog
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog

do_restart = False


class SettingsDialog(tk.Toplevel):

    def __init__(self, parent, title=None):

        tk.Toplevel.__init__(self, parent.master)
        self.transient(parent.master)

        if title:
            self.title(title)

        self.parent = parent
        self.result = None
        self.measured_minutes = None

        body = tk.Frame(self)
        self.initial_focus = self.create_widgets(body)
        self.load_config()
        body.pack(padx=10, pady=10)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.master.winfo_rootx() + 50,
                                  parent.master.winfo_rooty() + 50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def create_widgets(self, root):
        '''
        create dialog body
        '''

        self.pathtree = ttk.Treeview(root)
        self.pathtree["columns"] = ("folder", "filename")
        self.pathtree['show'] = 'headings'  # hide first column
        self.pathtree.heading('#0', text='Directory Structure', anchor=tk.W)
        self.pathtree.column("folder", stretch=True, width=300)
        self.pathtree.column("filename")
        self.pathtree.heading("folder", text="Folder")
        self.pathtree.heading("filename", text="Filename")
        self.pathtree.grid(row=0, column=0)

        def browse_file():
            file_path = filedialog.askopenfilename()
            if file_path:
                self.add_line(file_path)

        def remove_file():
            selection = self.pathtree.selection()
            if len(selection):
                selected_item = selection[0]
                self.pathtree.delete(selected_item)

        button_frame = tk.Frame(root)
        button_del = tk.Button(button_frame, text="+", command=browse_file, width=5)
        button_del.pack(side=tk.LEFT)
        button_del = tk.Button(button_frame, text="-", command=remove_file, width=5)
        button_del.pack(side=tk.LEFT)
        button_frame.grid(row=1, column=0, pady=5, sticky=tk.W)

        mtime_frame = tk.Frame(root)
        front_label = tk.Label(mtime_frame, text="Measured time range is ")
        label = tk.Label(mtime_frame, text="minutes.")
        front_label.pack(side=tk.LEFT, pady=10, padx=5)
        label.pack(side=tk.RIGHT, pady=10, padx=5)
        self.measured_minutes = tk.Entry(mtime_frame, relief=tk.RIDGE)
        self.measured_minutes.pack(side=tk.RIGHT, pady=10, padx=2)
        mtime_frame.grid(row=2, column=0, pady=10, sticky=tk.W)

    def buttonbox(self):
        '''
        add standard button box
        '''

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack(pady=5)

    def load_config(self):
        loaded_data = Config.load()
        for n in loaded_data['input_files']:
            self.add_line(n)

        if self.measured_minutes and 'minutes' in loaded_data and loaded_data['minutes']:
            self.measured_minutes.delete(0, tk.END)
            self.measured_minutes.insert(0, loaded_data['minutes'])

    def add_line(self, path):
        folder = PATH_SEPARATOR.join(path.split(PATH_SEPARATOR)[:-1])
        filename = PATH_SEPARATOR.join(path.split(PATH_SEPARATOR)[-1:])

        self.pathtree.insert("", 0, values=(folder, filename))

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()
        self.save()
        self.parent.restart()

    def save(self):
        input_files = []
        children_ids = self.pathtree.get_children()
        for child_id in children_ids:
            values = self.pathtree.item(child_id)['values']
            input_files.append(values)

        measured_minutes = int(self.measured_minutes.get())

        Config.save(input_files=input_files, minutes=measured_minutes)

    def cancel(self, event=None):
        '''
        put focus back to the parent window and destroy this dialog
        '''
        self.parent.master.focus_set()
        self.destroy()


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
        print(('Loading config file: %s' % (full_path)))

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
        print(('Saving config data: %s' % (full_path)))

        config.add_section(Config.config_section)
        config.set(Config.config_section, Config.config_target_input, json.dumps(input_files))
        config.set(Config.config_section, Config.config_target_minutes, json.dumps(minutes))

        with open(full_path, 'w') as f:
            config.write(f)


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.header = None
        self.plot_panels = {}
        self.current_input = 0
        self.status_text = tk.StringVar()
        self.filename_text = tk.StringVar()
        self.monitors = []

        self.attributes = {
            'Light': {
                'order': 1,
                'col': 10,
                'unit': 'Lux'
            },
            'Humidity': {
                'order': 2,
                'col': 20,
                'unit': 'R.H.'
            },
            'Temperature': {
                'order': 3,
                'col': 15,
                'unit': 'Celsius',
                'function': 'x * 0.1'
            }
        }

        self.load_config()
        self.setup_window(master)

        if self.input_files:
            self.create_widgets(master, self.input_files[self.current_input])
            self.load_input(self.current_input)
        else:
            self.create_widgets(master, None)

    def load_config(self):
        self.input_files = []
        loaded_data = Config.load()

        for n in sorted(loaded_data['input_files']):
            self.input_files.append(n)

        self.minutes = loaded_data['minutes']

    def load_input(self, target_input):
        def get_formatted_filename_from_path(path):
            if path:
                appendix = ' (' + str(self.current_input + 1) + '/' + str(len(self.input_files)) + ')'
                return path.split(PATH_SEPARATOR)[-1:][0] + appendix
            return '<Error>'

        self.monitors_terminate()

        self.monitors = []
        if self.input_files:
            self.set_filename(get_formatted_filename_from_path(self.input_files[target_input]))
            self.monitors.append(Monitor(self.set_status, self.input_files[target_input], self.plot_panels, self.attributes, self.minutes))
            self.monitors_start()

    def setup_window(self, root, sizex=560, sizey=615):
        def center(toplevel):
            toplevel.update_idletasks()
            w = toplevel.winfo_screenwidth()
            h = toplevel.winfo_screenheight()
            size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
            x = w / 2 - size[0] / 2
            y = h / 2 - size[1] / 2
            toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

        root.wm_title("DEnM_Visualizer")
        root.resizable(width=False, height=False)
        root.geometry('{}x{}'.format(sizex, sizey))
        center(root)

    def set_status(self, text=None):
        if text:
            text = text[:55]
            self.status_text.set(text)
        else:
            actual_time = strftime("%H:%M:%S")
            self.status_text.set('Last time of recording: ' + str(actual_time))

    def set_filename(self, text):
        self.filename_text.set(text)

    def create_widgets(self, root, filepath):

        # BLOCK 0
        # #######

        self.status_field = tk.Message(root, textvariable=self.status_text, width=370, padx=15)
        self.status_field.grid(row=0, column=0, sticky=tk.W, columnspan=1)

        self.filename_field = tk.Message(root, textvariable=self.filename_text, width=190, padx=15)
        self.filename_field.grid(row=0, column=1, sticky=tk.E, columnspan=1)

        if not filepath:
            self.set_status('No input files found. Please add files in Settings.')
        else:
            self.set_status('Loading data...')

        self.set_filename('No file')

        # BLOCK 1
        # #######

        for idx, attribute in enumerate(sorted(self.attributes, key=lambda x: int(self.attributes[x]['order']))):
            self.plot_panels[attribute] = Plotter(root, 1 + idx)

        # BLOCK 2
        # #######

        button_frame = tk.Frame(root, width=root.winfo_width(), height=35)

        buttons = []
        buttons.append(tk.Button(button_frame, text="Exit", command=self.quit, width=7))
        buttons.append(tk.Button(button_frame, text="<", command=self.change_input_backward, width=7))
        buttons.append(tk.Button(button_frame, text=">", command=self.change_input_forward, width=7))
        buttons.append(tk.Button(button_frame, text="Settings", command=self.show_settings, width=7))

        buttons[0].grid(row=0, column=0, sticky=tk.W, pady=3, padx=5)
        buttons[1].grid(row=0, column=1, sticky=tk.E, pady=3)
        buttons[2].grid(row=0, column=2, sticky=tk.W, pady=3)
        buttons[3].grid(row=0, column=3, sticky=tk.E, pady=3, padx=5)

        button_frame.grid_propagate(False)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(3, weight=1)
        button_frame.grid(row=4, column=0, columnspan=2)

    def change_input_backward(self):
        self.current_input -= 1
        if self.current_input < 0:
            self.current_input = len(self.input_files) - 1

        self.load_input(self.current_input)

    def change_input_forward(self):
        self.current_input += 1
        if self.current_input >= len(self.input_files):
            self.current_input = 0

        self.load_input(self.current_input)

    def show_settings(self):
        SettingsDialog(self, title="Settings")

    def quit(self):
        self.monitors_terminate()
        self.master.destroy()

    def restart(self):
        global do_restart

        print('Restarting...\n')

        do_restart = True
        self.quit()

    def monitors_terminate(self):
        for monitor in self.monitors:
            monitor.terminate()

    def monitors_start(self):
        for monitor in self.monitors:
            thread = Thread(target=monitor.run)
            thread.daemon = True
            thread.start()


class Plotter():

    def __init__(self, root, row, dpi=80):
        self.fig = mpl.figure.Figure(dpi=dpi, figsize=(7, 2.3))
        self.fig.subplots_adjust(top=0.87)
        self.fig.subplots_adjust(bottom=0.2)
        self.fig.subplots_adjust(left=0.1)
        self.fig.subplots_adjust(right=0.92)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas._tkcanvas.grid(row=row, column=0, columnspan=4, pady=1)

    def draw(self, vals, label='', label_x='', label_y=''):
        self.fig.clear()
        axes = self.fig.gca()
        axes.invert_xaxis()
        axes.set_xlabel(label_x)
        axes.set_ylabel(label_y)
        axes.set_title(label)
        axes.set_xlim([len(vals) - 1, 0])
        axes.set_ylim(self.get_ylim(vals))
        plot_style = self.get_plot_style(len(vals))
        if len(vals):
            axes.text(1.05, 0.5, vals[-1:][0], horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize=15)
        axes.plot(list(reversed(list(range(len(vals))))), vals, plot_style, color='r', label='r')
        self.canvas.draw()

    def get_plot_style(self, length):
        if length > 240:
            return 'b-'
        else:
            return 'o-'

    def get_ylim(self, vals):
        if not len(vals):
            return [-1, 1]

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

        try:
            self.content_file = open(self.filename, 'r')
        except Exception as ex:
            self.update_title('Error while opening file!')
            print("Error while opening file: {0}".format(ex))
            self.alive = False

    def main(self):
        reached_end = False
        while self.alive:
            where = self.content_file.tell()

            try:
                line = self.content_file.readline()
            except Exception as ex:
                self.update_title('Error while reading file!')
                print("Error while reading file: {0}".format(ex))
                self.alive = False

            try:
                if line:
                    # get all values and add them to the list
                    for attribute in self.attributes:
                        val = int(line.split(' ')[2].split('\t')[self.attributes[attribute]['col']])
                        # apply lambda function if defined
                        if 'function' in self.attributes[attribute]:
                            fun = lambda x: eval(self.attributes[attribute]['function'])
                            val = fun(val)

                        self.vals[attribute].append(val)

                    if reached_end:
                        self.update_title()
                else:
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

            except Exception as ex:
                for attribute in self.attributes:
                    self.plot_panel[attribute].draw([], attribute, 'minutes', self.attributes[attribute]['unit'])
                self.update_title('Error while reading file data!')
                print("Error while reading file data: {0}".format(ex))
                self.alive = False

        print('Thread: Terminated')

    def run(self):
        self.alive = True
        self.main()

    def terminate(self):
        self.alive = False


def main():
    global do_restart

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

    if do_restart:
        python = sys.executable
        os.execl(python, python, * sys.argv)


if __name__ == "__main__":
    main()
