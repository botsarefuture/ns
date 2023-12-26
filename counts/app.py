import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

class ChartApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Clients Count Chart")

        self.create_widgets()
        self.update_chart()  # Initial update
        self.schedule_update()  # Schedule periodic updates

    def create_widgets(self):
        # Label
        label = ttk.Label(self.master, text="Clients Count Chart")
        label.pack(pady=10)

        # Canvas for the chart
        self.chart_canvas = FigureCanvasTkAgg(self.create_chart(), master=self.master)
        self.chart_canvas.get_tk_widget().pack()

    def create_chart(self, clients_counts=None):
        # Create a chart with the given clients_counts data
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if clients_counts is not None:
            # Extract x (time) and y (clients count) from clients_counts
            x = [entry['_id'] for entry in clients_counts]
            y = [entry['count'] for entry in clients_counts]

            # Plot the data
            ax.plot(x, y, marker='o')
            ax.set_title('Clients Count Chart')
            ax.set_xlabel('Time')
            ax.set_ylabel('Clients Count')

        return fig

    def update_chart(self):
        # Fetch data from the specified URL
        url = "http://10.0.0.7:5000/get_clients_count/"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            clients_counts = data.get('clients_counts_over_time', [])
            self.update_chart_canvas(clients_counts)
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

        # Schedule the next update
        self.schedule_update()

    def update_chart_canvas(self, clients_counts):
        # Regenerate the chart with the new data
        self.chart_canvas.get_tk_widget().destroy()
        self.chart_canvas = FigureCanvasTkAgg(self.create_chart(clients_counts), master=self.master)
        self.chart_canvas.get_tk_widget().pack()

    def schedule_update(self):
        # Schedule the next update after 5000 milliseconds (5 seconds)
        self.master.after(5000, self.update_chart)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChartApp(root)
    root.mainloop()
