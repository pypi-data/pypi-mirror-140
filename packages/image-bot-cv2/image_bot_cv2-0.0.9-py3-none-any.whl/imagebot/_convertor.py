import cv2


def convert_images(image, ref, convert_2_gray: bool):
    _image = image.copy()
    _ref = ref.copy()
    if len(_image.shape) <= 2 or len(_ref.shape) <= 2 or convert_2_gray:
        # image / ref are gray
        if len(_image.shape) > 2:
            _image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
        if len(_ref.shape) > 2:
            _ref = cv2.cvtColor(_ref, cv2.COLOR_BGR2GRAY)
    else:
        _image_channel = _image.shape[2]
        _ref_channel = _ref.shape[2]
        if _image_channel != _ref_channel:
            # make sure the image color depth are the same
            _image = cv2.cvtColor(_image, cv2.COLOR_BGRA2BGR)
            _ref = cv2.cvtColor(_ref, cv2.COLOR_BGRA2BGR)
    return _image, _ref
