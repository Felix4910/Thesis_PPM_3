import pm4py

def discover_dfg(log):
    """
    Discovers a Directly-Follows Graph (DFG) from an event log.

    :param log: The event log object
    :return: The Directly-Follows Graph (DFG) object
    """
    # 0 because we only want the DFG, not the start and end activities
    dfg = pm4py.discover_dfg(log)[0]
    return dfg 
