import numpy as np
def split_train_test_temporal(df, test_len, case_id, timestamp, mode):
    """
    Taken from: https://github.com/BrechtWts/SuffixTransformerNetwork/blob/main/Preprocessing/create_benchmarks.py

    Split the dataset in train and test set, applying strict temporal 
    splitting and debiasing the test set.

    Parameters
    ----------
    df : pd.DataFrame
        Event log to be preprocessed. 
    test_len : float
        Fraction of last occurring cases assigned to the test set in 
        the chronological train-test split. In the SuTraN paper, this 
        was set to 0.25 for all event logs. 
    case_id : str, optional
        Column name of column containing case IDs.
    timestamp : str
        Column name of column containing timestamps. Column Should be of 
        the datetime64 dtype.
    mode : {'preferred', 'workaround'}
        Manner in which the out-of-time train-test split is performed. 
        The 'preferred' split adheres the the approach adopted from 
        Weytjens et al, and hence, for cases containing 
        events both before and after the split point, the prefix-suffix 
        pairs for which the prefix contains at least one event after the 
        split point are assigned to the test set, while the other pairs 
        pertaining to these cases are discarded. 
        If `mode='workaround'`, prefix-suffix pairs derived from those 
        overlapping cases, and for which all prefix events occur before 
        the split point, are assigned to the training set, while other 
        pairs pertaining to these cases (i.e. pairs for which one or more 
        prefix events are recorded after the plit point) are discarded. 

        Consequently, for `mode='preferred'`, the training set will only 
        contain cases having ended before the split point, while for 
        `mode='workaround'`, the test set will only contain cases having 
        started after the split point. 

    Returns
    -------
    df_train : pd.DataFrame
        Cases assigned to the training set. Still contains complete 
        cases only. I.e. the cases should still be parsed into 
        training instances (prefix-suffix pairs). 
    df_test : pd.DataFrame
        Cases assigned to the test set. Still contains complete 
        cases only. I.e. the cases should still be parsed into 
        test instances (prefix-suffix pairs). 
    prefix_dict : dict 
        `first_prefix_dict` if `mode='preferred'`, `last_prefix_dict` if 
        `mode='workaround'`. 

        * `first_prefix_dict`: dictionary having case IDs of cases 
          intersecting with the split point / separation time, as keys, 
          and the (chronologically sorted) event index of the first event 
          occurring after separation time as values. This dictionary 
          is needed later on in the preprocessing pipeline, to discard 
          test set prefix-suffix pairs pertaining to prefixes containing 
          only events before separation time, and hence overlapping 
          with running training set cases. 

        * `last_prefix_dict`: dictionary having case IDs of cases 
          intersecting with the split point / separation time, as keys, 
          and the (chronologically sorted) event index of the last event 
          occurring before separation time as values. This dictionary 
          is needed later on in the preprocessing pipeline, to discard 
          training (and validation) set prefix-suffix pairs pertaining to 
          prefixes containing prefix events occurring after separation 
          time, and hence overlappign with test set case. 
    """

    case_starts_df = df.groupby(case_id)[timestamp].min()
    # Sort values puts the first starting case first, the last one last
    # .index.array gets the chronologically sorted list of cases, with 
    # since the case ids were the indices of the case_starts_df pd.series. 
    case_nr_list_start = case_starts_df.sort_values().index.array
    case_stops_df = df.groupby(case_id)[timestamp].max().to_frame()  

    ### TEST SET ###
    # case_nr_list_start chronologically ordered list of all cases. 
    first_test_case_nr = int(len(case_nr_list_start) * (1 - test_len))

    # Split point
    first_test_start_time = np.sort(case_starts_df.values)[first_test_case_nr]


    if mode=='preferred':
        # -----------------------------------------------------
        # List of all cases ending after separation time (`first_test_start_time`)
        test_case_ids_all = list(case_stops_df[case_stops_df[timestamp].values >= first_test_start_time].index)

        # List of all cases starting after separation time 
        test_case_ids_sa = list(case_nr_list_start[first_test_case_nr:])

        # List of cases that overlap. I.e. all cases ending after separation time 
        # but starting before it. For these cases in the test set, only 
        # the prefixes with at least one event after separation time can be 
        # contained within the final test set. 
        test_case_ids_overlap = list(set(test_case_ids_all)-set(test_case_ids_sa))

        # Retain in preliminary test set all cases that end after separation time. 
        df_test = df[df[case_id].isin(test_case_ids_all)].reset_index(drop=True).copy()

        train_case_ids = case_stops_df[case_stops_df[timestamp].values < first_test_start_time].index.array  # added values
        df_train = df[df[case_id].isin(train_case_ids)].reset_index(drop=True)

        # For overlapping test cases, derive dictionary of first prefix idx to be contained within 
        # the ultimate test set. 
        df_test_overlap = df_test[df_test[case_id].isin(test_case_ids_overlap)].copy().reset_index(drop=True)
        # Add event index column 
        df_test_overlap['evt_idx'] = df_test_overlap.groupby([case_id]).cumcount()
        # Get dataframe of only the events of those cases that occur after seperation time
        df_test_overlap_prefixes = df_test_overlap[df_test_overlap[timestamp].values>first_test_start_time].copy().reset_index(drop=True)
        # Only retain first row for each case 
        df_test_overlap_prefixes = df_test_overlap_prefixes.groupby(case_id, sort=False, as_index=False).first().reset_index(drop=True)
        # Deriving dictionary
        overlap_cases_list = list(df_test_overlap_prefixes[case_id])
        overlap_evt_ids = list(df_test_overlap_prefixes['evt_idx'])
        first_prefix_dict = dict(zip(overlap_cases_list, overlap_evt_ids))

        return df_train, df_test, first_prefix_dict
    elif mode=='workaround':
        # Dataframe containing for each case id the start timestamp 
        case_starts_df = df.groupby(case_id)[timestamp].min().to_frame()  
        # In test set: all cases that start at or after separation time 
        test_case_ids = list(case_starts_df[case_starts_df[timestamp].values >= first_test_start_time].index.array)
        df_test = df[df[case_id].isin(test_case_ids)].copy().reset_index(drop=True)

        # Training case ids: those cases that start before separation time
        train_case_ids_all = list(case_starts_df[case_starts_df[timestamp].values < first_test_start_time].index.array) # added values
        df_train = df[df[case_id].isin(train_case_ids_all)].copy().reset_index(drop=True)
        # -----------------------------------------------------
        # List of ids of all training cases that end before separation time
        train_case_ids_eb = list(case_stops_df[case_stops_df[timestamp].values < first_test_start_time].index.array)
        
        # List of ids of all training cases that start before, but end after, separation time
        train_case_ids_overlap = list(set(train_case_ids_all)-set(train_case_ids_eb))

        # Retaining only the training traces ending after separation time 
        df_train_overlap = df_train[df_train[case_id].isin(train_case_ids_overlap)].copy().reset_index(drop=True)
        # Adding zero-based event indices for each case 
        df_train_overlap['evt_idx'] = df_train_overlap.groupby([case_id]).cumcount()
        # Slicing out only those events that occur before separation time 
        df_train_overlap_prefixes = df_train_overlap[df_train_overlap[timestamp].values < first_test_start_time].copy().reset_index(drop=True)
        # Slicing out only the last event that occurred before separation 
        # time for each case
        df_train_overlap_prefixes = df_train_overlap_prefixes.groupby(case_id, sort=False, as_index=False).last().reset_index(drop=True)
        
        # Deriving dictionary
        last_prefix_dict = df_train_overlap_prefixes.set_index('case:concept:name')['evt_idx'].to_dict()


        return df_train, df_test, last_prefix_dict


def split_train_test_simple(df, test_ratio):
    """
    Split the dataset in train and test set, applying a simple random 
    split. 

    Parameters
    ----------
    df : pd.DataFrame
        Event log to be preprocessed. 
    test_ratio : float
        Fraction of cases assigned to the test set. 

    Returns
    -------
    df_train : pd.DataFrame
        Cases assigned to the training set. 
    df_test : pd.DataFrame
        Cases assigned to the test set. 
    """

    case_ids = df['case:concept:name'].unique()
    test_size = int(len(case_ids) * test_ratio)
    test_case_ids = case_ids[:test_size]
    train_case_ids = case_ids[test_size:]

    df_test = df[df['case:concept:name'].isin(test_case_ids)].copy().reset_index(drop=True)
    df_train = df[df['case:concept:name'].isin(train_case_ids)].copy().reset_index(drop=True)

    return df_train, df_test

def split_train_test_variant_based_sampling(df, test_ratio):
    """
    Split the dataset in train and test set, by aplying active control-flow based sampling.

    Parameters
    ----------
    df : pd.DataFrame
        Event log to be preprocessed. 
    test_ratio : float
        Fraction of variants used for sampling the test set.

    Returns
    -------
    df_train : pd.DataFrame
        Cases assigned to the training set. 
    df_test : pd.DataFrame
        Cases assigned to the test set. 
    """
    #import packages needed
    import pm4py, random

    # Gets a dictionary whose key is the variant and as value there is the list of case ids that share the variant
    variants_dictionary = pm4py.statistics.variants.log.get.get_variants_from_log_trace_idx(df)

    # Get number of variant for test set
    test_size = int(len(variants_dictionary) * test_ratio)

    # Get the variants for the test set randomly, and the remaining variants in the training set
    test_variants = random.sample(list(variants_dictionary.keys()), test_size)
    train_variants = [variant for variant in variants_dictionary.keys() if variant not in test_variants]

    # Get the cases corresponding to the training and the test set using the values of the dictionary pointing at the case ids
    test_case_ids = [case_id for variant in test_variants for case_id in variants_dictionary[variant]]
    train_case_ids = [case_id for variant in train_variants for case_id in variants_dictionary[variant]]

    # Get the cases corresponding to the training and the test set
    df_test = df[df['case:concept:name'].isin(test_case_ids)].copy().reset_index(drop=True)
    df_train = df[df['case:concept:name'].isin(train_case_ids)].copy().reset_index(drop=True)

    return df_train, df_test