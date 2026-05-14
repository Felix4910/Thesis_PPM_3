def get_dfg_probabilities(dfg, last_activity):
    """
    Determines probabilities of outgoing activities from the given last activity in a DFG.

    :param dfg: The Directly-Follows Graph (DFG) object, a dictionary with edge tuples as keys and frequencies as values.
    :param last_activity: The last activity (string) from which outgoing edges are evaluated.
    :return: A dictionary with activities as keys and their probabilities as values.
    """
    # Filter outgoing edges from the last_activity
    outgoing_edges = {
        target: freq
        for (source, target), freq in dfg.items()
        if source == last_activity
    }

    # Sum the frequencies of outgoing edges
    total_frequency = sum(outgoing_edges.values())

    # Calculate probabilities
    if total_frequency > 0:
        probabilities = {
            target: freq / total_frequency
            for target, freq in outgoing_edges.items()
        }
    else:
        probabilities = {}  # No outgoing edges

    return probabilities
