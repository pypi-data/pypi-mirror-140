# -*- coding: utf-8 -*-
"""
Bowyer component for printing data to a stream.

"""


import os.path
import pprint
import sys


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the pretty printer.

    """
    # Ensure any existing open files are closed.
    # (Ignore stdout and stderr)
    if 'stream' in state and not state['stream'].name.startswith('<std'):
        state['stream'].close()

    # Select the stream to use for output.
    state['stream'] = sys.stdout
    if 'output' in cfg:
        name_output = cfg['output']
        if name_output == 'stdout':
            state['stream'] = sys.stdout
        elif name_output == 'stderr':
            state['stream'] = sys.stderr
        else:
            filepath = name_output
            dirpath  = os.path.dirname(filepath)
            os.makedirs(dirpath, exist_ok = True)
            state['stream'] = open(filepath, 'wt')

    state['pretty'] = False
    if 'pretty' in cfg:
        state['pretty'] = cfg['pretty']

    state['path'] = list(list())
    if 'path' in cfg:
        for path in cfg['path']:
            state['path'].append(path.split('.'))
    else:
        for key in inputs.keys():
            state['path'].append([key])


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the pretty printer.

    """
    for list_items in inputs.values():
        for item in list_items:
            if state['pretty']:
                pprint.pprint(item, stream = state['stream'])
            else:
                print(item, file = state['stream'])
