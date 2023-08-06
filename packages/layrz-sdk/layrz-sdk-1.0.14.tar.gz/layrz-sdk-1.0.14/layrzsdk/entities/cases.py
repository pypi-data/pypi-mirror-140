""" Events entitites """

class User:
  """
  User entity definition
  
  Available attributes
  --------------------
    pk (int): User ID
    name (str): User name
  """
  
  def __init__(self, pk, name):
    """ Constructor """
    self.__pk = pk
    self.__name = name
  
  @property
  def pk(self):
    """ User ID """
    return self.__pk
  
  @property
  def name(self):
    """ User name """
    return self.__name

  @property
  def __readable(self):
    """ Readable """
    return f'User(pk={self.__pk}, name="{self.__name}")'
  
  def __str__(self):
    """ Readable property """
    return self.__readable
  
  def __repr__(self):
    """ Readable property """
    return self.__readable

class Comment:
  """
  Case comment entity definition

  Available attributes
  --------------------
    pk (int): Comment ID
    content (str): Comment content
    user (User): Operator/User what commented the case
    submitted_at (datetime): Date of comment submission
  """

  def __init__(self, pk, content, user, submitted_at):
    """ Constructor """
    self.__pk = pk
    self.__content = content
    self.__user = user
    self.__submitted_at = submitted_at
  
  @property
  def pk(self):
    """ Comment ID """
    return self.__pk
  
  @property
  def content(self):
    """ Comment content """
    return self.__content
  
  @property
  def user(self):
    """ Operator/User who commented the case """
    return self.__user
  
  @property
  def submitted_at(self):
    """ Date of comment submission """
    return self.__submitted_at

  @property
  def __readable(self):
    """ Readable """
    return f'Comment(pk={self.__pk}, content="{self.__content}", user={self.__user}, submitted_at={self.__submitted_at})'
  
  def __str__(self):
    """ Readable property """
    return self.__readable
  
  def __repr__(self):
    """ Readable property """
    return self.__readable

class Case:
  """
  Case entity definition

  Available attributes
  --------------------
    pk (int): Case ID
    trigger (Trigger): Trigger object that triggered the case
    asset_id (int): Asset ID
    comments list(Comment): List of comments submitted when the case was opened.
    opened_at (datetime): Date of case opening
    closed_at (datetime): Date of case closing
  """

  def __init__(self, pk, trigger, asset_id, comments, opened_at, closed_at):
    """ Constructor """
    self.__pk = pk
    self.__trigger = trigger
    self.__asset_id = asset_id
    self.__comments = comments
    self.__opened_at = opened_at
    self.__closed_at = closed_at
  
  @property
  def pk(self):
    """ Case ID """
    return self.__pk
  
  @property
  def trigger(self):
    """ Trigger object that triggered the case """
    return self.__trigger
  
  @property
  def asset_id(self):
    """ Asset ID """
    return self.__asset_id
  
  @property
  def comments(self):
    """ List of comments submitted when the case was opened """
    return self.__comments
  
  @property
  def opened_at(self):
    """ Date of case opening """
    return self.__opened_at
  
  @property
  def closed_at(self):
    """ Date of case closing """
    return self.__closed_at

  @property
  def __readable(self):
    """ Readable """
    return f'Case(pk={self.__pk}, trigger={self.__trigger}, asset_id={self.__asset_id}, comments={self.__comments}, opened_at={self.__opened_at}, closed_at={self.__closed_at})'
  
  def __str__(self):
    """ Readable property """
    return self.__readable
  
  def __repr__(self):
    """ Readable property """
    return self.__readable