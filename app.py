from flask import Flask, render_template
import psutil
import plotly.graph_objs as go
from plotly.offline import plot
import time

app = Flask(__name__)

def get_system_info():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get memory usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Get battery information (for laptops)
    battery_info = None
    if psutil.sensors_battery():
        battery_info = {
            'percent': psutil.sensors_battery().percent,
            'power_plugged': psutil.sensors_battery().power_plugged
        }

    # Get process information
    processes = [{'name': proc.info['name'], 'cpu_percent': proc.info['cpu_percent']} for proc in psutil.process_iter(['name', 'cpu_percent'])]

    return cpu_usage, memory_usage, battery_info, processes

def plot_system_info(cpu_usage, memory_usage, battery_info, processes):
    # Plot CPU usage
    cpu_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cpu_usage,
        title={'text': "CPU Usage (%)"},
        gauge={'axis': {'range': [0, 100]}}
    ))
    cpu_plot = cpu_fig.to_html(full_html=False)

    # Plot memory usage
    memory_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=memory_usage,
        title={'text': "Memory Usage (%)"},
        gauge={'axis': {'range': [0, 100]}}
    ))
    memory_plot = memory_fig.to_html(full_html=False)

    # Plot battery information (for laptops)
    if battery_info:
        battery_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=battery_info['percent'],
            title={'text': "Battery Percentage"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        battery_plot = battery_fig.to_html(full_html=False)
    else:
        battery_plot = None

    # Table for process information
    process_table = go.Figure(data=[go.Table(
        header=dict(values=['Process Name', 'CPU Percent']),
        cells=dict(values=[[proc['name'] for proc in processes],
                           [proc['cpu_percent'] for proc in processes]])
    )])
    process_plot = process_table.to_html(full_html=False)

    return cpu_plot, memory_plot, battery_plot, process_plot


@app.route('/')
def index():
    cpu_usage, memory_usage, battery_info, processes = get_system_info()
    cpu_plot, memory_plot, battery_plot, process_plot = plot_system_info(cpu_usage, memory_usage, battery_info, processes)
    return render_template('index.html', cpu_plot=cpu_plot, memory_plot=memory_plot, battery_plot=battery_plot, process_plot=process_plot)

if __name__ == "__main__":
    app.run(debug=True)