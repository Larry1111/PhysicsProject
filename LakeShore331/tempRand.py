# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
import serial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import deque
from datetime import datetime, timedelta
import matplotlib.dates as mdates

serial_port = 'COM1'  # Update with the correct serial port name
baud_rate = 9600  # Baud rate specified in the device manual
data_bits = 7  # Number of data bits
stop_bits = serial.STOPBITS_ONE  # Specify one stop bit

parity = serial.PARITY_ODD 
class TemperatureMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.flag=0
        self.timer = QTimer()
        self.start_button = None
        # Initialize Lakeshore 331
        #self.ser = serial.Serial(serial_port, baud_rate, bytesize=data_bits, stopbits=stop_bits, parity=serial.PARITY_ODD, timeout=10)
        # Create main layout
        main_layout = QVBoxLayout()
        self.graph_widget = QWidget()
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        # Create bottom layout for labels
        bottom_layout = QHBoxLayout()
        self.channel_a_label = QLabel("Channel A: ")
        self.channel_a_label.setMaximumWidth(150)
        self.channel_a_label.setMaximumHeight(50)
        self.channel_a_label.setStyleSheet("border: 1px solid black; background-color: white;")
        self.channel_a_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.channel_a_label)

        self.channel_b_label = QLabel("Channel B: ")
        self.channel_b_label.setMaximumWidth(150)
        self.channel_b_label.setMaximumHeight(50)
        self.channel_b_label.setStyleSheet("border: 1px solid black; background-color: white;")
        self.channel_b_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.channel_b_label)
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        bottom_layout.addWidget(self.start_button)
        
        # Add bottom layout to main layout
        main_layout.addLayout(bottom_layout)

        # Set main layout as the central widget
        self.graph_widget.setLayout(main_layout)
        self.setCentralWidget(self.graph_widget)

        # Variables for storing temperature and time data
        self.temperatures_a = deque(maxlen=120)  # Keep only the last 2 minutes (120 seconds)
        self.temperatures_b = deque(maxlen=120)  # Keep only the last 2 minutes (120 seconds)
        self.times = deque(maxlen=120)  # Keep only the last 2 minutes (120 seconds)

        
    def start_timer(self):
        self.timer.timeout.connect(self.generate_random_data)
        self.timer.start(1000)  # Update every 1 second
        self.start_button.setEnabled(False)
        
    def read_temperature(self):
        # Send command to request temperature
        command1 = 'KRDG? A\r\n'
        self.ser.write(command1.encode())

        # Read temperature response
        response1 = self.ser.readline().decode().strip()
        
        command2 = 'KRDG? B\r\n'
        self.ser.write(command2.encode())

        # Read temperature response
        response2 = self.ser.readline().decode().strip()
        
        try:
            temperature_a = round(float(response1),3)
            temperature_b = round(float(response2),3)
            # Add temperature and current time to the data lists
            self.temperatures_a.append(temperature_a)
            self.temperatures_b.append(temperature_b)
            #self.times.append(len(self.temperatures_a))
            self.times.append(datetime.now())
            
            # Update the graph with new data
            self.update_graph()
            
            #Update the channel labels
            self.channel_a_label.setText(f"Channel A: {temperature_a:.2f} K")
            self.channel_b_label.setText(f"Channel B: {temperature_b:.2f} K")

        except ValueError:
            print("Invalid response:", response1, response2)
            
    def generate_random_data(self):
        # Generate random temperature values
        temperature_a = round(random.uniform(20, 30),3)
        temperature_b = round(random.uniform(15, 25),3)

        # Add temperature and current time to the data dequeues
        self.temperatures_a.append(temperature_a)
        self.temperatures_b.append(temperature_b)
        self.times.append(datetime.now())

        # Update the graph with new data
        self.update_graph()

        # Update the channel labels
        self.channel_a_label.setText(f"Channel A: {temperature_a:.2f} °C")
        self.channel_b_label.setText(f"Channel B: {temperature_b:.2f} °C")
        
        # Export temperature and time data to a text file
        self.export_data_to_file(datetime.now(), temperature_a, temperature_b)

    def update_graph(self):
        # Clear previous graph
        self.fig.clear()
        
        # Calculate the time range for the last two minutes
        now = datetime.now()
        two_minutes_ago = now - timedelta(minutes=2)
        

        # Filter the data for the last two minutes
        filtered_temperatures_a = [temp for temp, time in zip(self.temperatures_a, self.times) if time >= two_minutes_ago]
        filtered_temperatures_b = [temp for temp, time in zip(self.temperatures_b, self.times) if time >= two_minutes_ago]
        filtered_times = [time for time in self.times if time >= two_minutes_ago]

        # Convert filtered times to matplotlib compatible format
        filtered_times = mdates.date2num(filtered_times)

        # Plot temperature vs. time
        ax = self.fig.add_subplot(111)
        #ax.plot(self.times, self.temperatures_a, label='Channel A')
        #ax.plot(self.times, self.temperatures_b, label='Channel B')
        ax.plot(filtered_times, filtered_temperatures_a, label='Channel A')
        ax.plot(filtered_times, filtered_temperatures_b, label='Channel B')
        
        # Set labels and title
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Temperature(K)')
        ax.set_title('Temperature vs. Time')
        ax.legend()
        
       
        # Set x-axis limits to display the last two minutes (-2 to 0)
        ax.set_xlim(two_minutes_ago, now)
        #x = [-2, -1.5, -1, -0.5, 0]
        #ax.set_xticks(x)
        # Set the number of tick marks on the x-axis
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=20))

        #ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        # Manually set the tick positions and labels
        x = [-2, -1.5, -1, -0.5, 0]
        x_ticks = [now + timedelta(minutes=val) for val in x]  # Convert relative values to datetime
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x)
        
        # Redraw the graph
        self.canvas.draw()
        
    def export_data_to_file(self, timestamp, temperature_a, temperature_b):
        if(self.flag==0):
            self.file_name = f"temperature_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"


            # Specify the directory path for the text file
            self.directory = "/Users/larryli/Desktop/Physics/Madhukar/tempData"  # Update with the desired directory path

            # Create the directory if it doesn't exist
            os.makedirs(self.directory, exist_ok=True)

            # Create the file path
            self.file_path = os.path.join(self.directory, self.file_name)
        self.flag=1
        # Append data to the text file
        timestamp = timestamp.replace(microsecond=0)
        data = f"{timestamp}\t{temperature_a}\t{temperature_b}\n"
        
        # Append data to the text file
        with open(self.file_path, "a") as file:
            file.write(data)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = TemperatureMonitor()
    monitor.show()
    sys.exit(app.exec_())
