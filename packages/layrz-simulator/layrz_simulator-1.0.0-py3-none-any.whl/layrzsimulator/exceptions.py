""" Simulator exceptions """

class SimulatorException(BaseException):
  """
  Simulator Exception
  """
  def __init__(self, message):
    """ Constructor """
    self.__message = message

  @property
  def __readable(self):
    """ Readable """
    return f'SimulatorException: {self.__message}'

  def __str__(self):
    """ Readable property """
    return self.__readable

  def __repr__(self):
    """ Readable property """
    return self.__readable