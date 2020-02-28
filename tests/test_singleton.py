import pytest
from flagship import Flagship


def test_flagship_singleton():
    fs = Flagship()
    fs.start("toto")
    fs2 = Flagship()
    fs2.start("titi")
    assert fs == fs2
    assert fs._config == fs2._config == "titi"
