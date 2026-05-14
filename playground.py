import pm4py
from pm4py.objects.dfg.utils import dfg_utils

def get_enabled_activities(petri_net, initial_marking, final_marking, prefix):
    """
    Determines which activities are enabled in a Petri net given a prefix.

    :param petri_net: The Petri net object (discovered net)
    :param initial_marking: The initial marking of the Petri net
    :param initial_marking: The initial marking of the Petri net
    :param final_marking: The final marking of the Petri net
    :param prefix: A list of activities (strings) representing the incomplete execution
    :return: A set of enabled activities (strings)
    """
    from pm4py.objects.petri_net.obj import Marking

    # Clone the marking to avoid modifying the original
    current_marking = Marking(initial_marking)

    # Replay the prefix on the Petri net
    for activity in prefix:
        # Find the transition corresponding to the activity
        transitions = [t for t in petri_net.transitions if t.label == activity]
        if not transitions:
            raise ValueError(f"Activity '{activity}' not found in the Petri net.")

        transition = transitions[0]  # Assuming unique labels

        # Check if the transition is enabled
        enabled_transitions = [t for t in petri_net.transitions if all(
            current_marking[arc.source] >= arc.weight for arc in t.in_arcs)]
        if transition in enabled_transitions:
            # Fire transition manually by updating current marking
            for arc in transition.in_arcs:
                current_marking[arc.source] -= arc.weight
            for arc in transition.out_arcs:
                if arc.target in current_marking:
                    current_marking[arc.target] += arc.weight
                else:
                    current_marking[arc.target] = arc.weight
        else:
            raise ValueError(f"Activity '{activity}' is not enabled at this point in the prefix.")

    # Get the list of enabled transitions from the current marking
    enabled_transitions = [t for t in petri_net.transitions if all(
        current_marking[arc.source] >= arc.weight for arc in t.in_arcs)]

    # Return the labels of enabled transitions (activities)
    enabled_activities = {t.label for t in enabled_transitions if t.label is not None}

    return enabled_activities

def force_fire_transition(petri_net, marking, transition):
    """
    Force fires a transition in the Petri net, updating the marking regardless of whether it is enabled.

    :param petri_net: The Petri net object
    :param marking: The current marking (dict)
    :param transition: The transition to fire
    """
    # Consume tokens from input places
    for arc in transition.in_arcs:
        if arc.source in marking:
            marking[arc.source] -= arc.weight
            if marking[arc.source] < 0:
                marking[arc.source] = 0  # Ensure no negative tokens

    # Produce tokens in output places
    for arc in transition.out_arcs:
        if arc.target in marking:
            marking[arc.target] += arc.weight
        else:
            marking[arc.target] = arc.weight

    return marking

def get_dfg_probabilities(dfg, last_activity):
    """
    Given a directly-follows graph (DFG) and a last activity, returns the probabilities of each next activity.

    :param dfg: A directly-follows graph (DFG object from pm4py)
    :param last_activity: The last activity executed (string)
    :return: A dictionary where keys are next activities and values are their probabilities
    """
    # Get all outgoing edges from the last activity
    outgoing_edges = dfg_tools.get_outgoing_edges(dfg, last_activity)

    # Calculate the total frequency of outgoing edges
    total_count = sum(freq for _, freq in outgoing_edges.items())

    # Calculate probabilities for each next activity
    probabilities = {
        target: freq / total_count for target, freq in outgoing_edges.items()
    } if total_count > 0 else {}

    return probabilities

# Example usage for DFG:
# from pm4py.objects.dfg.importer import importer as dfg_importer
# dfg = dfg_importer.apply('path_to_dfg.json')
# last_activity = 'A'
# probabilities = get_dfg_probabilities(dfg, last_activity)
# print(probabilities)

def get_enabled_activities(petri_net, initial_marking, prefix):
    """
    Determines which activities are enabled in a Petri net given a prefix.

    :param petri_net: The Petri net object (discovered net)
    :param initial_marking: The initial marking of the Petri net
    :param final_marking: The final marking of the Petri net
    :param prefix: A list of activities (strings) representing the incomplete execution
    :return: A set of enabled activities (strings)
    """
    from pm4py.objects.petri_net.obj import Marking

    # Clone the marking to avoid modifying the original
    current_marking = Marking(initial_marking)

    # Replay the prefix on the Petri net
    for activity in prefix:
        # Find the transition corresponding to the activity
        transitions = [t for t in petri_net.transitions if t.label == activity]
        if not transitions:
            raise ValueError(f"Activity '{activity}' not found in the Petri net.")

        transition = transitions[0]  # Assuming unique labels

        # Check if the transition is enabled
        enabled_transitions = [t for t in petri_net.transitions if all(
            current_marking[arc.source] >= arc.weight for arc in t.in_arcs)]
        if transition in enabled_transitions:
            # Fire transition manually by updating current marking
            for arc in transition.in_arcs:
                current_marking[arc.source] -= arc.weight
            for arc in transition.out_arcs:
                if arc.target in current_marking:
                    current_marking[arc.target] += arc.weight
                else:
                    current_marking[arc.target] = arc.weight
        else:
            raise ValueError(f"Activity '{activity}' is not enabled at this point in the prefix.")

    # Get the list of enabled transitions from the current marking
    enabled_transitions = [t for t in petri_net.transitions if all(
        current_marking[arc.source] >= arc.weight for arc in t.in_arcs)]

    # Return the labels of enabled transitions (activities)
    enabled_activities = {t.label for t in enabled_transitions if t.label is not None}

    return enabled_activities

def get_enabled_activities_with_force(petri_net, initial_marking, prefix):
    """
    Determines which activities are enabled in a Petri net given a prefix. 
    If prefix contains an activitity whose transition is not enabled, the transition is forced.

    :param petri_net: The Petri net object (discovered net)
    :param initial_marking: The initial marking of the Petri net
    :param final_marking: The final marking of the Petri net
    :param prefix: A list of activities (strings) representing the incomplete execution
    :return: A set of enabled activities (strings)
    """
    from pm4py.objects.petri_net.obj import Marking

    # Clone the marking to avoid modifying the original
    current_marking = Marking(initial_marking)

    # Replay the prefix on the Petri net
    for activity in prefix:
        # Find the transition corresponding to the activity
        transitions = [t for t in petri_net.transitions if t.label == activity]
        if not transitions:
            raise ValueError(f"Activity '{activity}' not found in the Petri net.")

        transition = transitions[0]  # Assuming unique labels

        # Check if the transition is enabled
        enabled_transitions = [t for t in petri_net.transitions if all(
            current_marking[arc.source] >= arc.weight for arc in t.in_arcs)]
        if transition in enabled_transitions:
            # Fire transition manually by updating current marking
            for arc in transition.in_arcs:
                current_marking[arc.source] -= arc.weight
            for arc in transition.out_arcs:
                if arc.target in current_marking:
                    current_marking[arc.target] += arc.weight
                else:
                    current_marking[arc.target] = arc.weight
        else:
            print(f"Activity '{activity}' is not enabled. Forcing transition...")
            force_fire_transition(current_marking, transition)
        

    # Get the list of enabled transitions from the current marking
    enabled_transitions = [t for t in petri_net.transitions if all(
        current_marking[arc.source] >= arc.weight for arc in t.in_arcs)]

    # Return the labels of enabled transitions (activities)
    enabled_activities = {t.label for t in enabled_transitions if t.label is not None}

    return enabled_activities

def force_fire_transition(marking, transition):
    """
    Force fires a transition in the Petri net, updating the marking regardless of whether it is enabled.

    :param petri_net: The Petri net object
    :param marking: The current marking (dict)
    :param transition: The transition to fire
    """
    # Consume tokens from input places
    for arc in transition.in_arcs:
        if arc.source in marking:
            marking[arc.source] -= arc.weight
            if marking[arc.source] < 0:
                marking[arc.source] = 0  # Ensure no negative tokens

    # Produce tokens in output places
    for arc in transition.out_arcs:
        if arc.target in marking:
            marking[arc.target] += arc.weight
        else:
            marking[arc.target] = arc.weight

    return marking


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

log = pm4py.read_xes('Datasets/Log_Model1.xes') 

dfg, _, _ = pm4py.discover_dfg(log)

last_activity = 'D'

probabilities = get_dfg_probabilities(dfg, last_activity)

print(probabilities)