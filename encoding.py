import numpy as np
import pandas as pd
import pm4py
from sklearn.preprocessing import LabelEncoder


#find maximum length any split can have the maximum length
def find_max_len(train,val,test):

    max_len = 0
    event_len = []
    for df in [train,val,test]:
        for seq in df:
            event_len.append(len(seq))
        if max(event_len) > max_len:
            max_len = max(event_len)
    return max_len


#encode data
def si_encoding(df,cases,max_len=None,option="prefix"):

    # Label encode to get integers
    le = LabelEncoder()
    le.fit(cases)
    result = [] 
    if option == "prefix":
        # Transform traces to integer-encoded sequences
        int_traces = [le.transform(trace) for trace in df["prefix"]]

        # One-hot encode
        num_classes = len(le.classes_)

        for event_seq in int_traces:
            result.append(one_hot(event_seq,num_classes,max_len))

        result = np.array(result)

    else:
        # One-hot encode
        num_classes = len(le.classes_)
        
        int_trace = le.transform(df["activity"])
        result = np.array(one_hot(int_trace,num_classes))
    
    

    return result, le

#function to one hot encode by index
def one_hot(event_seq,num_classes, max_len=None):
    
    #get event sequence
    event = np.eye(num_classes)[event_seq] 

    #only true for prefix
    if max_len is not None: 
        pad_len = max_len - len(event_seq)
        if pad_len >= 1:
            pad_zeros = np.zeros((pad_len,num_classes))
            event = np.append(pad_zeros,event,axis=0)
                                 
    return event