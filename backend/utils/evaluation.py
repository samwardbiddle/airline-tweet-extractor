def evaluate_extraction(true_labels, predicted_labels):
    """Calculate accuracy of airline extraction."""
    correct = sum(set(pred) == set(true) for pred, true in zip(predicted_labels, true_labels))
    return correct / len(true_labels)
