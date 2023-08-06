""" Charts simulator / faker """
import numpy as np
import matplotlib.pyplot as plt
from layrzsdk.entities import ChartConfiguration, ColumnChart, AreaChart, LineChart, PieChart, BarChart, RadialBarChart
from .messages import MessageFaker
from .exceptions import SimulatorException

class ChartFaker:
  """
  Chart faker
  """

  def __init__(self, messages_faker, calculate_series):
    """
    Constructor

    Args:
      messages_faker (MessageFaker): Message faker
      calculate_series (function): Function to calculate series
    """
    if not isinstance(messages_faker, MessageFaker):
      raise SimulatorException('messages_faker must be a MessageFaker')
    self.__messages_faker = messages_faker

    if not callable(calculate_series):
      raise SimulatorException('calculate_series must be a function')
    self.__calculate_series = calculate_series

  def perform(self):
    """ Perform simulation of charts """
    messages = self.__messages_faker.generate_messages()

    chart_result = self.__calculate_series(messages, configuration=ChartConfiguration(name='Fake chart', description='Fake chart'), assets=self.__messages_faker.assets)
    
    if isinstance(chart_result, ColumnChart):
      self.__plot_column_chart(chart_result)
    elif isinstance(chart_result, BarChart):
      print('Bar Chart not avainable, visualizing data using Column chart')
      self.__plot_column_chart(chart_result, is_bar_chart=True)
    elif isinstance(chart_result, AreaChart):
      self.__plot_line_chart(chart_result, with_area=True)
    elif isinstance(chart_result, LineChart):
      self.__plot_line_chart(chart_result, with_area=False)
    elif isinstance(chart_result, PieChart):
      self.__plot_pie_chart(chart_result)
    elif isinstance(chart_result, RadialBarChart):
      print('Radial Bar Chart not avainable, visualizing data using Pie chart')
      self.__plot_pie_chart(chart_result, is_bar_chart=True)
    else:
      print('Chart not supported yet')
  
  def __plot_pie_chart(self, chart, is_bar_chart=False):
    """ Plot pie chart """

    fig, ax = plt.subplots()

    series = [serie.data[0] for serie in chart.series]
    labels = [serie.label for serie in chart.series]

    ax.pie(series, labels=labels, autopct='%1.1f%%')
    fig.canvas.set_window_title(chart.title)
    if is_bar_chart:
      ax.set_title('Simulation not equals to Layrz Result\nRadial Bar Chart not supported, using Pie Chart')
    else:
      ax.set_title('Simulation not equals to Layrz Results')
    ax.grid(True)

    fig.tight_layout()
    plt.show()

  def __plot_line_chart(self, chart, with_area=False):
    """ Plot line chart """
    x_axis = chart.x_axis.data
    x = np.arange(len(x_axis))
    width = 0.15

    fig, ax = plt.subplots()
    for serie in chart.y_axis:
      if with_area:
        ax.fill_between(x_axis, serie.data, color=serie.color, alpha=0.4)
      ax.plot(x_axis, serie.data, label=serie.label, color=serie.color)

    fig.canvas.set_window_title(chart.title)
    ax.set_title('Simulation not equals to Layrz Results')
    ax.set_xticks(x, labels=chart.x_axis.data)
    ax.grid(True)
    plt.legend()

    fig.tight_layout()
    plt.show()

  def __plot_column_chart(self, chart, is_bar_chart=False):
    """ Plot column chart """
    x = np.arange(len(chart.x_axis.data))
    width = 0.15

    bars = []
    fig, ax = plt.subplots()
    for i, serie in enumerate(chart.y_axis):
      bars.append(
        ax.bar(x + (width * i), serie.data, width, label=serie.label)
      )

    fig.canvas.set_window_title(chart.title)
    if is_bar_chart:
      ax.set_title('Simulation not equals to Layrz Results\nBar Chart not supported, using Column Chart')
    else:
      ax.set_title('Simulation not equals to Layrz Results')
    ax.set_xticks(x, labels=chart.x_axis.data)
    ax.grid(True)
    plt.legend()

    for bar in bars:
      ax.bar_label(bar, padding=3)

    fig.tight_layout()
    plt.show()