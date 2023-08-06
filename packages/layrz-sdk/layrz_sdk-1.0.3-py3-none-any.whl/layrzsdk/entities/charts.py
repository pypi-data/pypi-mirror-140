""" Charts entities """
from enum import Enum

class ChartDataSerie:
  """
  Chart Serie
  """

  def __init__(self, data, color, label):
    """
    Constructor

    Args
    ----
      data list((float, int, bool)): List of data points.
      color str: Color of the serie.
      label str: Label of the serie.
    """
    for i, datum in enumerate(data):
      if not isinstance(datum, (int, float, bool)):
        raise ChartException(f'Data point {i} must be an instance of int, float or bool')
    self.__data = data

    if not isinstance(color, str):
      raise ChartException('color must be an instance of str')
    self.__color = color

    if not isinstance(label, str):
      raise ChartException('label must be an instance of str')
    self.__label = label

  @property
  def data(self):
    """ List of data points """
    return self.__data

  @property
  def color(self):
    """ Color of the serie """
    return self.__color

  @property
  def label(self):
    """ Label of the serie """
    return self.__label

class ChartAlignment(Enum):
  """
  Chart Alignment
  """
  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'

class ChartException(BaseException):
  """
  Chart Exception
  """
  def __init__(self, message):
    """ Constructor """
    self.__message = message

  @property
  def __readable(self):
    """ Readable """
    return f'ChartException: {self.__message}'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable

class ChartConfiguration:
  """
  Chart configuration
  """

  def __init__(self, name, description):
    """ Constructor """
    self.__name = name
    self.__description = description

  @property
  def name(self):
    """ Name of the chart """
    return self.__name

  @property
  def description(self):
    """ Description of the chart """
    return self.__description

  @property
  def __readable(self):
    """ Readable """
    return f'ChartConfiguration(name="{self.__name}")'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable