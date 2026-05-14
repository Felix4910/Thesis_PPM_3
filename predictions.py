import numpy as np
import pandas as pd
import pm4py
from sklearn.preprocessing import LabelEncoder

def cal_metrics(actual_label,predicted_labels):
  
    #macro accuracy
    true_positive = actual_label[actual_label == predicted_labels]
    macro_accuracy = true_positive.value_counts()/actual_label.value_counts()
    macro_accuracy_mean = macro_accuracy.mean()
    
    #micro accuracy
    micro_accuracy = true_positive.shape[0]/actual_label.shape[0]

    #set predicted label name
    predicted_labels = pd.Series(predicted_labels,name="Predicted")

    #set to data frame
    result = actual_label.groupby(predicted_labels).value_counts()
    result = result.reset_index()
    true_positive = result[result["activity"] == result["Predicted"]]
    true_positive = true_positive.reset_index()
    true_positive = true_positive.set_index("activity",drop=True)

    #macro recall
    fn = result[result["Predicted"] != result["activity"]]
    fn = fn.groupby("Predicted")["count"].sum()
    false_negative = fn.reset_index()
    false_negative = false_negative.set_index("Predicted",drop=True)
    recall = true_positive["count"]/(true_positive["count"] + false_negative["count"])
    macro_recall = recall.sum()/len(actual_label.unique())

    #macro precision
    result_actual = predicted_labels.groupby(actual_label).value_counts()
    result_actual = result_actual.reset_index()
    fp = result_actual[result_actual["activity"] != result_actual["Predicted"]]
    fp = fp.groupby("activity")["count"].sum()
    false_positive = fp.reset_index()
    false_positive = false_positive.set_index("activity",drop=True)
    precision = true_positive["count"]/(true_positive["count"]+false_positive["count"])
    macro_precision = precision.sum()/len(actual_label.unique())

    return macro_accuracy_mean, recall, macro_recall, precision, macro_precision, micro_accuracy

def single_input_prediction(model,df,label_encoder):
    prediction = model.predict(df)
    indexes = prediction.argmax(axis=1)
    predicted_label = label_encoder.inverse_transform(indexes)
    return predicted_label

def multi_input_prediction(model,df_1,df_2,label_encoder):
    prediction = model.predict([df_1,df_2])
    indexes = prediction.argmax(axis=1)
    predicted_label = label_encoder.inverse_transform(indexes)
    return predicted_label