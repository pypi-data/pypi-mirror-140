import cv2
from typing import List
from ._results import MatchingResult


class BaseMatcher:
    def __init__(
        self, image_path: str, template_path: str, convert_2_gray: bool = True
    ):
        self.image_path = image_path
        self.template_path = template_path
        self.image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
        assert self.image is not None, "Image should not be None"
        assert self.template is not None, "Image template should not be None"
        self.h_image, self.w_image = self.image.shape[:2]
        self.h_template, self.w_template = self.template.shape[:2]
        assert (
            self.h_image >= self.h_template and self.w_image >= self.w_template
        ), "Image template should be smaller than image source."
        self.convert_2_gray = convert_2_gray

    def find_best_result(self) -> MatchingResult:
        """
        TODO
        """

    def find_all_results(self) -> List[MatchingResult]:
        """
        TODO
        """
