import usb.core
from .constants import LMX_EVENT_ID, RESPONSE_CODES
from .ptp import GenericContainer

VENDOR_ID = 0x04da
PRODUCT_ID = 0x2382  # Panasonic G9

# TODO: Figure out what each of these do
_SUFFIX = 0x000010809404000100000010

SINGLE_SHOT = _SUFFIX.to_bytes(12, 'little') + \
              LMX_EVENT_ID.LMX_DEF_LIB_TAG_REC_CTRL_RELEASE_ONESHOT.value.to_bytes(4, 'little')


class Camera:
    def __init__(self, product_id=PRODUCT_ID, vendor_id=VENDOR_ID):
        self._device = usb.core.find(idProduct=product_id, idVendor=vendor_id)
        self._configuration = self._device.get_active_configuration()
        self._device.set_configuration(self._configuration)
        self._device.reset()
        self._transaction_id = 0x00000001

    @property
    def interface(self):
        return self._configuration.interfaces()[0]

    @property
    def endpoints(self):
        return self.interface.endpoints()

    def inc_count(self):
        self._transaction_id += 1
        if self._transaction_id > 0xffffffff:
            self._transaction_id = 0x00000001

    def snap(self):
        self.inc_count()
        self.endpoints[0].write(SINGLE_SHOT)

    def read(self, timeout=0):
        resp = self.endpoints[1].read(self.endpoints[1].wMaxPacketSize if timeout < 1 else timeout)
        return GenericContainer(resp.tobytes())

    def write(self, data):
        return self.endpoints[0].write(data)

    def set_iso(self, iso):
        self.inc_count()

        length = 0x10000000.to_bytes(4, 'big')
        container_type = 0x0100.to_bytes(2, 'big')
        code = 0x0394.to_bytes(2, 'big')
        transaction_id = self._transaction_id
        event_id = (LMX_EVENT_ID.LMX_DEF_LIB_EVENT_ID_ISO.value + 1).to_bytes(4, 'little')

        data = length + container_type + code + transaction_id.to_bytes(4, 'little') + event_id
        self.write(data)
        # FIXME: Figure out the purpose of 0x0400
        self.write(data + b'\x04\00' + b'\x00\x00' + int(iso).to_bytes(2, 'little') + b'\x00\x00')

        return self.read()

    def set_aperture(self, aperture):
        self.inc_count()
        a = int(aperture * 10)

        length = 0x10000000.to_bytes(4, 'big')
        container_type = 0x0100.to_bytes(2, 'big')

        code = 0x0394.to_bytes(2, 'big')
        transaction_id = self._transaction_id
        event_id = (LMX_EVENT_ID.LMX_DEF_LIB_EVENT_ID_APERTURE.value + 1).to_bytes(4, 'little')

        data = length + container_type + code + transaction_id.to_bytes(4, 'little') + event_id
        self.write(data)
        # FIXME: Figure out the purpose of 0x02000000
        self.write(data + b'\x02\x00\x00\x00' + a.to_bytes(2, 'little'))

        return self.read()

    def set_shutter_speed(self, ss):
        self.inc_count()
        # FIXME: Bulb and auto don't work yet on the g9
        if ss.lower() == 'bulb':
            ss = 0xFFFFFFFF
        elif ss.lower() == 'auto':
            ss = 0x0FFFFFFF
        else:
            split_ss = ss.split("/")
            if len(split_ss) == 1:
                ss = (int(ss) * 1000) + 0x8000000
            else:
                ss = int(split_ss[-1]) * 1000

        length = 0x18000000.to_bytes(4, 'big')
        container_type = 0x0200.to_bytes(2, 'big')

        code = 0x0394.to_bytes(2, 'big')
        transaction_id = self._transaction_id
        event_id = (LMX_EVENT_ID.LMX_DEF_LIB_EVENT_ID_SHUTTER.value + 1).to_bytes(4, 'little')
        data = length + container_type + code + transaction_id.to_bytes(4, 'little') + event_id
        self.write(data)
        # FIXME: Figure out the purpose of 0x04000000
        self.write(data + b'\x04\x00\x00\x00' + ss.to_bytes(4, 'little'))
        return self.read()

    # def call_init(self):
    #     self.write(b"\x0c\x00\x00\x00\x01\x00\x01\x10\x00\x00\x00\x00")
    #     return self.read()
