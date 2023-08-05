# -*- coding: utf-8 -*-
"""
Python extension module for process mainloop support.

"""


import bowyer.signal


cdef int step  = 0
cdef int reset = 1


# -----------------------------------------------------------------------------
def run_with_retry(tup_node):
    """
    Repeatedly step the specified nodes in order, resetting if needed.

    """
    cdef object iter_signal
    while True:

        # Reset nodes.
        #
        iter_signal = _call(function = reset,
                            tup_node = tup_node)

        for signal in bowyer.signal.exit:
            if signal in iter_signal:
                return signal

        for signal in bowyer.signal.reset:
            if signal in iter_signal:
                continue

        # Main loop
        #
        while True:

            iter_signal = _call(function = step,
                                tup_node = tup_node)

            for signal in bowyer.signal.exit:
                if signal in iter_signal:
                    return signal

            for signal in bowyer.signal.reset:
                if signal in iter_signal:
                    break


# -----------------------------------------------------------------------------
cdef object _call(object function, object tup_node):
    """
    Call the specified function once on each node.

    """
    cdef object accumulator = list()
    cdef object iter_signal

    for node in tup_node:

        if function == step:
            iter_signal = node.step()
        elif function == reset:
            iter_signal = node.reset()
        else:
            iter_signal = (bowyer.signal.exit_ex_immediate,)

        for signal in bowyer.signal.immediate:
            if signal in iter_signal:
                return (signal,)

        for signal in iter_signal:
            if signal in bowyer.signal.controlled:
                accumulator.append(signal)

    if accumulator:
        return tuple(accumulator)
    else:
        return tuple()

