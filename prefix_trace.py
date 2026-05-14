import numpy as np
import pandas as pd

def prefix_trace(df):
    group_cases = df.groupby("case_id")[["timestamp","activity"]].apply(lambda x:x)
    prefixes = []

    # Group by the case
    for case_id, group in group_cases.groupby(level='case_id'):
        events = group['activity'].tolist()
    
        # Create prefixes
        for i in range(1, len(events) + 1):
            prefix = events[:i]
            prefixes.append({'case_id': case_id, 'prefix': prefix})

    # Convert to DataFrame
    prefix_df = pd.DataFrame(prefixes)

    return prefix_df