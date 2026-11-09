from sklearn.metrics import accuracy_score, precision_score, classification_report
import pandas as pd


true_labels_file = "true_labels.csv"
predicted_labels_file = "predicted_labels.csv"


y_true = pd.read_csv(true_labels_file)["label"]
y_pred = pd.read_csv(predicted_labels_file)["label"]

print("True Labels: ", y_true.head())
print("Predicted Labels: ", y_pred.head())


accuracy = accuracy_score(y_true, y_pred)
print(f"Accuracy: {accuracy:.2f}")

precision = precision_score(y_true, y_pred, average="binary")
print(f"Precision: {precision:.2f}")


print("Classification Report:")
print(classification_report(y_true, y_pred))
