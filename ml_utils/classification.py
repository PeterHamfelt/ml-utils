"""Utilities for evaluting classification models."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    auc, average_precision_score, confusion_matrix,
    precision_recall_curve, r2_score, roc_curve
)

def confusion_matrix_visual(y_true, y_pred, class_labels, ax=None, title=None, **kwargs):
    """
    Create a confusion matrix heatmap to evaluate classification.

    Parameters:
        - y_test: The true values for y
        - preds: The predicted values for y
        - class_labels: What to label the classes.
        - ax: The matplotlib Axes object to plot on.
        - title: The title for the confusion matrix
        - kwargs: Additional keyword arguments for `seaborn.heatmap()`

    Returns:
        A confusion matrix heatmap.
    """
    mat = confusion_matrix(y_true, y_pred)
    axes = sns.heatmap(
        mat.T, square=True, annot=True, fmt='d',
        cbar=True, cmap=plt.cm.Blues, ax=ax, **kwargs
    )
    axes.set_xlabel('Actual')
    axes.set_ylabel('Model Prediction')
    tick_marks = np.arange(len(class_labels)) + 0.5
    axes.set_xticks(tick_marks)
    axes.set_xticklabels(class_labels)
    axes.set_yticks(tick_marks)
    axes.set_yticklabels(class_labels, rotation=0)
    axes.set_title(title or 'Confusion Matrix')
    return axes

def find_threshold(y_test, y_preds, fpr_below, tpr_above):
    """
    Find the threshold to use with `predict_proba()` for classification
    based on the maximum acceptable FPR and the minimum acceptable TPR.

    Parameters:
        - y_test: The actual labels.
        - y_preds: The predicted labels.
        - fpr_below: The maximum acceptable FPR.
        - tpr_above: The minimum acceptable TPR.

    Returns:
        The thresholds were the criteria are met.
    """
    fpr, tpr, thresholds = roc_curve(y_test, y_preds)
    return thresholds[(fpr <= fpr_below) & (tpr >= tpr_above)]

def plot_roc(y_test, preds, ax=None):
    """
    Plot ROC curve to evaluate classification.

    Parameters:
        - y_test: The true values for y
        - preds: The predicted values for y as probabilities
        - ax: The Axes to plot on

    Returns:
        Plotted ROC curve.
    """
    if not ax:
        fig, ax = plt.subplots(1, 1)
    fpr, tpr, thresholds = roc_curve(y_test, preds)
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='baseline')
    ax.plot(fpr, tpr, color='red', lw=2, label='model')
    ax.legend(loc='lower right')
    ax.set_title('ROC curve')
    ax.set_xlabel('False Positive Rate (FPR)')
    ax.set_ylabel('True Positive Rate (TPR)')
    ax.annotate(f'AUC: {auc(fpr, tpr):.2}', xy=(.43, .025))
    return ax

def plot_pr_curve(y_test, preds, positive_class=1):
    """
    Plot precision-recall curve to evaluate classification.

    Parameters:
        - y_test: The true values for y
        - preds: The predicted values for y as probabilities
        - positive_class: The label for the positive class in the data

    Returns:
        Plotted precision-recall curve.
    """
    precision, recall, thresholds = precision_recall_curve(y_test, preds)

    fig, axes = plt.subplots()

    axes.axhline(sum(y_test == positive_class)/len(y_test), color='navy', lw=2, linestyle='--', label='baseline')
    axes.plot(recall, precision, color='red', lw=2, label='model')

    axes.legend()
    axes.set_title(
        'Precision-recall curve\n'
        f""" AP: {average_precision_score(
            y_test, preds, pos_label=positive_class
        ):.2} | """
        f'AUC: {auc(recall, precision):.2}'
    )
    axes.set_xlabel('Recall')
    axes.set_ylabel('Precision')

    axes.set_xlim(-0.05, 1.05)
    axes.set_ylim(-0.05, 1.05)

    return axes

def plot_multi_class_roc(y_test, preds, ax=None):
    """
    Plot ROC curve to evaluate classification.

    Parameters:
        - y_test: The true values for y
        - preds: The predicted values for y as probabilities
        - ax: The Axes to plot on

    Returns:
        ROC curve.
    """
    if not ax:
        fig, ax = plt.subplots(1, 1)
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='baseline')
    class_labels = np.sort(y_test.unique())
    for i, class_label in enumerate(class_labels):
        actuals = np.where(y_test == class_label, 1, 0)
        predicted_probabilities = preds[:,i]
        fpr, tpr, thresholds = roc_curve(actuals, predicted_probabilities)
        auc_score = auc(fpr, tpr)
        ax.plot(fpr, tpr, lw=2, label=f"""class {class_label}; AUC: {auc_score:.2}""")
    ax.legend()
    ax.set_title('Multi-class ROC curve')
    ax.set_xlabel('False Positive Rate (FPR)')
    ax.set_ylabel('True Positive Rate (TPR)')
    return ax

def plot_multi_class_pr_curve(y_test, preds):
    """
    Plot precision-recall curve to evaluate classification.

    Parameters:
        - y_test: The true values for y
        - preds: The predicted values for y as probabilities

    Returns:
        Plotted precision-recall curve.
    """
    class_labels = np.sort(y_test.unique())

    row_count = np.ceil(len(class_labels) / 3).astype(int)
    fig, axes = plt.subplots(row_count, 3, figsize=(15, row_count*5))
    axes = axes.flatten()

    if len(axes) > len(class_labels):
        for i in range(len(class_labels), len(axes)):
            fig.delaxes(axes[i])

    for i, class_label in enumerate(class_labels):
        axes[i].axhline(sum(y_test == class_label)/len(y_test), color='navy', lw=2, linestyle='--', label='baseline')
        actuals = np.where(y_test == class_label, 1, 0)
        predicted_probabilities = preds[:,i]
        precision, recall, thresholds = precision_recall_curve(actuals, predicted_probabilities)
        auc_score = auc(recall, precision)
        ap_score = average_precision_score(actuals, predicted_probabilities)
        axes[i].plot(recall, precision, lw=2, label=f"""AUC: {auc_score:.2}; AP : {ap_score:.2}""")

        axes[i].legend()
        axes[i].set_title(f'Precision-recall curve: class {class_label}')
        axes[i].set_xlabel('Recall')
        axes[i].set_ylabel('Precision')

        axes[i].set_xlim(-0.05, 1.05)
        axes[i].set_ylim(-0.05, 1.05)

    return axes
