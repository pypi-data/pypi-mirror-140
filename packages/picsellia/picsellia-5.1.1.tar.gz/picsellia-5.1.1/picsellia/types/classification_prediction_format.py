
from picsellia.types.prediction_format import PredictionFormat


class ClassificationPredictionFormat(PredictionFormat):

    def __init__(self, label_id : int, score : float):
        self.label_id = label_id
        self.score = score
        self.check_validity()

    def check_validity(self) -> bool:
        assert isinstance(self.label_id, int), "Label of classification prediction shall be id in labelmap and should be an int"
        assert isinstance(self.score, float), "Score of classification prediction shall be a float"
        assert self.score >= 0, "Score shall be positive"

    def to_oracle_payload(self) -> dict:
        self.check_validity()
        return {
            "labels" : [self.label_id],
            "detection_scores" : [self.score]
        }