import os
import tempfile
import cv2
import numpy as np
from typing import Union, List
from ._convertor import convert_images
from ._base_matcher import BaseMatcher
from ._results import MatchingResult


class FeatureMatcher(BaseMatcher):
    _MAX_RATIO = 0.5

    def find_all_results(self) -> List[MatchingResult]:
        result = self.find_best_result()
        return [result] if result is not None else []

    def _feature_match(self):
        # Initiate SIFT detector
        sift = cv2.SIFT_create()
        # find the key points and descriptors with SIFT
        _image, _template = convert_images(
            self.image, self.template, self.convert_2_gray
        )
        kp_image, desc_image = sift.detectAndCompute(_image, None)
        kp_template, desc_template = sift.detectAndCompute(_template, None)
        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(desc_template, desc_image, k=2)
        # Apply ratio test
        match_pts = []

        def _get_good_matches(r):
            _good_pts = []
            for m, n in matches:
                if m.distance < r * n.distance:
                    _good_pts.append(m)
            return _good_pts

        ratio = 0.4
        while ratio < 0.75:
            match_pts = _get_good_matches(ratio)
            if len(match_pts) > 0:
                break
            else:
                ratio = ratio + 0.001
        return match_pts, kp_image, kp_template, ratio

    def find_best_result(self) -> Union[MatchingResult, None]:
        match_pts, kp_image, kp_template, _ = self._feature_match()
        h, w = self.h_template, self.w_template
        is_homography_ret_none = False
        if len(match_pts) >= 4:
            # Draw a polygon around the recognized object
            src_pts = np.float32(
                [kp_template[m.queryIdx].pt for m in match_pts]
            ).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_image[m.trainIdx].pt for m in match_pts]).reshape(
                -1, 1, 2
            )
            # Get the transformation matrix
            M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if M is not None:
                # Find the perspective transformation to get the corresponding points
                pts = np.float32(
                    [[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]
                ).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                points = np.int32(dst).tolist()
                center_x = int(sum([p[0][0] for p in points]) / len(points))
                center_y = int(sum([p[0][1] for p in points]) / len(points))
                max_x = int(max(max([p[0][0] for p in points]), 0))
                min_x = int(max(min([p[0][0] for p in points]), 0))
                max_y = int(max(max([p[0][1] for p in points]), 0))
                min_y = int(max(min([p[0][1] for p in points]), 0))
                result = MatchingResult(
                    center=(center_x, center_y), rect=((min_x, max_y), (max_x, min_y))
                )
                new_ratio = self._cal_feature_ratio(result)
                return result if new_ratio < self._MAX_RATIO else None
            else:
                is_homography_ret_none = True
        if len(match_pts) > 0 or is_homography_ret_none:
            points = [kp_image[m.trainIdx].pt for m in match_pts]
            center_x = int(sum([x for x, y in points]) / len(points))
            center_y = int(sum([y for x, y in points]) / len(points))
            result = MatchingResult(
                center=(center_x, center_y),
                rect=(
                    (max(int(center_x - w / 2), 0), int(center_y + h / 2)),
                    (int(center_x + w / 2), max(int(center_y - h / 2), 0)),
                ),
            )
            new_ratio = self._cal_feature_ratio(result)
            return result if new_ratio < self._MAX_RATIO else None
        else:
            return None

    def _cal_feature_ratio(self, result: MatchingResult) -> float:
        """
        re-calculate the first matched image rect with original template
        """
        (min_x, max_y), (max_x, min_y) = result.rect
        matched_img = self.image[min_y:max_y, min_x:max_x]
        same_size_matched_img = None
        try:
            if len(matched_img) > 0:
                same_size_matched_img = cv2.resize(
                    matched_img,
                    self.template.shape[:2][::-1],
                    interpolation=cv2.INTER_NEAREST,
                )
        except Exception as e:
            print(f"Convert matched image with error: {e}")
        if same_size_matched_img is not None:
            with tempfile.TemporaryDirectory() as d:
                matched_img_path = os.path.join(d, "tmp_matched_img.png")
                cv2.imwrite(matched_img_path, same_size_matched_img)
                feature_matcher = FeatureMatcher(
                    self.template_path, matched_img_path, self.convert_2_gray
                )
                _, _, _, ratio = feature_matcher._feature_match()
                return ratio
        else:
            return 1
