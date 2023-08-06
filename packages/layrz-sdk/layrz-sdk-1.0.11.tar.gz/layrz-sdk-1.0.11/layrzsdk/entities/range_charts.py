""" Range charts entities """
import json
from .charts import ChartDataSerie, ChartAlignment, ChartException

class AreaChart:
  """
  Area chart configuration

  """

  def __init__(self, x_axis, y_axis, title='Chart', align=ChartAlignment.CENTER):
    """
    Constructor

    Args
    ----
      x_axis ChartDataSerie: Defines the X Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
      y_axis list(ChartDataSerie): Defines the Y Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
    """
    for i, serie in enumerate(y_axis):
      if not isinstance(serie, ChartDataSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.__x_axis = x_axis

    if not isinstance(x_axis, ChartDataSerie):
      raise ChartException('X Axis must be an instance of ChartDataSerie')
    self.__y_axis = y_axis

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.__title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.__align = align

  @property
  def x_axis(self):
    """ X Axis of the chart """
    return self.__x_axis

  @property
  def y_axis(self):
    """ Y Axis of the chart """
    return self.__y_axis

  @property
  def title(self):
    """ Title of the chart """
    return self.__title

  @property
  def to_apexcharts(self):
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.__y_axis:
      series.append({
        'name': serie.label,
        'data': serie.data
      })
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'categories': self.__x_axis.data,
        'type': self.__x_axis.data_type.value,
        'title': {
          'text': self.__x_axis.label
        }
      },
      'title': {
        'text': self.__title,
        'align': self.__align.value
      },
      'chart': {
        'type': 'area'
      }
    }

    return json.dumps(config)

class LineChart:
  """
  Line chart configuration

  """

  def __init__(self, x_axis, y_axis, title='Chart', align=ChartAlignment.CENTER):
    """
    Constructor

    Args
    ----
      x_axis ChartDataSerie: Defines the X Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
      y_axis list(ChartDataSerie): Defines the Y Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
    """
    for i, serie in enumerate(y_axis):
      if not isinstance(serie, ChartDataSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.__x_axis = x_axis

    if not isinstance(x_axis, ChartDataSerie):
      raise ChartException('X Axis must be an instance of ChartDataSerie')
    self.__y_axis = y_axis

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.__title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.__align = align

  @property
  def x_axis(self):
    """ X Axis of the chart """
    return self.__x_axis

  @property
  def y_axis(self):
    """ Y Axis of the chart """
    return self.__y_axis

  @property
  def title(self):
    """ Title of the chart """
    return self.__title

  @property
  def to_apexcharts(self):
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.__y_axis:
      series.append({
        'name': serie.label,
        'data': serie.data
      })
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'categories': self.__x_axis.data,
        'type': self.__x_axis.data_type.value,
        'title': {
          'text': self.__x_axis.label
        }
      },
      'title': {
        'text': self.__title,
        'align': self.__align.value
      },
      'chart': {
        'type': 'line'
      }
    }

    return json.dumps(config)

class ColumnChart:
  """
  Column chart configuration

  """

  def __init__(self, x_axis, y_axis, title='Chart', align=ChartAlignment.CENTER):
    """
    Constructor

    Args
    ----
      x_axis ChartDataSerie: Defines the X Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
      y_axis list(ChartDataSerie): Defines the Y Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
    """
    for i, serie in enumerate(y_axis):
      if not isinstance(serie, ChartDataSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.__x_axis = x_axis

    if not isinstance(x_axis, ChartDataSerie):
      raise ChartException('X Axis must be an instance of ChartDataSerie')
    self.__y_axis = y_axis

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.__title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.__align = align

  @property
  def x_axis(self):
    """ X Axis of the chart """
    return self.__x_axis

  @property
  def y_axis(self):
    """ Y Axis of the chart """
    return self.__y_axis

  @property
  def title(self):
    """ Title of the chart """
    return self.__title

  @property
  def to_apexcharts(self):
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.__y_axis:
      series.append({
        'name': serie.label,
        'data': serie.data
      })
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'categories': self.__x_axis.data,
        'type': self.__x_axis.data_type.value,
        'title': {
          'text': self.__x_axis.label
        }
      },
      'title': {
        'text': self.__title,
        'align': self.__align.value
      },
      'chart': {
        'type': 'bar'
      },
      'plotOptions': {
        'bar': {
          'horizontal': False,
          'columnWidth': '55%',
          'endingShape': 'rounded'
        }
      }
    }

    return json.dumps(config)

class BarChart:
  """
  Bar chart configuration

  """

  def __init__(self, x_axis, y_axis, title='Chart', align=ChartAlignment.CENTER):
    """
    Constructor

    Args
    ----
      x_axis ChartDataSerie: Defines the X Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
      y_axis list(ChartDataSerie): Defines the Y Axis of the chart, uses the ChartDataSerie class. Please read the documentation to more information.
    """
    for i, serie in enumerate(y_axis):
      if not isinstance(serie, ChartDataSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.__y_axis = y_axis

    if not isinstance(x_axis, ChartDataSerie):
      raise ChartException('X Axis must be an instance of ChartDataSerie')
    self.__x_axis = x_axis

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.__title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.__align = align

  @property
  def x_axis(self):
    """ X Axis of the chart """
    return self.__x_axis

  @property
  def y_axis(self):
    """ Y Axis of the chart """
    return self.__y_axis

  @property
  def title(self):
    """ Title of the chart """
    return self.__title

  @property
  def to_apexcharts(self):
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.__y_axis:
      series.append({
        'name': serie.label,
        'data': serie.data
      })
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'categories': self.__x_axis.data,
        'type': self.__x_axis.data_type.value,
        'title': {
          'text': self.__x_axis.label
        }
      },
      'title': {
        'text': self.__title,
        'align': self.__align.value
      },
      'chart': {
        'type': 'bar'
      },
      'plotOptions': {
        'bar': {
          'horizontal': True,
          'borderRadius': 4
        }
      }
    }

    return json.dumps(config)
