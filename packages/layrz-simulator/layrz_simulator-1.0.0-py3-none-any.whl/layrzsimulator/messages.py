""" Message creator simulator """
import random
from datetime import datetime, timedelta
import pytz
from layrzsdk.entities import Asset, Device, Sensor, Message, Position, AssetOperationMode
from .exceptions import SimulatorException

class MessageFaker:
  """
  MessageFaker

  Will generate fake messages for testing purposes.
  """

  def __init__(self, assets_struct, payload_struct={}, sensors_struct={}, num_of_records=1):
    """
    Initialize MessageFaker

    Args:
      num_of_records (int): Number of records to generate
      payload_struct (dict): Payload structure, see example below
      sensors_struct (dict): Sensors structure, see example below
      assets_struct (dict): Assets structure, see example below

    Examples:
      assets_struct = [
        {
          'idents': ['ident1', 'ident2'],     # List of idents to append into this asset.
          'vin': '',                          # VIN of the Asset, default: empty str
          'plate': '',                        # Plate of the Asset
        },
      ]

      sensors_struct = {
        'sensor1': (int, 0, 10),      # 0 as minimum, 10 as maximum
        'sensor2': (float, 10, 100),  # 10 as minimum, 100 as maximum
        'sensor3': (str, 10),         # 10 is the length of the string
        'sensor4': (bool,)            # True or False, does not requires min/max
      }
      Note: The keys of the `sensors_struct` will convert to sensors entities to the asset automatically.

      payload_struct = {
        'fuel.level': (int, 0, 100),        # 0 as minimum, 100 as maximum
        'trunk.laod': (float, 10, 100),     # 10 as minimum, 100 as maximum
        'engine.ignition.status': (bool,),  # True or False, does not requires min/max
        'ibutton.code': (str, 10),          # 10 is the length of the string
      }

      Note: The keys of the `payload_struct` will convert to raw payload of the devices, and will append automatically the idents.
    """
    if payload_struct is None:
      raise SimulatorException('payload_struct is required')

    if not isinstance(payload_struct, dict):
      raise SimulatorException('payload_struct must be a dict')

    for key, struct in payload_struct.items():
      self.__check_struct(name='payload_struct', key=key, struct=struct)

    self.__payload_struct = payload_struct

    if sensors_struct is None:
      raise SimulatorException('sensors_struct is required')

    if not isinstance(sensors_struct, dict):
      raise SimulatorException('sensors_struct must be a dict')

    for key, struct in sensors_struct.items():
      self.__check_struct(name='sensors_struct', key=key, struct=struct)

    self.__sensors_struct = sensors_struct

    if assets_struct is None:
      raise SimulatorException('assets_struct is required')

    if not isinstance(assets_struct, list):
      raise SimulatorException('assets_struct must be a list')

    for i, asset in enumerate(assets_struct):
      if not isinstance(asset, dict):
        raise SimulatorException(f'Malformed assets_struct[{i}]: Must be a dict')

      if 'idents' not in asset:
        raise SimulatorException(f'Malformed assets_struct[{i}]: Must have idents')

      if not isinstance(asset['idents'], list):
        raise SimulatorException(f'Malformed assets_struct[{i}].idents: Must be a list')

      if len(asset['idents']) == 0:
        raise SimulatorException(f'Malformed assets_struct[{i}].idents: Must have at least one ident')

    self.__assets_struct = assets_struct

    if num_of_records < 1:
      raise SimulatorException('num_of_records must be greater than 0')

    self.__num_of_records = num_of_records
    self.__assets = []

  def generate_messages(self):
    """ Generate messages using the structure """
    messages = []
    self.__assets = []

    for i, asset in enumerate(self.__assets_struct):
      start_at = datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(minutes=(5 * self.__num_of_records))
      sensors = [Sensor(pk=random.randint(0, 100), name=key, slug=key) for key, _ in self.__sensors_struct.items()]
      devices = [Device(pk=random.randint(0, 100), name=ident, ident=ident, protocol='alpharest', is_primary=True if i == 0 else False) for i, ident in enumerate(asset['idents'])]
      asset = Asset(
        pk=random.randint(0, 100),
        name=f'Asset {i}',
        plate=asset['plate'] if 'plate' in asset else '',
        vin=asset['vin'] if 'vin' in asset else '',
        devices=devices,
        sensors=sensors,
        asset_type=1,
        operation_mode=AssetOperationMode.SINGLE if len(devices) == 1 else AssetOperationMode.MULTIPLE
      )
      self.__assets.append(asset)

      for j in range(self.__num_of_records):
        payload = {}
        sensors = {}

        for key, struct in self.__payload_struct.items():
          for device in devices:
            payload[f'{device.ident}.{key}'] = self.__generate_payload(struct=struct)

        for key, struct in self.__sensors_struct.items():
          sensors[key] = self.__generate_payload(struct=struct)

        messages.append(
          Message(
            pk=random.randint(0, 100),
            asset_id=asset.pk,
            position=Position(
              latitude=random.uniform(-90, 90),
              longitude=random.uniform(-180, 180),
              altitude=random.uniform(0, 100),
              speed=random.uniform(0, 100),
              direction=random.uniform(0, 360),
              hdop=random.uniform(0, 25)
            ),
            payload=payload,
            sensors=sensors,
            received_at=start_at
          )
        )

        start_at = start_at + timedelta(minutes=5)

    return messages

  def __generate_payload(self, struct):
    """
    Generate a payload using the defined structure
    """
    data_type = struct[0]

    if data_type == int:
      return random.randint(*struct[1:])

    if data_type == float:
      return random.uniform(*struct[1:])

    if data_type == str:
      return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(struct[1]))

    if data_type == bool:
      return random.choice([True, False])

  def __check_struct(self, name, key, struct):
    """ Check struc of `payload_struct` and `sensors_struct` """
    if not isinstance(struct, tuple):
      raise SimulatorException(f'Malformed {name}.{key}: Must be a tuple')

    data_type = struct[0]
    if isinstance(data_type, (int, float)) and len(struct) != 3:
      raise SimulatorException(f'Malformed {name}.{key}: Must be a tuple with 3 elements')
    elif isinstance(data_type, str) and len(struct) != 2:
      raise SimulatorException(f'Malformed {name}.{key}: Must be a tuple with 2 elements')
    elif isinstance(data_type, bool) and len(struct) != 1:
      raise SimulatorException(f'Malformed {name}.{key}: Must be a tuple with 1 elements')

  @property
  def assets(self):
    """ Return the assets """
    return self.__assets