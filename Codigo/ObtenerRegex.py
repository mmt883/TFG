import networkx as nx
import re

def dfa_to_regex_aux(dfa, start_state, final_states):
    G = dfa.copy()  # Use the provided MultiDiGraph directly
    
    new_start = "q_start"
    new_final = "q_final"
    
    # Add new start state
    G.add_node(new_start)
    G.add_edge(new_start, start_state, label='ε')
    
    # Add new final state
    G.add_node(new_final)
    for f in final_states:
        G.add_edge(f, new_final, label='')
    
    states = list(G.nodes())
    states.remove(new_start)
    states.remove(new_final)
    
    # State elimination method
    for state in states:
        incoming = {}  # Maps source states to regex expressions
        for u, _, data in G.in_edges(state, data=True):
            incoming.setdefault(u, []).append(data['label'])
        
        outgoing = {}  # Maps destination states to regex expressions
        for _, v, data in G.out_edges(state, data=True):
            outgoing.setdefault(v, []).append(data['label'])
        
        self_loops = [data['label'] for u, v, data in G.edges(state, data=True) if u == v]
        loop_regex = f"({ '|'.join(self_loops) })*" if self_loops else ""
        
        for u, r1_list in incoming.items():
            for v, r2_list in outgoing.items():
                combined_r1 = f"({'|'.join(r1_list)})" if len(r1_list) > 1 else r1_list[0]
                combined_r2 = f"({'|'.join(r2_list)})" if len(r2_list) > 1 else r2_list[0]
                new_label = f"{combined_r1}{loop_regex}{combined_r2}" if loop_regex else f"{combined_r1}{combined_r2}"
                G.add_edge(u, v, label=new_label)
        
        G.remove_node(state)
    
    regex = [data['label'] for _, v, data in G.edges(new_start, data=True) if v == new_final]
    return f"({'|'.join(regex)})" if len(regex) > 1 else regex[0] if regex else "∅"


def dfa_to_regex(dfa, start_state, final_states):
    
    out = dfa_to_regex_aux(dfa, start_state, final_states)

    # Filtrar el símbolo ε
    # Elimina ε si no está seguido por |
    filtered_out = re.sub(r'ε(?!\|)', '', out)

    return filtered_out

if re.match("SM1SM1SM1", "SM1SM1"):
    print("Valid identifier")