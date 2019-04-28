import sys
import discarded_code.display_ui.kivHelper as kh
import numpy as np
import sqlite3
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from collections import Counter

conn = sqlite3.connect('../databases/taskrabbit.db')
c = conn.cursor()
subtitleFont = QFont("Times", 18, QFont.Bold)
textFont = QFont("Times", 14)
class App(QMainWindow):

    def __init__(self):
        self.funcs = {
            0: self.drawTaskersPerLocation,
            1: self.drawSharedTaskers,
            2: self.draw_taskers_with_reviews,
            3: self.average_cost
        }
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'TaskRabbit analysis app'
        self.width = 1300
        self.height = 800
        self.initUI()

    def initUI(self):
        self.current_plot = 0
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        canv = QWidget(self)
        canv.setMinimumHeight(800)
        canv.setMinimumWidth(1000)
        self.plotWidget = MplWidget(canv)
        self.plotWidget.setGeometry(QRect(0, 50, 1000, 700))
        self.comboBox = QComboBox(self)
        #self.comboBox.currentIndexChanged.connect(self.updateGraph)
        c.execute("SELECT name FROM cities;")
        for row in c:
            self.comboBox.addItem(row[0])

        self.city_name = str(self.comboBox.currentText())
        self.comboBox.currentIndexChanged.connect(self.update_city)

        l1 = self.create_label("Pick city:", subtitleFont)
        l1.move(1050,10)

        self.comboBox.move(1050, 30)

        self.create_label("City details", subtitleFont).move(1050,90)
        self.l_taskers = self.create_label("Num of taskers: 100000", textFont)
        self.l_reviews = self.create_label("Num of reviews: 200000", textFont)
        self.l_taskers.move(1050,120)
        self.l_reviews.move(1050,140)
        self.update_city()

        button = QPushButton('Total taskers', self)
        button.move(1000, 210)
        button.resize(160, 50)
        button.clicked.connect(lambda: self.plot_data(0))

        button = QPushButton('Shared taskers', self)
        button.setToolTip('Show how taskers are shared across locations')
        button.move(1000, 280)
        button.resize(160, 50)
        button.clicked.connect(lambda: self.plot_data(1))

        button = QPushButton('Taskers with reviews', self)
        button.move(1000, 350)
        button.resize(160, 50)
        button.clicked.connect(lambda: self.plot_data(2))

        button = QPushButton('Average cost', self)
        button.move(1000, 420)
        button.resize(160, 50)
        button.clicked.connect(lambda: self.plot_data(3))

    def update_city(self):
        self.city_name = str(self.comboBox.currentText())
        c.execute("SELECT num_taskers, num_reviews FROM cities, city_details WHERE city_details.city_id = cities.city_id AND cities.name = '" + self.city_name + "';")
        city_details = c.fetchone()
        self.l_taskers.setText("Num of taskers: " + str(city_details[0]))
        self.l_reviews.setText("Num of reviews " + str(city_details[1]))
        self.plot_data(self.current_plot)

    def plot_data(self, i):
        self.current_plot = i
        self.plotWidget.canvas.ax.clear()
        f = self.funcs[i]
        f()
        
    def draw_key_value_bars(self, dict, title, xlabel, ylabel):
        keys = []
        vals = []
        for elem in dict.keys():
            keys.append(elem)
            vals.append(dict[elem])

        y_pos = np.arange(len(keys))

        self.plotWidget.canvas.ax.bar(keys, vals, align='center', alpha=0.5)
        labels = []
        for l in keys:
            labels.append("\n".join(l.split(" ")))
        self.plotWidget.canvas.ax.set_xticks(y_pos, labels)
        self.plotWidget.canvas.ax.set_xticklabels(labels)
        self.plotWidget.canvas.ax.set_ylabel(ylabel)
        self.plotWidget.canvas.ax.set_xlabel(xlabel)
        self.plotWidget.canvas.ax.set_title(title)
        self.plotWidget.canvas.draw()

    def drawTaskersPerLocation(self):
        locations = kh.get_locations_in_city(self.city_name)
        num_of_taskers = kh.get_num_taskers_per_location(locations)
        self.draw_key_value_bars(num_of_taskers, "Number of taskers across each area", "Areas in " + self.city_name,
                                  "Number of taskers")

    def drawSharedTaskers(self):
        locations = kh.get_locations_in_city(self.city_name)
        location_taskers = kh.get_taskers_per_location(locations)
        locations = [location[0] for location in locations]
        arrays = []
        for i in range(len(locations)):
            arr = []
            for location in locations:
                i_shared = sum([1 if len([x for x in location_taskers.keys() if
                                          (not x == location) and Counter(location_taskers[x])[tasker] > 0]) == i else 0
                                for tasker in location_taskers[location]])
                arr.append(i_shared)
            arrays.append(arr)
        X = len(locations)
        for i, arr in enumerate(arrays):
            if i == 0:
                self.plotWidget.canvas.ax.bar(np.arange(X), arr, label="Unique")
            else:
                self.plotWidget.canvas.ax.bar(np.arange(X), arr, bottom=[sum(x) for x in zip(*[a for j, a in enumerate(arrays) if j < i])],
                        label="Shared with " + str(i))
        self.plotWidget.canvas.ax.legend()
        self.plotWidget.canvas.ax.set_xticks(np.arange(X))
        labels = []
        for l in locations:
            labels.append("\n".join(l.split(" ")))
        self.plotWidget.canvas.ax.set_xticklabels(labels)
        self.plotWidget.canvas.ax.set_title("Taskers shared across locations")
        self.plotWidget.canvas.ax.set_ylabel("Number of taskers")
        self.plotWidget.canvas.ax.set_xlabel("Areas in " + self.city_name)
        self.plotWidget.canvas.draw()

    def draw_taskers_with_reviews(self):
        locations = kh.get_locations_in_city(self.city_name)
        num_of_taskers = kh.get_num_taskers_per_location(locations)
        taskers_with_review = {}
        for location in locations:
            c.execute(
                "SELECT count(*) FROM taskers, tasker_locations WHERE exists (SELECT * FROM reviews WHERE [tasker_id] = taskers.tasker_id) AND taskers.tasker_id = tasker_locations.tasker_id AND tasker_locations.location_id = " + str(
                    location[1]) + ";")
            taskers_with_review[location[0]] = round((c.fetchone()[0] / num_of_taskers[location[0]]) * 100, 2)

        self.draw_key_value_bars(taskers_with_review, "Percentage of taskers with reviews in each area",
                             "Areas in " + self.city_name, "Taskers with reviews (%)")

    '''
    def draw_reviews_per_tasker(self):
        locations = kh.get_locations_in_city(self.city_name)
        num_of_taskers = kh.get_num_taskers_per_location(locations)
        taskers_with_review = {}
        for location in locations:
            c.execute("SELECT AVG()")
            c.execute(
                "SELECT count(*) FROM taskers, tasker_locations WHERE exists (SELECT * FROM reviews WHERE [tasker_id] = taskers.tasker_id) AND taskers.tasker_id = tasker_locations.tasker_id AND tasker_locations.location_id = " + str(
                    location[1]) + ";")
            taskers_with_review[location[0]] = round((c.fetchone()[0] / num_of_taskers[location[0]]) * 100, 2)

        self.draw_key_value_bars(taskers_with_review, "Percentage of taskers with reviews in each area",
                             "Areas in " + self.city_name, "Taskers with reviews (%)")
    '''

    def average_cost(self):
        locations = kh.get_locations_in_city(self.city_name)
        cost_per_locations = {}
        for location in locations:
            c.execute(
                "SELECT AVG(amount) FROM price_details INNER JOIN taskers ON taskers.tasker_id = price_details.tasker_id INNER JOIN tasker_locations ON tasker_locations.tasker_id = taskers.tasker_id INNER JOIN  locations ON locations.location_id = tasker_locations.location_id WHERE locations.name = '" +
                location[0] + "' GROUP BY locations.location_id ORDER BY AVG(amount) DESC;")

            cost_per_locations[location[0]] = c.fetchone()[0]
        self.draw_key_value_bars(cost_per_locations, "Average cost per service",
                                  "Areas in " + self.city_name, "Average cost of tasker in each location")

    def create_label(self, text, font):
        label = QLabel(self)
        label.setText(text)
        label.setFont(font)
        label.adjustSize()
        label.setAlignment(Qt.AlignCenter)
        return label
# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())