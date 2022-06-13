import sys
from collections import deque

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, words in self.domains.items():  # Iterate over all variables and their words
            wordstoremove = set()  # Store words that will be removed from the variable's potential words
            for word in words:
                if len(word) != variable.length:  # If word is not of the same length as the variable can hold, add to set wordstoremove
                    wordstoremove.add(word)
            # Subtract the words that are unsuitable from variable's domain
            self.domains[variable] = words.difference(wordstoremove)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False  # Set revised to false to set an initial state
        overlap = self.crossword.overlaps[x, y]  # Find the overlap between two nodes and put them in a grid they share.

        if overlap:
            v1, v2 = overlap
            x_domains_to_remove = set()  # store all x domains to remove
            for x_i in self.domains[x]:
                overlaps = False  # Check if x variable overlaps with y variable.
                for y_j in self.domains[y]:
                    if x_i != y_j and x_i[v1] == y_j[v2]:
                        overlaps = True
                        break
                if not overlaps:  # if there is no overlap add x_i to the set of domains to remove.
                    x_domains_to_remove.add(x_i)
            if x_domains_to_remove:  # If thera are x values to remove, remove them.
                self.domains[x] = self.domains[x].difference(x_domains_to_remove)
                revised = True  # Set that a revision has been made

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:  # If there are no arcs add a queue with all edges.
            arcs = deque()
            for v1 in self.crossword.variables:
                for v2 in self.crossword.neighbors(v1):
                    arcs.appendleft((v1, v2))
        else:  # Is there are arcs add them to deque
            arcs = deque(arcs)

        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):  # Revise combination of edges
                # If there are no variables for x arc consistency is impossible
                if len(self.domains[x]) == 0:
                    return False
                # Check all x neighbours except those for y and add the edges between them and x to the queue
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.appendleft((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check all variables in the crossword
        for variable in self.crossword.variables:
            # If a variable is not in the assignment return False
            if variable not in assignment.keys():
                return False
            # If a variable is in the assignment but the word assigned to it not in the list of available words return False
            if assignment[variable] not in self.crossword.words:
                return False
        # Otherwise return True
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var_x, word_x in assignment.items():
            if var_x.length != len(word_x):  # Check if the assigned word fits also the length of x variable.
                return False

            for var_y, word_y in assignment.items():
                if var_x != var_y:
                    # Check if word assigned to x is unique
                    if word_x == word_y:
                        return False

                    # Check if the variables have an overlap.
                    overlap = self.crossword.overlaps[var_x, var_y]  # Return values in which x and y overlap.
                    if overlap:  # If the overlap exists check that it's the same character
                        a, b = overlap
                        if word_x[a] != word_y[b]:  # If the characters are not equal return an inconsistency
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Find neighbours of a given variable
        neighbors = self.crossword.neighbors(var) 
        # Check over the assignment and see if neighbour variables are assigned to a word.
        for variable in assignment:
            # If the variable is in the assignment and in neighbours already has a value.
            if variable in neighbors:
                neighbors.remove(variable)
        # Result list that will be stored considering heuristic least constraint values
        result = []
        for variable in self.domains[var]:
            take_out = 0  # Counter of how many domain options will be taked out from neighboring variables
            for neighbor in neighbors:
                for variable_2 in self.domains[neighbor]:
                    overlap = self.crossword.overlaps[var, neighbor]

                    # If there is overlap between variables one of them cannot have the domai
                    if overlap:
                        a, b = overlap
                        if variable[a] != variable_2[b]:
                            take_out += 1
            # Add the variable with the number of options it will take out from its neighbors
            result.append([variable, take_out])
        # Sort the list of variables by taken out domains they eliminate
        result.sort(key=lambda x: x[1])
        return [i[0] for i in result]  # Return the list of variables which have not been taken out

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree and any of these variables are acceptable return values.
        """
        # List of variables with heuristics minimum remain value and degree.
        
        potential_vars = []
        for variable in self.crossword.variables:  # Check all the variables in the crossword
            # If variable is not assigned add it to potential vars with number of domain options and minimum remainig value and the number of neighbours degree.
            if variable not in assignment:  
                potential_vars.append([variable, len(self.domains[variable]), len(self.crossword.neighbors(variable))])

        # Check potential vars by number of domain options, ascending, and number of neighbours, descending.
        
        if potential_vars:
            potential_vars.sort(key=lambda x: (x[1], -x[2]))
            return potential_vars[0][0]

        # Return None if thrre is no potential vars.
        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If the assignment is already complete return the assignment
        if self.assignment_complete(assignment): return assignment

        # Check an unassigned variable to choose its word
        variable = self.select_unassigned_variable(assignment)

        # Check all values in the domain that are sorted with heuristics leats constraint values.
        for value in self.order_domain_values(variable, assignment):
            assignment[variable] = value
            # If in the assignment all words are unique and overlaps are of same chars.
            if self.consistent(assignment):
                # Recursive method call to check if values are consitent.
                result = self.backtrack(assignment)
                if result:  # If the results are correct then the variable works.
                    return result

                # If the results are incorrect remove variable from assignment.
                assignment.pop(variable, None)

        # Return None if the variable does not fit with the assignment
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
