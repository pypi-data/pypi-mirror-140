import struct


class InterruptPacket:
    length = (0, 1)
    descriptor_type = (1, 1)
    endpoint_address = (2, 1)
    attributes = (3, 1)
    max_packet_size = (4, 2)
    interval = (6, 1)


class GenericContainer:
    _container_length = (0, 4, "<I")
    _container_type = (4, 2, "<H")
    _code = (6, 2, "<H")
    _transaction_id = (8, 4, "<I")
    _payload = 12

    _container_types = {
        0: 'undefined',
        1: 'Command block',
        2: 'Data block',
        3: 'Response block',
        4: 'Event block',
    }

    def __init__(self, bs):
        self.bs = bs
        self.container_length = self.unpack_field(self._container_length)
        self.container_type = self.unpack_field(self._container_type)
        self.code = self.unpack_field(self._code)
        self.transaction_id = self.unpack_field(self._transaction_id)
        self.payload = self.bs[self._payload:]

    def get_container_type(self):
        try:
            return self._container_types[self.container_type[0]]
        except KeyError:
            return 'reserved'

    def unpack_field(self, field):
        s = self.bs[field[0]: field[0] + field[1]]
        return struct.unpack(field[2], s)

    @property
    def event_id(self):
        if self.payload:
            return struct.unpack("<I", self.payload[:4])[0]
