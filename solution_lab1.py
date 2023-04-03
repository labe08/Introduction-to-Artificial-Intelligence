import sys
import argparse

def read_state_space(state_description):
    with open(state_description, "r", encoding="UTF-8") as input_file:
        lines = input_file.read().splitlines()
        # remove lines with comment
        lines = [x for x in lines if not x.startswith("#")]
        initial_state = lines[0]
        final_state = lines[1].split(" ")
        transitions = {}
        for line in lines[2:]:
                states = line.split(": ")
                if len(states) == 2:
                    current_state = states[0]
                    next_states = states[1]
                    transitions[current_state] = next_states
        return initial_state, final_state, transitions
            
def BFS(state_description):
    initial_state, final_state, transitions = read_state_space(state_description)
    states_visited = set()
    states_open = [(initial_state,0,[])]
    print("# BFS")
    while states_open != []:
        current_state = states_open[0][0]
        current_cost = states_open[0][1]
        current_path = states_open[0][2]
        del states_open[0]
        if current_state not in states_visited:
            states_visited.add(current_state)
            current_path.append(current_state)
            if current_state in final_state:
                print("[FOUND_SOLUTION]: yes")
                print("[STATES_VISITED]: " + str(len(states_visited)))
                print("[PATH_LENGTH]: " + str(len(current_path)))
                print("[TOTAL_COST]: " + str(float(current_cost)))
                print("[PATH]: " + " => ".join(current_path))
                return 
            next_states = sorted(transitions[current_state].split(" "))
            for next_state in next_states:
                next_state, cost = next_state.split(",")
                if next_state in current_path: continue
                states_open.append( (next_state, current_cost+int(cost), current_path[:]) )
    print("[FOUND_SOLUTION]: no")
    return

def UCS(initial_state, final_state, transitions):
    states_visited = set()
    states_open = [(initial_state,0,[])]
    while states_open != []:
        current_state = states_open[0][0]
        current_cost = states_open[0][1]
        current_path = states_open[0][2]
        del states_open[0]
        if current_state not in states_visited:
            states_visited.add(current_state)
            current_path.append(current_state)
            if current_state in final_state:
                return states_visited, current_path, current_cost
            next_states = sorted(transitions[current_state].split(" "))
            for next_state in next_states:
                next_state, cost = next_state.split(",")
                if next_state in current_path: continue
                lo = 0
                hi = len(states_open)
                while lo < hi:
                    mid = (lo+hi)//2
                    if (states_open[mid][1] > current_cost+int(cost)) or (states_open[mid][1] == current_cost+int(cost) and states_open[mid][0] > next_state):
                        hi = mid
                    else:
                        lo = mid + 1
                states_open.insert(lo, (next_state, current_cost+int(cost), current_path[:]))

    return 0, 0, 0

def read_heuristics(heuristics_file):
    heuristics = {}
    with open(heuristics_file, "r", encoding="UTF-8") as input_file:
        lines = input_file.read().splitlines()
        for line in lines:
            state, heuristic = line.split(': ')
            heuristics[state] = heuristic
    return heuristics

def A_star(state_description, heuristics_file):
    initial_state, final_state, transitions = read_state_space(state_description)
    heuristics = read_heuristics(heuristics_file)
    states_visited = set()
    states_closed = []
    states_open = [(initial_state, 0, int(heuristics[initial_state]), [])]
    print("# A-STAR")
    while states_open != []:
        current_state = states_open[0][0]
        current_cost = states_open[0][1]
        current_heuristic = states_open[0][2]
        current_path = states_open[0][3]
        del states_open[0]
        states_closed.append((current_state, current_cost))
        states_visited.add(current_state)
        current_path.append(current_state)
        if current_state in final_state:
            print("[FOUND_SOLUTION]: yes")
            print("[STATES_VISITED]: " + str(len(states_visited)))
            print("[PATH_LENGTH]: " + str(len(current_path)))
            print("[TOTAL_COST]: " + str(float(current_cost)))
            print("[PATH]: " + " => ".join(current_path))
            return
        next_states = transitions[current_state].split(" ")
        for next_state in next_states:
            next_state, cost = next_state.split(",")
            h = heuristics[next_state]
            if len(states_open) == 0:
                states_open.append((next_state, float(cost) + current_cost, current_cost + float(cost) + float(heuristics[next_state]), current_path[:]))
            else:
                found = False
                add = True
                for i in range(len(states_open)):
                    if next_state == states_open[i][0] and (float(cost) + current_cost) > states_open[i][1]:
                        found = True
                        add = False
                        break
                    elif next_state == states_open[i][0] and (float(cost) + current_cost) < states_open[i][1]:
                        del states_open[i]
                        states_open.append((next_state, float(cost) + current_cost, current_cost + float(cost) + float(heuristics[next_state]), current_path[:]))
                        found = True
                        add = False
                        break
                x = 0
                if not found:
                    for i in range(len(states_closed)):
                        if next_state == states_closed[i][0]:
                            if (float(cost) + current_cost) < states_closed[i][1]:
                                del states_closed[i]
                                add = False
                                states_open.append((next_state, float(cost) + current_cost, current_cost + float(cost) + float(heuristics[next_state]), current_path[:]))
                                break
                            else: add = False
                if add:
                    states_open.append((next_state, float(cost) + current_cost, current_cost + float(cost) + float(heuristics[next_state]), current_path[:]))
        states_open = sorted(states_open, key=lambda x:(x[2],x[1],x[0]))
    print("[FOUND_SOLUTION]: no")
    return

def optimistic(state_description, heuristics_file):
    heuristics = read_heuristics(heuristics_file)
    initial_state, final_state, transitions = read_state_space(state_description)
    is_optimistic = True
    for state in sorted(heuristics.keys()):
        true_cost = UCS(state, final_state, transitions)[2]
        if float(heuristics[state]) <= true_cost:
            print(('[CONDITION]: [OK] h({}) <= h*: {} <= {}').format(state, float(heuristics[state]), float(true_cost)))
        else:
            is_optimistic = False
            print(('[CONDITION]: [ERR] h({}) <= h*: {} <= {}').format(state, float(heuristics[state]), float(true_cost)))
    if not is_optimistic:
        print('[CONCLUSION]: Heuristic is not optimistic.')
    else:
        print('[CONCLUSION]: Heuristic is optimistic.')
    return

def consistent(state_description, heuristics_file):
    heuristics = read_heuristics(heuristics_file)
    initial_state, final_state, transitions = read_state_space(state_description)
    is_consistent = True
    for state in sorted(heuristics.keys()):
        if transitions.get(state, "") == "": continue
        for child in sorted(transitions[state].split(" ")):
            parent, c = child.split(",")
            if float(heuristics[state]) <= (float(heuristics[parent]) + float(c)):
                print(('[CONDITION]: [OK] h({}) <= h({}) + c: {} <= {} + {}').format(state, parent, float(heuristics[state]), float(heuristics[parent]), float(c)))
            else:
                is_consistent = False
                print(('[CONDITION]: [ERR] h({}) <= h({}) + c: {} <= {} + {}').format(state, parent, float(heuristics[state]), float(heuristics[parent]), float(c)))
    if not is_consistent:
        print('[CONCLUSION]: Heuristic is not consistent.')
    else:
        print('[CONCLUSION]: Heuristic is consistent.')
    return

#main function
function_names = { "BFS" : BFS, "UCS" : UCS, "ASTAR" : A_star}
if len(sys.argv) > 2:
    parser = argparse.ArgumentParser()
    parser.add_argument('--alg', required=False)
    parser.add_argument('--ss', required=True)
    parser.add_argument('--h', required=False)
    parser.add_argument('--check-optimistic', required=False, action='store_true')
    parser.add_argument('--check-consistent', required=False, action='store_true')
    args = vars(parser.parse_args())

    state_description = args['ss']
    if args['alg'] is not None:
        function_to_call = args['alg'].upper()
        if function_to_call in function_names:
            if function_to_call == 'ASTAR':
                heuristics = args['h']
                function_names[function_to_call](state_description, heuristics)
            elif function_to_call == 'UCS':
                print("# UCS")
                initial_state, final_state, transitions = read_state_space(state_description)
                states_visited, path, cost = function_names[function_to_call](initial_state, final_state, transitions)
                if states_visited == 0 and path == 0 and cost == 0:
                    print("[FOUND_SOLUTION]: no")
                else:
                    print("[FOUND_SOLUTION]: yes")
                    print("[STATES_VISITED]: " + str(len(states_visited)))
                    print("[PATH_LENGTH]: " + str(len(path)))
                    print("[TOTAL_COST]: " + str(float(cost)))
                    print("[PATH]: " + " => ".join(path))
            else:
                function_names[function_to_call](state_description)
    elif(args['check_optimistic']):
        heuristics = args['h']
        optimistic(state_description, heuristics)
    elif(args['check_consistent']):
        heuristics = args['h']
        consistent(state_description, heuristics)
        
else:
    print("Error: Not enough arguments!")