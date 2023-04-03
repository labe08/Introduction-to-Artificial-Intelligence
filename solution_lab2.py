import sys

#read from input file
def read_clauses(clauses_file):
    with open(clauses_file, 'r', encoding='UTF-8') as input_file:
        lines = input_file.read().strip().splitlines()
        clauses = [x for x in lines if not x.startswith('#')]
        clauses_lower = []
        for clause in clauses:
            clause = clause.lower()
            clauses_lower.append(clause)
        return clauses_lower

#negate one simbol
def negate(simbol):
    if simbol.startswith('~'):
        return simbol[1:]
    else:
        return '~' + simbol

#remove valid
def remove_valid(clause):
    nonvalid = []
    for i in clause.split(' v '):
        if i not in nonvalid:
            nonvalid.append(i)
    returning_clause = []
    for n in nonvalid:
        if negate(n) in nonvalid:
            return []
        returning_clause.append(n)
    returning_clause = ' v '.join(returning_clause)
    return returning_clause

#resolve two clauses
def plResolve(a, b):
    resolvent = []
    clause = a
    if a != b:
        clause = clause + ' v ' + b
    for i in clause.split(' v '):
        if i not in resolvent:
            resolvent.append(i)
    returning_resolvents = []
    for r in resolvent:
        if not negate(r) in resolvent:
            returning_resolvents.append(r)
    if returning_resolvents == []: return []
    resolvent = ' v '.join(returning_resolvents)
    return resolvent

def check_if_exists(clause_to_check, existing_clauses):
    clause_to_check = clause_to_check.split(' v ')
    for clause in existing_clauses:
        clause = clause.split(' v ')
        if clause == clause_to_check:
            return True
    return False

def is_equal(clause1, clause2):
    clause1 = sorted(clause1.split(' v '))
    clause2 = sorted(clause2.split(' v '))
    if clause1 == clause2:
        return True
    return False

def turn_to_list(clause):
    return sorted(clause.split(' v '))

def save_in_order(clause):
    clause = ' v '.join(turn_to_list(clause))
    return clause

def derived_clauses(derived_from, clause, clauses_only, clauses, negated_goal):
    derived = []
    if clause in clauses_only or clause in negated_goal:
        return []
    else:
        parent1, parent2 = derived_from[clause]
        if parent1 not in clauses_only:
            derived.append(parent1)
            d = derived_clauses(derived_from, parent1, clauses_only, clauses, negated_goal)
            derived += d
        if parent2 not in clauses_only:
            derived.append(parent2)
            d = derived_clauses(derived_from, parent2, clauses_only, clauses, negated_goal)
            derived += d
    return derived

def refutation_resolution_algorithm(clauses):
    goal_clause = clauses[-1]
    clauses_only_mixed = clauses[:-1]
    negated_goal = []
    new = []
    goal_clause = sorted(goal_clause.split(' v '))
    for n in goal_clause:
        n = negate(n)
        negated_goal.append(n)
    negated_goal = sorted(negated_goal)
    negated_goal_string = ' v '.join(negated_goal)
    clauses_only = []
    for c in clauses_only_mixed:
        c = save_in_order(c)
        clauses_only.append(c)

    #check if goal is already in clauses and delete redundand parts
    clauses = []
    for clause in clauses_only:
        simple_clause = remove_valid(clause)
        if simple_clause in goal_clause:
            for k in range(len(clauses_only)):
                print(str(k+1) + '. ' + str(clauses_only[k]))
            print(str(len(clauses_only)+1) + '. ' + str(negated_goal_string))
            print('===============')
            return True
        elif simple_clause != []:
            clauses.append(simple_clause)
    derived_from = {}
    resolved_pairs = []

    #set of support strategy
    set_of_support = []
    set_of_support += negated_goal
    for i in range(len(negated_goal)):
        for j in range(len(clauses)):
            resolvents = plResolve(negated_goal[i], clauses[j])
            if resolvents == [] or (len(turn_to_list(resolvents)) > len(turn_to_list(negated_goal[i])) and len(turn_to_list(resolvents)) > len(turn_to_list(clauses[j]))): continue
            resolvents = save_in_order(resolvents)
            if not is_equal(negated_goal[i], clauses[j]) and (turn_to_list(negated_goal[i]), turn_to_list(clauses[j])) not in resolved_pairs:
                resolved_pairs.append((turn_to_list(negated_goal[i]), turn_to_list(clauses[j])))
            if not is_equal(negated_goal[i], resolvents) and (turn_to_list(negated_goal[i]), turn_to_list(resolvents)) not in resolved_pairs:
                resolved_pairs.append((turn_to_list(negated_goal[i]), turn_to_list(resolvents)))
            if not is_equal(clauses[j], resolvents) and (turn_to_list(clauses[j]), turn_to_list(resolvents)) not in resolved_pairs:
                resolved_pairs.append((turn_to_list(clauses[j]), turn_to_list(resolvents)))
            if not check_if_exists(resolvents, clauses_only):
                set_of_support.insert(0, resolvents)
                derived_from[resolvents] = (save_in_order(negated_goal[i]), save_in_order(clauses[j]))
    clauses = set_of_support + clauses

    while(True):
        #call plResolve for all pairs of clauses
        derived_from_temp = {}
        for i in range(len(set_of_support)):
            for j in range(len(clauses)):
                if (is_equal(set_of_support[i], clauses[j])) or ((turn_to_list(set_of_support[i]), turn_to_list(clauses[j])) in resolved_pairs) or ((turn_to_list(clauses[j]), turn_to_list(set_of_support[i])) in resolved_pairs): continue
                resolvents = plResolve(set_of_support[i], clauses[j])
                resolved_pairs.append((turn_to_list(set_of_support[i]), turn_to_list(clauses[j])))
                if resolvents == []:
                    derived_from['NIL'] = (save_in_order(set_of_support[i]), save_in_order(clauses[j]))
                    derived = derived_clauses(derived_from, 'NIL', clauses_only, clauses, negated_goal)
                    derived.insert(0, 'NIL')
                    clauses.insert(0, 'NIL')
                    #print original clauses + negated goal
                    counter = 1
                    for o in clauses_only:
                        print(str(counter) + '. ' + str(o))
                        counter += 1
                    print(str(counter) + '. ' + str(negated_goal_string))
                    counter += 1
                    print('===============')
                    #print derived clauses
                    for d in reversed(derived):
                        if d in derived_from.keys():
                            print(str(counter) + '. ' + str(d) + '\n ' + str(derived_from[d]))
                            counter += 1
                    return True
                if len(turn_to_list(resolvents)) > len(turn_to_list(set_of_support[i])) and len(turn_to_list(resolvents)) > len(turn_to_list(clauses[j])): continue
                resolvents = save_in_order(resolvents)
                resolved_pairs.append((turn_to_list(set_of_support[i]), turn_to_list(resolvents)))
                resolved_pairs.append((turn_to_list(clauses[j]), turn_to_list(resolvents)))
                if new == []:
                    new = [resolvents]
                    derived_from_temp[resolvents] = (save_in_order(set_of_support[i]), save_in_order(clauses[j]))
                else:
                    if not check_if_exists(resolvents, new):
                        new.insert(0, resolvents)
                        derived_from_temp[resolvents] = (save_in_order(set_of_support[i]), save_in_order(clauses[j]))
        
        subset = True
        for n in new:
            if not check_if_exists(n, clauses):
                clauses.insert(0, n)
                derived_from[n] = derived_from_temp[n]
                set_of_support.insert(0, n)
                subset = False

        if subset:
            for k in range(len(clauses_only)):
                print(str(k+1) + '. ' + str(clauses_only[k]))
            print(str(len(clauses_only)+1) + '. ' + str(negated_goal_string))
            print('===============')
            return False

def cooking_assistent(clauses, user_commands):
    for line in user_commands:
        command = line[-1]
        clause = line[:-2]
        if command == '-':
            if clause in clauses:
                clauses.remove(clause)
        elif command == '+':
            clauses.append(clause)
        elif command == '?':
            clauses.append(clause)
            if refutation_resolution_algorithm(clauses[:]):
                print('===============')
                print('[CONCLUSION]: ' + clauses[-1] + ' is true\n')
            else: print('[CONCLUSION]: ' + clauses[-1] + ' is unknown\n')
            clauses = clauses[:-1]
    return

#main function
if len(sys.argv) > 2:
    function = sys.argv[1]
    if function == 'resolution':
        if len(sys.argv) == 3:
            clauses_file = sys.argv[2]
            clauses = read_clauses(clauses_file)
            if refutation_resolution_algorithm(clauses[:]):
                print('===============')
                print('[CONCLUSION]: ' + clauses[-1] + ' is true')
            else: print('[CONCLUSION]: ' + clauses[-1] + ' is unknown')
        else:
            print('Error: Too many arguments!')
    elif function == 'cooking':
        if len(sys.argv) == 4:
            clauses_file = sys.argv[2]
            user_commands_file = sys.argv[3]
            clauses = read_clauses(clauses_file)
            user_commands = read_clauses(user_commands_file)
            cooking_assistent(clauses, user_commands)
        else:
            print('Error: Not enough arguments!')
else:
    print('Error: Not enough arguments!')