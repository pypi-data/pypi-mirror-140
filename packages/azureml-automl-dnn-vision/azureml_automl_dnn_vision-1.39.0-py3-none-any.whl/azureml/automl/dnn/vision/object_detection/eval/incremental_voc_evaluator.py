# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Incremental VOC-style evaluation for object detection."""

import numpy as np

from typing import Any, Dict, List

from pycocotools import mask as pycoco_mask

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.object_detection.eval.map_computation_utils import map_score_voc_auc_np, \
    map_score_voc_11_point_metric_np


# Codes for TP, FP, other.
_TP_CODE, _FP_CODE, _OTHER_CODE = 1, 0, 2

# Constant to avoid division by 0.
EPSILON = 1E-9


logger = get_logger(__name__)


def _get_boxes_classes_maybe_scores(objects, get_scores):
    """
    Extract ground truth/predicted boxes, classes and possibly scores from input to `evaluate_batch()`.
    """

    if len(objects) > 0:
        # Get boxes and convert from xyxy to xywh format.
        boxes = np.array(objects[:, :4], copy=True)
        boxes[:, 2] -= boxes[:, 0]
        boxes[:, 3] -= boxes[:, 1]

        # Get classes.
        classes = objects[:, 4]

        # Get scores, if present.
        scores = objects[:, 5] if get_scores else None
    else:
        # No objects.
        boxes, classes = np.zeros((0, 4)), np.zeros((0, 1))
        scores = np.zeros((0, 1)) if get_scores else None

    return boxes, classes, scores


def _match_boxes(gt_boxes, is_crowd, predicted_boxes, predicted_scores, iou_threshold):
    """
    Match ground truth boxes with predicted boxes based on IOU and predicted scores.

    Assign a label (TP/FP/other) to each predicted box.

    :param gt_boxes: Ground truth boxes.
    :type gt_boxes: numpy.ndarray of shape (m, 4): (pixel x1, y1, w, h)
    :param is_crowd: Whether the ground truth boxes represent crowd objects.
    :type is_crowd: numpy.ndarray of shape (m)
    :param predicted_boxes: Predicted boxes.
    :type predicted_boxes: numpy.ndarray of shape (n, 4): (pixel x1, y1, w, h)
    :param predicted scores: Predicted scores.
    :type predicted_scores: numpy.ndarray of shape (n)
    :param iou_threshold: Threshold for deciding whether two boxes match.
    :type iou_threshold: float
    :return: A TP/FP/other label for predicted boxes.
    :rtype: numpy.ndarray of shape (n) with int codes
    """

    # Get the number of ground truth and predicted objects.
    m, n = len(gt_boxes), len(predicted_boxes)

    # Initialize the tp_fp_labels for predictions to all false positives.
    tp_fp_labels = _FP_CODE * np.ones((n,), dtype=np.uint8)
    if (m == 0) or (n == 0):
        # All false positives (n > 0, m=0) or no predictions (n=0, m does not matter).
        return tp_fp_labels

    # Calculate an nxm matrix of IOUs for the predicted boxes and ground truth boxes.
    ious = pycoco_mask.iou(predicted_boxes, gt_boxes, is_crowd)

    # Calculate the indexes that sort the predicted objects descending by score and the index of the ground truth
    # object with the highest IOU given a predicted object.
    predicted_indexes = np.argsort(predicted_scores)[::-1]
    gt_indexes_max = np.argmax(ious, axis=1)

    # TODO: investigate alternative assignments: from ground truth boxes to predicted boxes, Hungarian.

    # Assign predicted boxes to ground truth boxes greedily: go through predicted objects in decreasing order of
    # scores and for each object assign the ground truth object with highest IOU with it.
    gt_assigned = np.zeros((m,), dtype=bool)
    for predicted_index, gt_index in zip(predicted_indexes, gt_indexes_max[predicted_indexes]):
        # Check that the IOU is above the threshold.
        if ious[predicted_index, gt_index] >= iou_threshold:
            # Check that ground truth object is not marked as crowd.
            if not is_crowd[gt_index]:
                # Check that the ground truth object has not been assigned to a predicted object yet.
                if not gt_assigned[gt_index]:
                    # The predicted object is true positive. Mark the ground truth object as assigned.
                    tp_fp_labels[predicted_index] = _TP_CODE
                    gt_assigned[gt_index] = True
            else:
                # The predicted object is neither true positive nor false positive.
                tp_fp_labels[predicted_index] = _OTHER_CODE

    return tp_fp_labels


def _calculate_pr_metrics(m, tp_fp_labels, scores, use_voc_11_point_metric, undefined_value):
    """
    Calculate AP, highest recall and precision at highest recall given TP/FP labels and scores for predictions.

    :param m: Number of ground truth objects.
    :type m: int
    :param tp_fp_labels: Labels for predicted objects.
    :type tp_fp_labels: numpy.ndarray
    :param scores: Scores for predicted objects.
    :type scores: numpy.ndarray
    :param use_voc_11_point_metric: Whether to use the 11 point computation style.
    :type use_voc_11_point_metric: bool
    :return: mAP, highest recall, precision@highest recall.
    :rtype: dict with precision, recall, mAP
    """

    # Get the number of predicted objects.
    n = len(tp_fp_labels)

    # If there are no ground truth objects and no predicted objects, AP, precision and recall are undefined.
    if (m == 0) and (n == 0):
        return {
            MetricsLiterals.AVERAGE_PRECISION: undefined_value,
            MetricsLiterals.PRECISION: undefined_value,
            MetricsLiterals.RECALL: undefined_value
        }
    # If there are no ground truth objects but predicted objects exist, AP and recall are undefined and precision is 0.
    if m == 0:
        return {
            MetricsLiterals.AVERAGE_PRECISION: undefined_value,
            MetricsLiterals.PRECISION: 0.0,
            MetricsLiterals.RECALL: undefined_value
        }
    # If ground truth objects exist but there are no predicted objects, AP and recall are 0 and precision is undefined.
    if n == 0:
        return {
            MetricsLiterals.AVERAGE_PRECISION: 0.0,
            MetricsLiterals.PRECISION: undefined_value,
            MetricsLiterals.RECALL: 0.0
        }

    # Sort the predictions decreasing by score and count the true positives and the false positives for each score
    # threshold.
    indexes = np.argsort(scores)
    labels_sorted_by_score_desc = tp_fp_labels[indexes[::-1]]
    cum_tp = np.cumsum(labels_sorted_by_score_desc == _TP_CODE)
    cum_fp = np.cumsum(labels_sorted_by_score_desc == _FP_CODE)

    # Calculate the precision and the recall values for each score threshold.
    precisions = cum_tp / (cum_tp + cum_fp + EPSILON)
    recalls = cum_tp / m

    # Calculate the area under the PR curve.
    if use_voc_11_point_metric:
        average_precision = map_score_voc_11_point_metric_np(precisions, recalls)
    else:
        average_precision = map_score_voc_auc_np(precisions, recalls)

    # TODO: add F1 score.
    return {
        MetricsLiterals.AVERAGE_PRECISION: average_precision,
        MetricsLiterals.PRECISION: precisions[-1],
        MetricsLiterals.RECALL: recalls[-1],
    }


class IncrementalVocEvaluator:
    """
    Incremental VOC-style evaluation for object detection.

    Suggested flow: make new object at beginning of evaluation, call `evaluate_batch()` after each batch, and
    eventually call `compute_metrics()` to get the final evaluation results.
    """

    # Min and max allowed values for the IOU threshold parameter used to decide whether a predicted box matches a
    # ground truth box.
    MIN_IOU_THRESHOLD = 0.1
    MAX_IOU_THRESHOLD = 1.0

    # Constant to mark undefined metric value.
    UNDEFINED_METRIC_VALUE = -1.0

    def __init__(self, num_classes: int, iou_threshold: float):
        """
        Construct an incremental VOC-style evaluator.

        :params num_classes: The number of classes in the dataset.
        :type num_classes: int
        :params iou_threshold: IOU threshold used when matching ground truth boxes with predicted boxes.
        :type iou_threshold: float
        """

        # Copy the number of classes.
        self._num_classes = num_classes

        # Validate the IOU threshold value.
        self._iou_threshold = self._validate_iou_threshold(iou_threshold)

        # Set the type of AP computation to its default value.
        self._use_voc_11_point_metric = False

        # Initialize per class lists for the number of ground truth objects, the predicted object label (TP/FP/other),
        # the predicted object score.
        self._num_gt_objects_per_class = {i: 0 for i in range(num_classes)}
        self._tp_fp_labels_per_class = {i: [np.zeros((0,), dtype=np.uint8)] for i in range(num_classes)}
        self._scores_per_class = {i: [np.zeros((0,))] for i in range(num_classes)}

    def evaluate_batch(
        self,
        gt_objects_per_image: List[np.array],
        predicted_objects_per_image: List[np.array],
        meta_info_per_image: List[Dict[str, Any]],
    ) -> None:
        """
        Compute necessary statistics for evaluating the object detections in the images of a batch.

        No metric values computed directly, just per-class statistics that can be aggregated after running for all
        batches.

        :param gt_objects_per_image: Ground truth objects for each image.
        :type gt_objects_per_image: list of numpy.ndarray of shape (n, 5): (pixel x1, y1, x2, y2, class)
        :param predicted_objects_per_image: Predicted objects for each image.
        :type predicted_objects_per_image: list of numpy.ndarray of shape (n, 6): (pixel x1, y1, x2, y2, class, score)
        :param meta_info_per_image: Meta information for each image.
        :type meta_info_per_image: list of dict's that have "iscrowd" key
        """

        # Go through each image and evaluate its predictions.
        for i, (gt_objects, predicted_objects, meta_info) in enumerate(
            zip(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)
        ):
            # Get the ground truth boxes and classes for the current image.
            gt_boxes, gt_classes, _ = _get_boxes_classes_maybe_scores(gt_objects, get_scores=False)

            # Get the crowd labels of the ground truth boxes for the current image.
            is_crowd = np.array(meta_info["iscrowd"]).astype(bool)

            # Get the predicted boxes, classes and scores for the current image.
            predicted_boxes, predicted_classes, predicted_scores = _get_boxes_classes_maybe_scores(
                predicted_objects, get_scores=True
            )

            # Evaluate the predictions for the current image.
            self._evaluate_image(gt_boxes, gt_classes, is_crowd, predicted_boxes, predicted_classes, predicted_scores)

    def compute_metrics(self) -> Dict[str, Any]:
        """
        Compute metrics for all the batches seen so far.

        This aggregates the necessary statistics computed for each batch.

        :return: mAP, highest recall, precision at highest recall + per label AP, highest recall and precision at
            highest recall.
        :rtype: dict with precision, recall, mAP and per_label_metrics keys
        """

        # Initialize the per class metrics to empty.
        metrics_per_class = {}

        # Go through each class and calculate the metrics for its objects (e.g. AP).
        for c in range(self._num_classes):
            # Get the labels and scores of predicted objects across all images.
            tp_fp_labels = np.concatenate(self._tp_fp_labels_per_class[c])
            scores = np.concatenate(self._scores_per_class[c])

            # Calculate metrics for the kept objects.
            metrics_per_class[c] = _calculate_pr_metrics(
                self._num_gt_objects_per_class[c],
                tp_fp_labels,
                scores,
                self._use_voc_11_point_metric,
                self.UNDEFINED_METRIC_VALUE
            )

        # Calculate the mean over all classes for the last precision, last recall and AP (=>mAP) metrics.
        return {
            MetricsLiterals.PER_LABEL_METRICS: metrics_per_class,
            MetricsLiterals.PRECISION: self._calculate_metric_mean_over_classes(
                metrics_per_class, MetricsLiterals.PRECISION
            ),
            MetricsLiterals.RECALL: self._calculate_metric_mean_over_classes(
                metrics_per_class, MetricsLiterals.RECALL
            ),
            MetricsLiterals.MEAN_AVERAGE_PRECISION: self._calculate_metric_mean_over_classes(
                metrics_per_class, MetricsLiterals.AVERAGE_PRECISION
            ),
        }

    def _validate_iou_threshold(self, iou_threshold):
        """
        Make the iou threshold value sane if it's not.

        :param iou_threshold: Arbitrary IOU threshold value.
        :type iou_threshold: float
        :return: Validated IOU threshold value.
        :rtype: float
        """

        if (iou_threshold < self.MIN_IOU_THRESHOLD) or (iou_threshold > self.MAX_IOU_THRESHOLD):
            logger.info(
                "Clamping IOU threshold for validation to [{}, {}] interval.".format(
                    self.MIN_IOU_THRESHOLD, self.MAX_IOU_THRESHOLD
                )
            )

        return max(self.MIN_IOU_THRESHOLD, min(self.MAX_IOU_THRESHOLD, iou_threshold))

    def _evaluate_image(self, gt_boxes, gt_classes, is_crowd, predicted_boxes, predicted_classes, predicted_scores):
        """
        Compute necessary statistics for evaluating the objects predicted in an image.

        The computation is done separately for each class. The statistics are: number of ground truth objects,
        TP/FP/other labels for predictions, scores for predictions.

        :param gt_boxes: Ground truth boxes for an image.
        :type gt_boxes: numpy.ndarray of shape (m, 4): (pixel x1, y1, w, h)
        :param gt_classes: Classes for the ground truth boxes for an image.
        :type gt_classes: numpy.ndarray of shape (m, 1)
        :param is_crowd: Crowd attribute for the ground truth boxes for an image.
        :type is_crowd: numpy.ndarray of shape (m, 1)
        :param predicted_boxes: Predicted boxes for an image.
        :type predicted_boxes: numpy.ndarray of shape (n, 4): (pixel x1, y1, w, h)
        :param predicted_classes: Classes for the predicted boxes for an image.
        :type predicted_classes: numpy.ndarray of shape (n, 1)
        :param predicted_scores: Scores for the predicted boxes for an image.
        :type predicted_scores: numpy.ndarray of shape (n, 1)
        """

        # Go through each class and extract the statistics necessary to evaluate the predictions for that class.
        for c in range(self._num_classes):
            # Get masks for the ground truth and the predicted objects for the current class.
            gt_mask_class = gt_classes == c
            predicted_mask_class = predicted_classes == c

            # Using both box coordinates and scores, match the predicted boxes with the ground truth boxes for the
            # current class. Assign a label of TP/FP/other to each prediction based on the match.
            tp_fp_labels = _match_boxes(
                gt_boxes[gt_mask_class],
                is_crowd[gt_mask_class],
                predicted_boxes[predicted_mask_class],
                predicted_scores[predicted_mask_class],
                self._iou_threshold
            )

            # Update for the current class: a. the number of ground truth boxes; b. the list of tp/fp/other labels; c.
            # the list of scores.
            self._num_gt_objects_per_class[c] += np.sum(~is_crowd[gt_mask_class])
            self._tp_fp_labels_per_class[c].append(tp_fp_labels)
            self._scores_per_class[c].append(predicted_scores[predicted_mask_class])

    def _calculate_metric_mean_over_classes(self, metrics_per_class, metric_name):
        """
        Average a metric's values over all classes.

        :param metrics_per_class: PR metrics by class.
        :type metrics_per_class: dict from int to PR metrics
        :param metric_name: One of the PR metrics, eg. "precision".
        :type metric_name: str
        :return: Mean metric value.
        :rtype: float
        """

        # Get the list of values of a metric across classes.
        values = [metrics_per_class[c][metric_name] for c in range(self._num_classes)]

        # Calculate the mean of valid values.
        valid_values = [v for v in values if v != self.UNDEFINED_METRIC_VALUE]
        average_value = sum(valid_values) / (len(valid_values) + EPSILON)

        return average_value
