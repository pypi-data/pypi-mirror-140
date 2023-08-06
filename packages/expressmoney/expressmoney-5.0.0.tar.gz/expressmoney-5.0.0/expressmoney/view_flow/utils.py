__all__ = ('fix_flow_signal', )


def fix_flow_signal(func):
    def _wrapper_fix_signal(self, **kwargs):
        kwargs.update({'self': self})
        func(**kwargs)

    return _wrapper_fix_signal
