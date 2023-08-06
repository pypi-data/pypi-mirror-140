import importlib

try:
    importlib.import_module('not-exists')
except Exception as e:
    print(e, type(e))
