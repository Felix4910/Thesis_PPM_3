import numpy as np
import pandas as pd
import pm4py

#import dfg implementations
from discover_dfg import discover_dfg
from playout_probabilities_dfg import get_dfg_probabilities

def dfg_df(df_prefix,cases):

    #convert to train dataframe to log for dfg
    df_prefix = df_prefix.sort_values(by=["case_id","timestamp"])
    df_log = pm4py.format_dataframe(df_prefix,case_id="case_id",activity_key="activity",timestamp_key="timestamp")
    df_log = pm4py.convert_to_event_log(df_log)
    
    # Read playout
    dfg = discover_dfg(df_log)
    
    # Calculate probabilities from dfg
    probabilities = {}
    for activity in cases:
        probabilities[activity] = get_dfg_probabilities(dfg, activity)
        if len(probabilities[activity]) == 0:
            probabilities[activity] = {activity:0}
    
    #convert probabilities to dataframe
    probability = pd.DataFrame.from_dict(probabilities,orient="index")
    probability = probability.fillna(0)

    return probability