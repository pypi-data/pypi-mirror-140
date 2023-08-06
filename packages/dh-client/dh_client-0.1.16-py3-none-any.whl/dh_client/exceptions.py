import pprint


class NotSupportedYet(Exception):
    pass


class FailedToEmmitMpc(Exception):
    def __int__(self, mpc, change_type):
        super().__init__(
            f"could not emmit the following MPC:\n{pprint.pformat(mpc)}\nchange type: {change_type}"
        )
