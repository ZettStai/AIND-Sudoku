assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
d1_units = [[s+t for s,t in zip(rows,cols)]]
d2_units = [[s+t for s,t in zip(rows,cols[::-1])]]
unitlist = row_units + column_units + square_units + d1_units + d2_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    no_more_twins = False
    # We have to iterate through all units until there are no more twins to be found. The way we do that is to compare the board before
    # and after the naked twins detection. If the board is the same then no new twins have been found. We have to do it in a while loop
    # because we might uncover new twins when possible values are removed from peers

    while not no_more_twins:
        board_before = values

        # Find all instances of naked twins

        # we select all the boxes which have length of their digits equal to 2

        twins = [box for box in values.keys() if len(values[box]) == 2]

        # We can create a dictionary here for more efficient implementation

        # dictionary:
        #  keys: two-digit box values
        #  values: lists of boxes containing exactly these digits
        # if we have exact two matches (not triplets or more) and the values are the same then we have a naked twin

        #If two squares within the same unit contain only
        #the same two digits, both digits can be eliminated from all the other squares in that unit
        nakedtwins = [[a,b] for a in twins for b in peers[a] if set(values[a])==set(values[b]) ]

        # Eliminate the naked twins as possibilities for their peers

        #for every naked twin find common peers
        for i in range(len(nakedtwins)):
            a = nakedtwins[i][0] #key for first twin

            twinvalue = (values[a]) #value of shared twin number

            b = nakedtwins[i][1] #key for the second twin

            commonpeers = set(peers[a]) & set(peers[b])
            # for each box in the unit which is not one of the two naked twins remove the possible values

            for c in commonpeers:
            #c is the key for commonpeer; values[c] is for remaining possibilities within peer
            #For every commonpeer check to see if
            #  length is not = to 1 to exclude solved peers
                if len(values[c]) != 1:
                    #pos is the pointer to integer in remaining possibilities within peer
                    for pos in values[c]:
                        #com is the pointer to integer in twinvalue
                        for com in twinvalue:
                            #Check to see if value from remaining possibilities matches twinvalue
                            if pos == com:
                                #Remove that value from remaining possibilities within peer
                                values[c] = values[c].replace(pos,'')

        board_after = values

        # if boards before and after naked twin detection are the same then there are no more twins thus we end the while loop
        if board_before == board_after:
            no_more_twins = True

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    allnum = '123456789'
    for i in grid:
        if i=='.':
            values.append(allnum)
        elif i in allnum:
            values.append(i)
    #Test that values is still the expected 81 characters
    assert len(values) == 81

    # Return new dictionary with changes from . to numbers

    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """ 
    Eliminate solved values from peers
    
    Args: 
        values(dict): The sudoku in dictionary form
    Returns:
        The dictionary representation of the reduced sudoku grid. 
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')

    return values

def only_choice(values):
    """ 
    Applies only choice strategy

    Args: 
        values(dict): The sudoku in dictionary form
    Returns:
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """ 
    Applies 3 sudoku solving strategies (eliminate, only_choice, naked_twins
     until it stalls

    Args: 
        values(dict): The sudoku in dictionary form
    Returns:
        Updated values for sudoku board
    """

    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = (grid_values(grid))
    values = reduce_puzzle(values)
    values = search(values)

    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')