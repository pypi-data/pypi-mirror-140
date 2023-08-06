"""
Assets and related entities
"""
from enum import Enum

class AssetOperationMode(Enum):
  """
  Asset Operation mode definition
  It's an enum of the operation mode of the asset.
  """
  SINGLE = 'SINGLE'
  MULTIPLE = 'MULTIPLE'
  ASSETMULTIPLE = 'ASSETMULTIPLE'
  DISCONNECTED = 'DISCONNECTED'
  FAILOVER = 'FAILOVER'

  @property
  def __readable(self):
    """ Readable """
    return self.value

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable

class Asset:
  """
  Asset entity definition

  Available attributes
  --------------------
    pk (int): Asset ID
    name (str): Name of the asset
    devices (list(Device)=[]): List of devices
    vin (str): Vehicle identification number
    plate (str): Vehicle plate number
    asset_type (int): Asset type ID
    operation_mode (AssetOperationMode): Operation mode of the asset
    custom_fields (list(CustomField)=[]): List of custom fields
    children (list(Asset)=[]): List of children assets
    sensors (list(Sensor)=[]): List of sensors
  """

  def __init__(self, pk, name, vin, plate, asset_type, operation_mode, sensors=[], custom_fields=[], devices=[], children=[]):
    """ Constructor """
    self.__pk = pk
    self.__name = name
    self.__devices = devices
    self.__vin = vin
    self.__plate = plate
    self.__asset_type = asset_type
    self.__operation_mode = operation_mode
    self.__custom_fields = custom_fields
    self.__children = children
    self.__sensors = sensors

  @property
  def pk(self):
    """ Asset ID """
    return self.__pk

  @property
  def name(self):
    """ Name of the asset """
    return self.__name

  @property
  def devices(self):
    """ List of devices """
    return self.__devices

  @property
  def vin(self):
    """ Vehicle identification number """
    return self.__vin

  @property
  def plate(self):
    """ Vehicle plate number """
    return self.__plate

  @property
  def asset_type(self):
    """ Asset type ID """
    return self.__asset_type

  @property
  def operation_mode(self):
    """ Operation mode of the asset """
    return self.__operation_mode

  @property
  def custom_fields(self):
    """ Custom fields """
    return self.__custom_fields

  @property
  def children(self):
    """ Children assets """
    return self.__children

  @property
  def sensors(self):
    """ Sensors """
    return self.__sensors

class Sensor:
  """
  Sensor entity

  Available attributes
  --------------------
    pk (int): Sensor ID
    name (str): Name of the sensor
    slug (str): Slug of the sensor
  """

  def __init__(self, pk, name, slug):
    """ Constructor """
    self.__pk = pk
    self.__name = name
    self.__slug = slug

  @property
  def pk(self):
    """ Sensor ID """
    return self.__pk

  @property
  def name(self):
    """ Name of the sensor """
    return self.__name

  @property
  def slug(self):
    """ Slug of the sensor """
    return self.__slug

  @property
  def __readable(self):
    """ Readable """
    return f'Sensor(pk={self.__pk}, name="{self.__name}", slug="{self.__slug}")'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable