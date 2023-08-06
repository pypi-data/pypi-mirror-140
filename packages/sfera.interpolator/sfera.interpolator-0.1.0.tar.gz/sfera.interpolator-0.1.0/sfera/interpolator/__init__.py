import json
import pathlib


root = pathlib.Path(__file__).absolute().parent
metadata_path = root / 'metadata.json'
if metadata_path.exists():
    globals().update(json.loads(metadata_path.read_text()))
del json, pathlib, metadata_path


from .interpolator import Interpolator


__all__ = [
    'Interpolator',
]