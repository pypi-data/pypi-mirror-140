from mnapy import Utils


class KeyPair:
    def __init__(self, key: str = "", data: str = "") -> None:
        self.key = key
        self.data = data
        self.type = Utils.Utils.GetDataType(self.data)
