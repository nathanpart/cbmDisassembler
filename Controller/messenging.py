"""
Provide a more universal messaging service than the signal system in urwid. By tying signals to a
class urwid prevents the ability of a listener to bind to a signal that could be emitted by multiple
widget classes.

For simplicity this class handles things by making the signal name itself the only identifier needed.

"""
import types
import weakref

callbacks = dict()
tokens = dict()


def register_message(msg_name):
    if not isinstance(msg_name, str):
        raise ValueError("Message name must be a string.")

    if msg_name in callbacks:
        raise ValueError("Message name {} is already registered.".format(msg_name))
    callbacks[msg_name] = list()
    tokens[msg_name] = 0


def connect_listener(msg_name, callback):
    if msg_name not in callbacks:
        raise ValueError("Message {} has not been registered.".format(msg_name))

    # noinspection PyTypeChecker
    if isinstance(callback, types.MethodType):
        tokens[msg_name] += 1
        callbacks[msg_name].append((weakref.WeakMethod(callback), tokens[msg_name]))
        return tokens[msg_name]
    elif isinstance(callback, types.FunctionType):
        tokens[msg_name] += 1
        callbacks[msg_name].append((weakref.ref(callback), tokens[msg_name]))
        return tokens[msg_name]
    else:
        raise ValueError('Callback not a function or a method')


def disconnect_listener(msg_name, token):
    if msg_name not in callbacks:
        raise ValueError("Message {} has not been registered.".format(msg_name))

    for i, (_, tok) in enumerate(callbacks[msg_name]):
        if tok == token:
            del callbacks[msg_name][i]


def change_listener(msg_name, token, new_callback):
    if msg_name not in callbacks:
        raise ValueError("Message {} has not been registered.".format(msg_name))

    for i, (_, tok) in enumerate(callbacks[msg_name]):
        if tok == token:
            # noinspection PyTypeChecker
            if isinstance(new_callback, types.MethodType):
                callbacks[msg_name].append((weakref.WeakMethod(new_callback), tokens[msg_name]))
                return
            elif isinstance(new_callback, types.FunctionType):
                callbacks[msg_name].append((weakref.ref(new_callback), tokens[msg_name]))
                return
            else:
                raise ValueError('Callback not a function or a method')
    raise ValueError("Token {} not found for Message {}".format(token, msg_name))


def send_message(msg_name, *args, **kwargs):
    if msg_name not in callbacks:
        raise ValueError("Message {} has not been registered.".format(msg_name))

    for i, (callback_wref, _) in enumerate(callbacks[msg_name]):
        if callback_wref() is not None:
            callback_wref()(*args, **kwargs)
        else:
            # callback got garbage collected so delete it
            del callbacks[msg_name][i]
