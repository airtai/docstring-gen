from tempfile import TemporaryDirectory

with TemporaryDirectory() as d:
    !ls -la {d}
