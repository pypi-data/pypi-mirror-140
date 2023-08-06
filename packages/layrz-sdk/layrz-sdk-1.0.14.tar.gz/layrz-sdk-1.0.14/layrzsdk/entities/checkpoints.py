""" Checkpoints entitites """

class Geofence:
  """
  Geofence entity definition

  Available attributes
  --------------------
    pk (int): Geofence ID
    name (str): Geofence name
    color (str): Geofence color in Hex format
  """

  def __init__(self, pk, name, color):
    """ Constructor """
    self.__pk = pk
    self.__name = name
    self.__color = color

  @property
  def pk(self):
    """ Geofence ID """
    return self.__pk

  @property
  def name(self):
    """ Geofence name """
    return self.__name

  @property
  def color(self):
    """ Geofence color in Hex format """
    return self.__color

  @property
  def __readable(self):
    """ Readable """
    return f'Geofence(pk={self.__pk}, name="{self.__name}", color="{self.__color}")'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable

class Waypoint:
  """
  Checkpoint waypoint entity definition

  Available attributes
  --------------------
    pk (int): Waypoint ID
    geofence (Geofence): Related geofence
    start_at (datetime): Date of start this waypoint stage
    end_at (datetime): Date of end this waypoint stage
    sequence_real (int): Real sequence performed
    sequence_ideal (int): Ideal/defined sequence
  """
  
  def __init__(self, pk, geofence, start_at, end_at, sequence_real, sequence_ideal):
    """ Constructor """
    self.__pk = pk
    self.__geofence = geofence
    self.__start_at = start_at
    self.__end_at = end_at
    self.__sequence_real = sequence_real
    self.__sequence_ideal = sequence_ideal

  @property
  def pk(self):
    """ Waypoint ID """
    return self.__pk

  @property
  def geofence(self):
    """ Related geofence """
    return self.__geofence

  @property
  def start_at(self):
    """ Date of start this waypoint stage """
    return self.__start_at

  @property
  def end_at(self):
    """ Date of end this waypoint stage """
    return self.__end_at

  @property
  def sequence_real(self):
    """ Real sequence performed """
    return self.__sequence_real

  @property
  def sequence_ideal(self):
    """ Ideal/defined sequence """
    return self.__sequence_ideal

  @property
  def __readable(self):
    """ Readable """
    return f'Waypoint(pk={self.__pk}, geofence={self.__geofence}, start_at={self.__start_at}, end_at={self.__end_at}, sequence_real={self.__sequence_real}, sequence_ideal={self.__sequence_ideal})'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable

class Checkpoint:
  """
  Checkpoint entity definition

  Available attributes
  --------------------
    pk (int): Checkpoint activation ID
    asset_id (int): Asset ID
    waypoints (list(Waypoint)): List of waypoints of the checkpoint
    start_at (datetime): Start date
    end_at (datetime): End date
  """

  def __init__(self, pk, asset_id, waypoints, start_at, end_at):
    """ Constructor """
    self.__pk = pk
    self.__asset_id = asset_id
    self.__waypoints = waypoints
    self.__start_at = start_at
    self.__end_at = end_at

  @property
  def pk(self):
    """ Checkpoint activation ID """
    return self.__pk

  @property
  def asset_id(self):
    """ Asset ID """
    return self.__asset_id

  @property
  def waypoints(self):
    """ List of waypoints of the checkpoint """
    return self.__waypoints

  @property
  def start_at(self):
    """ Start date """
    return self.__start_at

  @property
  def end_at(self):
    """ End date """
    return self.__end_at

  @property
  def __readable(self):
    """ Readable """
    return f'Checkpoint(pk={self.__pk}, asset_id={self.__asset_id}, waypoints={self.__waypoints}, start_at={self.__start_at}, end_at={self.__end_at})'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable
