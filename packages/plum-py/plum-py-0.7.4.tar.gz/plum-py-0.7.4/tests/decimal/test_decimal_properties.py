"""Test decimal transform properties."""

from plum.decimal import DecimalX


class TestProperties:

    """Test with as many left to default as possible."""

    u16p1 = DecimalX("u16p1", 2, 1, "big", signed=False)

    def test_name(self):
        assert self.u16p1.name == "u16p1"

    def test_nbytes(self):
        assert self.u16p1.nbytes == 2

    def test_byteorder(self):
        assert self.u16p1.byteorder == "big"

    def test_signed(self):
        assert self.u16p1.signed is False

    def test_precision(self):
        assert self.u16p1.precision == 1
