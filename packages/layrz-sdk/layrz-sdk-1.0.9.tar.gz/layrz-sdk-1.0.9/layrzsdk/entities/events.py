""" Events entitites """
class Trigger:
  """
  Trigger entity definition
  
  Available attributes
  --------------------
    pk (int): Trigger ID
    name (str): Trigger name
    code (str): Trigger code
  """
  
  def __init__(self, pk, name, code):
    """ Constructor """
    self.__pk = pk
    self.__name = name
    self.__code = code
  
  @property
  def pk(self):
    """ Trigger ID """
    return self.__pk
  
  @property
  def name(self):
    """ Trigger name """
    return self.__name
  
  @property
  def code(self):
    """ Trigger code """
    return self.__code
  
  @property
  def __readable(self):
    """ Readable """
    return f'Trigger(pk={self.__pk}, name="{self.__name}", code="{self.__code}")'
  
  def __str__(self):
    """ Readable property """
    return self.__readable
  
  def __repr__(self):
    """ Readable property """
    return self.__readable

class Event:
  """
  Event entity definition

  Available attributes
  --------------------
    pk (int): Event ID
    trigger (Trigger): Trigger object that triggered the event
    asset (Asset): Asset owner of the event
    message (Message): Telemetry information of the event
    activated_at (datetime): Reception/triggered at
  """
  
  def __init__(self, pk, trigger, asset, message, activated_at):
    """ Constructor """
    self.__pk = pk
    self.__trigger = trigger
    self.__asset = asset
    self.__message = message
    self.__activated_at = activated_at
  
  @property
  def pk(self):
    """ Event ID """
    return self.__pk
  
  @property
  def trigger(self):
    """ Trigger object that triggered the event """
    return self.__trigger
  
  @property
  def asset(self):
    """ Asset owner of the event """
    return self.__asset
  
  @property
  def message(self):
    """ Telemetry information of the event """
    return self.__message
  
  @property
  def activated_at(self):
    """ Reception/triggered at """
    return self.__activated_at
  
  @property
  def __readable(self):
    """ Readable """
    return f'Event(pk={self.__pk}, trigger={self.__trigger}, asset={self.__asset}, message={self.__message}, activated_at={self.__activated_at})'
  
  def __str__(self):
    """ Readable property """
    return self.__readable
  
  def __repr__(self):
    """ Readable property """
    return self.__readable