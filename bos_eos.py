import numpy as np
import pandas as pd

def add_bos_eos_target(target,portion=None):
    
    cases = target["case_id"].unique()
    last_idx = target.index.max()
    temp_df = target.copy()
    for case in cases:
        
        if portion == "prefix":
            #create bos record for case, use all caps so its the lowest value timestamp is updated by 1sec
            first_time = target[target["case_id"] == case]["timestamp"].min() 
            bos_time = first_time - pd.Timedelta(seconds=1)
            last_idx += 1
            bos = pd.DataFrame({"timestamp":[bos_time],"activity":["BOS"],"case_id":[case]},index = [last_idx])
            temp_df = pd.concat([temp_df,bos])

        else:
            #create eos record for case,use z so that label encoder gives it highest value timestamp is updated by 1sec
            last_time = target[target["case_id"] == case]["timestamp"].max()
            eos_time = last_time + pd.Timedelta(seconds=1)
            last_idx += 1
            eos = pd.DataFrame({"timestamp":[eos_time],"activity":["zos"],"case_id":[case]}, index = [last_idx])
            temp_df = pd.concat([temp_df,eos])

    #sort by case id and timestamp
    temp_df = temp_df.sort_values(by=["case_id","timestamp"])
    temp_df = temp_df.reset_index(drop=True)
    
    return temp_df