""" Message entities """

class Position:
  """
  Geographic position definition

  Available attributes
  --------------------
    latitude (float): Latitude (in decimal degrees)
    longitude (float): Longitude (in decimal degrees)
    altitude (float): Altitude (in meters)
    hdop (float): Horizontal dilution of precision
    speed (float): Speed (in Kilometers per hour)
    direction (float): Direction or heading (in degrees)
  """

  def __init__(self, latitude, longitude, altitude, hdop, speed, direction):
    """ Constructor """
    self.__latitude = latitude
    self.__longitude = longitude
    self.__altitude = altitude
    self.__hdop = hdop
    self.__speed = speed
    self.__direction = direction

  @property
  def latitude(self):
    """ Latitude """
    return self.__latitude

  @property
  def longitude(self):
    """ Longitude """
    return self.__longitude

  @property
  def altitude(self):
    """ Altitude """
    return self.__altitude

  @property
  def hdop(self):
    """ Horizontal dilution of precision """
    return self.__hdop

  @property
  def speed(self):
    """ Speed """
    return self.__speed

  @property
  def direction(self):
    """ Direction or heading """
    return self.__direction

  @property
  def __readable(self):
    """ Readable """
    return f'Position(latitude={self.__latitude}, longitude={self.__longitude}, altitude={self.__altitude}, speed={self.__speed}, direction={self.__direction}, hdop={self.__hdop})'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable

class Message:
  """
  Message definition

  Available attributes
  --------------------
    pk (int): Message ID
    asset_id (int): Asset ID
    position (Position): Geographic position
    payload (dict): Message raw payload
    sensors (dict): Calculated sensor values
    received_at (datetime(tzinfo=pytz.UTC)): Message reception date and time
  """

  def __init__(self, pk, asset_id, position, payload, sensors, received_at):
    """ Constructor """
    self.__pk = pk
    self.__asset_id = asset_id
    self.__position = position
    self.__payload = payload
    self.__sensors = sensors
    self.__received_at = received_at

  @property
  def pk(self):
    """ Message ID """
    return self.__pk

  @property
  def asset_id(self):
    """ Asset ID """
    return self.__asset_id

  @property
  def position(self):
    """ Geographic position """
    return self.__position

  @property
  def payload(self):
    """ Message raw payload """
    return self.__payload

  @property
  def sensors(self):
    """ Calculated sensor values """
    return self.__sensors

  @property
  def received_at(self):
    """ Message reception date and time """
    return self.__received_at
