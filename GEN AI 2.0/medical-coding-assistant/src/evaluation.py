"""
ML Evaluation Framework for Medical Coding Assistant
Comprehensive metrics for ICD-10 code prediction assessment
"""
from __future__ import annotations
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import math


class EvaluationMetrics:
    """Core evaluation metrics for ICD-10 predictions"""
    
    @staticmethod
    def top_k_accuracy(predicted_top_k: List[str], ground_truth: List[str], k: int = 1) -> float:
        """
        Top-K Accuracy: Percentage of cases where ground truth is in top-K predictions
        
        Formula: (# of correct predictions in top-K) / (total predictions)
        
        Example:
        - Ground truth: ['I21.11']
        - Predicted top-5: ['I21.11', 'I21.09', 'R07.9', 'I24.1', 'R06.02']
        - Top-1 Accuracy: 1.0 (correct at position 0)
        - Top-3 Accuracy: 1.0 (correct at position 0)
        """
        if not ground_truth:
            return 0.0
        
        correct = 0
        for gt_code in ground_truth:
            if gt_code in predicted_top_k[:k]:
                correct += 1
        
        return correct / len(ground_truth)

    @staticmethod
    def precision_at_k(predicted_top_k: List[str], ground_truth: List[str], k: int = 5) -> float:
        """
        Precision@K: Of the top-K predictions, what fraction are correct?
        
        Formula: (# correct in top-K) / K
        
        Useful for: Understanding quality of top-K results
        """
        if k == 0:
            return 0.0
        
        top_k_preds = predicted_top_k[:k]
        correct = sum(1 for pred in top_k_preds if pred in ground_truth)
        
        return correct / k

    @staticmethod
    def recall_at_k(predicted_top_k: List[str], ground_truth: List[str], k: int = 5) -> float:
        """
        Recall@K: Of all ground truth codes, what fraction appears in top-K?
        
        Formula: (# ground truth in top-K) / (# total ground truth)
        
        Useful for: Measuring coverage of correct codes
        """
        if not ground_truth:
            return 0.0
        
        top_k_preds = predicted_top_k[:k]
        correct = sum(1 for gt in ground_truth if gt in top_k_preds)
        
        return correct / len(ground_truth)

    @staticmethod
    def mean_reciprocal_rank(predicted_top_k: List[str], ground_truth: List[str]) -> float:
        """
        Mean Reciprocal Rank (MRR): Average inverse rank of first correct prediction
        
        Formula: 1/rank of first correct prediction
        
        Example:
        - Ground truth: ['I21.11']
        - Predicted: ['I21.09', 'I21.11', ...]
        - MRR = 1/2 = 0.5
        
        Useful for: Ranking quality (does model place correct code early?)
        """
        for idx, pred in enumerate(predicted_top_k, 1):
            if pred in ground_truth:
                return 1.0 / idx
        
        return 0.0  # No correct prediction found

    @staticmethod
    def coverage(all_predictions: List[List[str]], all_ground_truth: List[List[str]]) -> float:
        """
        Coverage: Percentage of predictions where at least one code is found
        
        Formula: (# predictions with ≥1 correct) / (# total predictions)
        
        Useful for: Measuring if system can make any correct prediction
        """
        if not all_predictions:
            return 0.0
        
        covered = 0
        for preds, gt in zip(all_predictions, all_ground_truth):
            if any(p in gt for p in preds):
                covered += 1
        
        return covered / len(all_predictions)

    @staticmethod
    def f1_score(predicted_top_k: List[str], ground_truth: List[str], k: int = 5) -> float:
        """
        F1 Score: Harmonic mean of Precision and Recall
        
        Formula: 2 * (Precision * Recall) / (Precision + Recall)
        
        Useful for: Balanced metric when both precision and recall matter
        """
        precision = EvaluationMetrics.precision_at_k(predicted_top_k, ground_truth, k)
        recall = EvaluationMetrics.recall_at_k(predicted_top_k, ground_truth, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)


class ConfusionMatrixHandler:
    """Handle confusion matrix at code-level and chapter-level aggregation"""
    
    def __init__(self):
        # Chapter-level confusion: (predicted_chapter, gt_chapter) -> count
        self.chapter_confusion = defaultdict(int)
        # Detailed: (predicted_code, gt_code) -> count (limited to frequent codes)
        self.code_confusion = defaultdict(int)
        self.code_counts = defaultdict(int)

    @staticmethod
    def get_icd10_chapter(code: str) -> str:
        """
        Extract ICD-10 chapter from code (first 3 characters)
        
        Examples:
        - 'I21.11' -> 'I' (Diseases of circulatory system)
        - 'J44.9' -> 'J' (Respiratory system)
        - 'R06.02' -> 'R' (Symptoms/signs)
        """
        return code[0] if code else "Unknown"

    def add_prediction(self, predicted_code: str, ground_truth_code: str):
        """Record a single prediction for confusion matrix"""
        pred_chapter = self.get_icd10_chapter(predicted_code)
        gt_chapter = self.get_icd10_chapter(ground_truth_code)
        
        # Chapter-level
        self.chapter_confusion[(pred_chapter, gt_chapter)] += 1
        self.code_counts[ground_truth_code] += 1
        
        # Code-level (only for frequent codes to manage size)
        if self.code_counts[ground_truth_code] >= 5:
            self.code_confusion[(predicted_code, ground_truth_code)] += 1

    def get_chapter_confusion_matrix(self) -> Dict[str, Dict[str, int]]:
        """
        Get chapter-level confusion matrix
        
        Returns matrix as nested dict:
        {predicted_chapter: {gt_chapter: count}}
        
        Why chapter-level?
        - 71,000+ unique ICD-10 codes make full matrix impractical
        - Chapter groups related conditions (circulatory, respiratory, etc.)
        - Reveals systematic confusion patterns
        """
        matrix = defaultdict(lambda: defaultdict(int))
        
        for (pred_ch, gt_ch), count in self.chapter_confusion.items():
            matrix[pred_ch][gt_ch] = count
        
        return dict(matrix)

    def get_top_confused_codes(self, top_n: int = 10) -> List[Tuple[str, str, int]]:
        """Get most confused code pairs"""
        sorted_pairs = sorted(
            self.code_confusion.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [(pred, gt, count) for (pred, gt), count in sorted_pairs[:top_n]]


class ErrorAnalysis:
    """Detailed error analysis and categorization"""
    
    class ErrorType:
        """Error type categories"""
        SEMANTIC_MISMATCH = "semantic_mismatch"  # Unrelated codes
        SYMPTOM_VS_DIAGNOSIS = "symptom_vs_diagnosis"  # Symptom code instead of diagnosis
        SEVERITY_CONFUSION = "severity_confusion"  # Different severity of same condition
        LOCATION_CONFUSION = "location_confusion"  # Different anatomical location
        TIMING_CONFUSION = "timing_confusion"  # Acute vs chronic confusion
        RARE_CODE_FAILURE = "rare_code_failure"  # Low-frequency code not predicted

    def __init__(self):
        self.errors = defaultdict(list)

    @staticmethod
    def categorize_error(predicted_code: str, gt_code: str, note_text: str) -> str:
        """
        Categorize prediction error
        
        Uses heuristics to classify why prediction was wrong
        """
        # Symptom codes: R00-R99
        is_pred_symptom = predicted_code[0] == 'R'
        is_gt_symptom = gt_code[0] == 'R'
        
        if is_pred_symptom and not is_gt_symptom:
            return ErrorAnalysis.ErrorType.SYMPTOM_VS_DIAGNOSIS

        # Check for severity indicators
        if predicted_code[0] == gt_code[0]:
            # Same chapter, likely same condition family
            if predicted_code[:3] == gt_code[:3]:
                # Same 3-char prefix
                return ErrorAnalysis.ErrorType.SEVERITY_CONFUSION
            else:
                return ErrorAnalysis.ErrorType.LOCATION_CONFUSION

        # Different chapters entirely
        return ErrorAnalysis.ErrorType.SEMANTIC_MISMATCH

    def record_error(self, predicted_code: str, gt_code: str, note_text: str):
        """Record an error for analysis"""
        error_type = self.categorize_error(predicted_code, gt_code, note_text)
        self.errors[error_type].append({
            "predicted": predicted_code,
            "ground_truth": gt_code,
            "note_length": len(note_text)
        })

    def get_error_summary(self) -> Dict[str, int]:
        """Get error category summary"""
        return {error_type: len(errors) for error_type, errors in self.errors.items()}


class EvaluationPipeline:
    """Complete evaluation pipeline for batch predictions"""
    
    def __init__(self):
        self.metrics_history = []
        self.confusion_handler = ConfusionMatrixHandler()
        self.error_analyzer = ErrorAnalysis()

    def evaluate_prediction(self, predicted_codes: List[str], 
                           ground_truth_codes: List[str],
                           note_text: str = "",
                           latency_ms: int = 0) -> Dict:
        """
        Evaluate a single prediction
        
        Returns comprehensive metrics for this prediction
        """
        metrics = {
            "top_1_accuracy": EvaluationMetrics.top_k_accuracy(predicted_codes, ground_truth_codes, k=1),
            "top_3_accuracy": EvaluationMetrics.top_k_accuracy(predicted_codes, ground_truth_codes, k=3),
            "top_5_accuracy": EvaluationMetrics.top_k_accuracy(predicted_codes, ground_truth_codes, k=5),
            "precision_at_5": EvaluationMetrics.precision_at_k(predicted_codes, ground_truth_codes, k=5),
            "recall_at_5": EvaluationMetrics.recall_at_k(predicted_codes, ground_truth_codes, k=5),
            "mrr": EvaluationMetrics.mean_reciprocal_rank(predicted_codes, ground_truth_codes),
            "f1_at_5": EvaluationMetrics.f1_score(predicted_codes, ground_truth_codes, k=5),
            "latency_ms": latency_ms,
            "is_correct": any(p in ground_truth_codes for p in predicted_codes)
        }

        # Update confusion matrix
        for gt in ground_truth_codes:
            if predicted_codes:
                self.confusion_handler.add_prediction(predicted_codes[0], gt)

        # Error analysis
        if metrics["is_correct"] == False and predicted_codes and ground_truth_codes:
            self.error_analyzer.record_error(predicted_codes[0], ground_truth_codes[0], note_text)

        self.metrics_history.append(metrics)
        return metrics

    def get_aggregate_metrics(self) -> Dict:
        """Get aggregate metrics across all evaluated predictions"""
        if not self.metrics_history:
            return {}

        n = len(self.metrics_history)
        aggregate = {
            "total_predictions": n,
            "avg_top_1_accuracy": sum(m["top_1_accuracy"] for m in self.metrics_history) / n,
            "avg_top_3_accuracy": sum(m["top_3_accuracy"] for m in self.metrics_history) / n,
            "avg_top_5_accuracy": sum(m["top_5_accuracy"] for m in self.metrics_history) / n,
            "avg_precision_at_5": sum(m["precision_at_5"] for m in self.metrics_history) / n,
            "avg_recall_at_5": sum(m["recall_at_5"] for m in self.metrics_history) / n,
            "avg_mrr": sum(m["mrr"] for m in self.metrics_history) / n,
            "avg_f1_at_5": sum(m["f1_at_5"] for m in self.metrics_history) / n,
            "avg_latency_ms": sum(m["latency_ms"] for m in self.metrics_history) / n,
            "correct_predictions": sum(1 for m in self.metrics_history if m["is_correct"]),
            "error_categories": self.error_analyzer.get_error_summary(),
            "chapter_confusion_matrix": self.confusion_handler.get_chapter_confusion_matrix(),
        }

        return aggregate
