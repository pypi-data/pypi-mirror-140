
from typing import List
from picsellia.types.prediction_format import PredictionFormat


class SegmentationPredictionFormat(PredictionFormat):

    def __init__(self, label_ids : List[int], boxes : List[List[int]], detection_scores : List[float]):
        self.label_ids = label_ids
        self.boxes = boxes
        self.detection_scores = detection_scores
        self.check_validity()

    def check_validity(self) -> bool:
        assert isinstance(self.label_ids, List[int]), "Labels shall be a list of integer. Each one represening a label in labelmap"
        assert isinstance(self.boxes, List[List[int]]), "Boxes shall be a List of List of integer values."
        assert isinstance(self.detection_scores, List[int]), "Scores shall be a List of float values."

        for box in self.boxes:
            assert len(box) > 0, "One box is empty"

        for score in self.detection_scores:
            assert score >= 0, "Score shall be positive values"

    def to_oracle_payload(self) -> dict:
        self.check_validity()
        return {
            "labels": self.label_ids,
            "detection_scores": self.detection_scores,
            "boxes": self.boxes
        }