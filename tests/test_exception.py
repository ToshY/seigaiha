import pytest

from seigaiha.exception import InvalidViewBoxError, SvgToPngImageError


def test_invalid_view_box_error_message():
    with pytest.raises(InvalidViewBoxError) as exception_info:
        raise InvalidViewBoxError

    assert str(exception_info.value) == InvalidViewBoxError.ERROR_MESSAGE


def test_svg_to_png_image_error_formats_reason():
    with pytest.raises(SvgToPngImageError) as exception_info:
        raise SvgToPngImageError("out of memory")

    assert (
        str(exception_info.value) == "Cannot convert SVG to PNG. Reason: out of memory."
    )
