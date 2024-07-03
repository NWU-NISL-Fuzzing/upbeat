import re
import random



def array_max_process_1(input_code: str,count) -> str:
    """Handles the issue of quantum array exceeding maximum index, 
    e.g., use a=Qubit[2], but later q[2] causes an error"""

    def get_max_index_1(lines, variable_names):
        max_index = -1
        pattern = re.compile(r'({})\[(\d+)\]'.format('|'.join(variable_names)))
        for line in lines:
            matches = pattern.findall(line)
            for _, index in matches:
                max_index = max(max_index, int(index))
        return max_index

    lines = input_code.split('\n')

    new_lines = []
    for line in lines:
        match = re.search(r'use\s+([^=\s]+)\s*=\s*Qubit\[(\d+)\];', line)
        if match:
            var_name = match.group(1)
            old_size = int(match.group(2))

            alias_names = set()
            for alias_line in lines:
                alias_match = re.search(r'let\s+([^=\s]+)\s*=\s*{};'.format(var_name), alias_line)
                if alias_match:
                    alias_names.add(alias_match.group(1))

            alias_names.add(var_name)
            max_index = get_max_index_1(lines, alias_names)

            if max_index >= old_size:
                new_size = max_index + 1
                line = line.replace(match.group(0), f'use {var_name} = Qubit[{new_size}];')
                print(type(count))

                count += 1

        new_lines.append(line)

    return '\n'.join(new_lines), count


def get_max_index(lines, variable_names):
    """
    Finds the maximum index used in the code for the given variable names.

    Args:
        lines (list of str): The lines of code to be analyzed.
        variable_names (list of str): The list of variable names to check for indexing.

    Returns:
        int: The maximum index found.
    """

    max_index = -1
    num_pattern = re.compile(r'({})\[(\d+)\]'.format('|'.join(variable_names)))
    var_pattern = re.compile(r'({})\[(\w+)\]'.format('|'.join(variable_names)))
    # First, find direct number indices
    for line in lines:
        matches = num_pattern.findall(line)
        for _, index in matches:
            max_index = max(max_index, int(index))
    # Then, find variable indices and get their values from the code
    for line in lines:
        matches = var_pattern.findall(line)
        for _, var in matches:
            # Search for the variable value across ALL lines, not just the current line
            for search_line in lines:
                var_value_match = re.search(r'(let|mutable)\s+{}\s*=\s*(\d+);'.format(var), search_line)
                if var_value_match:
                    var_value = int(var_value_match.group(2))
                    max_index = max(max_index, var_value)
                    break  # Break once we find the value for this variable
    return max_index


def array_max_process(input_code: str, count) -> str:
    """
    Adjusts the size of quantum arrays and updates variable assignments to prevent out-of-bound errors.

    Args:
        input_code (str): The input code containing quantum array declarations and usage.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted array sizes and variable assignments.
        int: The updated counter of modifications made.
    """
     
    lines = input_code.split('\n')
    new_lines = []
    for line in lines:
        match = re.search(r'use\s+([^=\s]+)\s*=\s*Qubit\[(\d+)\];', line)
        if match:
            var_name = match.group(1)
            old_size = int(match.group(2))
            
            alias_names = set([var_name])
            max_index = get_max_index(lines, alias_names)

            if max_index >= old_size:
                for idx, l in enumerate(lines):
                    var_replacements = re.findall(r'(let|mutable)\s+(\w+)\s*=\s*(\d+);', l)
                    for _, var, value in var_replacements:
                        if int(value) >= old_size:
                        
                            count = count + 1
                            lines[idx] = l.replace(f'{var} = {value}', f'{var} = {old_size-1}')

    return '\n'.join(lines), count

def modify_input_code(input_code: str,count) -> str:

    """
    Modifies the input code to handle specific cases where quantum arrays are indexed with extreme values.

    Args:
        input_code (str): The input code containing variable declarations and quantum array usage.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted variable assignments.
        int: The updated counter of modifications made.
    """

    lines = input_code.split('\n')
    new_lines = []

    for line in lines:
        # Check for patterns like 'mutable A = 2^63-1;' or 'mutable A = -2^63-1;'
        mutable_match = re.search(r'mutable\s+(\w+)\s*=\s*(2\^63-1|-2\^63-1);', line)
        if mutable_match:
            var_name = mutable_match.group(1)

            # Check if there exists a line with 'use B = Qubit[A];'
            for use_line in lines:
                if re.search(r'use\s+\w+\s*=\s*Qubit\[' + var_name + r'\];', use_line):
                    # Modify the mutable line
                    line = f'mutable {var_name} = 10;'
                    count = count+1
                    break

        new_lines.append(line)

    return '\n'.join(new_lines),count


def array_negative_numbers(test_case: str, count) -> str:
    """
    Handles negative numbers in quantum arrays by replacing them with non-negative values.

    Args:
        test_case (str): The input code containing array and variable declarations.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted array and variable declarations.
        int: The updated counter of modifications made.
    """

    if "wrong" not in test_case :
        lines = test_case.split('\n')
        modified_lines = []
    
        variables_to_modify = set()
        variables_to_modify_let = set()
        # Identify mutable variables with negative values
        for line in lines:
            mutable_match = re.match(r'^\s*mutable\s+(\w+)\s*=\s*(-\d+(\.\d+)?);', line)
            if mutable_match:
                variable_name = mutable_match.group(1)
                variables_to_modify.add(variable_name)
            # Identify let variables dependent on mutable variables
            let_match = re.match(r'^\s*let\s+(\w+)\s*=\s*(\w+);', line)
            if let_match:
                variable_name = let_match.group(1)
                dependent_variable_name = let_match.group(2)
                if dependent_variable_name in variables_to_modify:
                    variables_to_modify_let.add(variable_name)
        # print(variables_to_modify_let,"s",variables_to_modify)
        exit_q =[]
        # Identify variables used in Qubit arrays
        for line in lines:
            modified_line = line
            pattern = r'use\s+\w+\s*=\s*Qubit\[(\w+)\]' 
            matches = re.findall(pattern, line)
      
            for match in matches:
                exit_q.append(match) 
        for line in lines:
            modified_line = line
            # Handle mutable variables with negative values
            for variable_name in variables_to_modify:
                if variable_name in line:
                    pattern = r'(mutable\s+' + re.escape(variable_name) + r'\s*=\s*)-\d+(\.\d+)?'
                    match = re.search(pattern, modified_line)
                    if match and variable_name in exit_q :
                     
                        count += 1
                        random_number = random.randint(0, 10)
                        modified_line = modified_line[:match.start(1)] + match.group(1) + str(random_number) + modified_line[match.end():]
                        break

            # Handle let variables dependent on mutable variables
            for variable_name in variables_to_modify_let:
                if variable_name in line and f'[{variable_name}]' in test_case:
                    pattern = r'(let\s+' + re.escape(variable_name) + r'\s*=\s*)\w+;'
                    match = re.search(pattern, modified_line)
                    if match and variable_name in exit_q:
                   
                        count += 1
                        modified_line = modified_line[:match.start(1)] + match.group(1) + next(iter(variables_to_modify)) + modified_line[match.end():]
                        break

            # Handle Qubit arrays with negative values
            qubit_array_match = re.match(r'^\s*use\s+(\w+)\s*=\s*Qubit\[-\d+\];', line)
            if qubit_array_match:
                
                count += 1
                modified_line = re.sub(r'Qubit\[-\d+\]', 'Qubit[5]', modified_line)
        
            modified_lines.append(modified_line)

        return '\n'.join(modified_lines), count
    else :
        return test_case, count


def fix_negative_exponents(test_case: str,count) -> str:
    """Resolve negative exponents by replacing them with 20."""
    
    if "//wrong" in test_case :
        return test_case ,count
    lines = test_case.split('\n')
    modified_lines = []
    
    variables_to_modify = set()
    variables_to_modify_let = set()

    # Identify all mutable variable assignments with negative values
    for line in lines:
        mutable_match = re.match(r'^\s*mutable\s+(\w+)\s*=\s*(-\d+);', line)
        if mutable_match:
            variable_name = mutable_match.group(1)
            variables_to_modify.add(variable_name)
    
    # Identify if those variables are being used elsewhere, especially in let assignments
    for line in lines:
        let_match = re.match(r'^\s*let\s+(\w+)\s*=\s*(\w+);', line)
        if let_match:
            variable_name = let_match.group(1)
            dependent_variable_name = let_match.group(2)
            if dependent_variable_name in variables_to_modify:
                variables_to_modify_let.add(variable_name)

    # Process each line and replace negative values 
    for line in lines:
        modified_line = line
        for variable_name in variables_to_modify:
            if variable_name in line and (f'2^{variable_name}' in test_case or f'2^{variable_name}' in test_case):
                pattern = r'(mutable\s+' + re.escape(variable_name) + r'\s*=\s*)-\d+'
                match = re.search(pattern, modified_line)
                if match:
                    count =count+1
                    random_number = random.randint(0, 10)
                    modified_line = modified_line[:match.start(1)] + match.group(1) + str(random_number) + modified_line[match.end():]
                    break
        modified_lines.append(modified_line)

    return '\n'.join(modified_lines), count


def modify_code_ControlledOnInt(test_case,count):
    """
    Finds the usage of ControlledOnInt and matches its two variable names. Adjusts the values 
    of these variables to ensure they are within the valid range based on their definitions.

    Args:
        test_case (str): The input code containing the usage of ControlledOnInt and variable declarations.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted variable values.
        int: The updated counter of modifications made.
    """
    # Find all occurrences of ControlledOnInt and extract the variable names
    matches = re.findall(r'ControlledOnInt\s*\(\s*([^,]+?)\s*,\s*.*?\)\s*\(\s*([^,]+?)\s*,', test_case, re.DOTALL)
    if not matches:
        return test_case,count
    for match in matches:
        variable_a, variable_b = match
        # Find the definition of variable_b and extract its size X
        match_b = re.search(r'use\s+' + variable_b + r'\s+=\s+Qubit\[(\d+)\];', test_case)
        if not match_b:
            continue
        x = int(match_b.group(1))
     
        # Find the definition of variable_a and determine if it is a number or an array
        match_a = re.search(r'mutable\s+(' + re.escape(variable_a) + r'\w*)\s+=\s+(\[.*?\]|-?\d+);', test_case, re.DOTALL)
        if not match_a:
            continue
        max_value = 2**x - 1
        
        actual_variable_name = match_a.group(1)  
        value_a = match_a.group(2)  

        # If variable_a is a single number
        if '[' in value_a:
            numbers = [int(n) for n in re.findall(r'-?\d+', value_a)]
            corrected_numbers = [str(n if 0 <= n <= max_value else max_value) for n in numbers]
            new_value = '[' + ', '.join(corrected_numbers) + ']'
            test_case = test_case.replace(value_a, new_value)
            count=count+1
        else:
            number = int(value_a)
            corrected_number = str(number if 0 <= number <= max_value else max_value)
            test_case = test_case.replace(value_a, corrected_number)
            count=count+1   
    return test_case, count


def modify_code_ApplyXorInPlace(code_str,count):
    """
    Modifies the code to ensure variables used in ApplyXorInPlace are within the valid range
    based on the size of the associated Qubit array.

    Args:
        code_str (str): The input code containing the usage of ApplyXorInPlace and variable declarations.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted variable values.
        int: The updated counter of modifications made.
    """
    matches = re.findall(r"ApplyXorInPlace\((\w+), LittleEndian\((\w+)\)\);", code_str)
    # Extract the values of mutable variables
    var_values = {}
    for var, value in re.findall(r"mutable (\w+) = (-?\d+);", code_str):
        var_values[var] = int(value)
    # Process each match found
    for var_A, var_B in matches:
        # Find the definition of var_B and extract the associated Qubit array size
        match = re.search(fr"use {var_B} = Qubit\[(\w+)\];", code_str)
        if match:
            var_C = match.group(1)
            value_C = var_values.get(var_C)
             # Check if var_A needs modification based on the value of var_C
            if var_A in var_values and value_C is not None and (var_values[var_A] > value_C or var_values[var_A] < 0):
                random_value = random.randint(0, value_C)
                code_str = code_str.replace(f"mutable {var_A} = {var_values[var_A]};", f"mutable {var_A} = {random_value};")
                var_values[var_A] = random_value
                count=count+1

    return code_str,count



def extract_long(test_case: str) -> dict:
    """
    Extracts variable names and their lengths or values from the provided code.

    Args:
        test_case (str): The input code containing variable and array declarations.

    Returns:
        dict: A dictionary where keys are variable names and values are their lengths or values.
    """
    variables_and_lengths = {}
    lines = test_case.split('\n')
    
    for line in lines:
        # Match mutable or let variable declarations and extract their values
        variable_match = re.match(r'^\s*(mutable\s+|let\s+)(\w+)\s*=\s*(.*?);', line)
        if variable_match:
            var_name = variable_match.group(2)
            value = variable_match.group(3)
            if value.startswith('[') and value.endswith(']'):
                # Calculate the length of the array
                value = len(value.split(','))
            else:
                try:
                    value = int(value)
                except ValueError:
                    value = value  
            variables_and_lengths[var_name] = value
        # Match Qubit array declarations and evaluate their lengths
        array_match = re.match(r'^\s*use (\w+)\s*=\s*Qubit\[([\w\s\-+*\/]+)\];', line)
        if array_match:
            array_name = array_match.group(1)
            array_length_expression = array_match.group(2)
            try:
                array_length = eval(array_length_expression, {}, variables_and_lengths)
            except:
                array_length = None
            if array_length is not None:
                variables_and_lengths[array_name] = array_length
    # Resolve variables that are dependent on other variables
    keys_to_remove = []
    variables_and_lengths_TEMP=variables_and_lengths
    for key, value in variables_and_lengths_TEMP.items():
        if not isinstance(value, (int, float)):
            for key1, value1 in variables_and_lengths_TEMP.items():
                if value== key1:
                    variables_and_lengths[key] = value1

    for key, value in variables_and_lengths.items():
        if not isinstance(value, (int, float)):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del variables_and_lengths[key]
    return variables_and_lengths

def extract_for_loop_range(test_case: str) -> (int, int):
    """
    Extracts the range of a for loop from the given code.

    Args:
        test_case (str): The input code containing a for loop.

    Returns:
        tuple: A tuple containing the start and end range of the for loop, or None if the range cannot be determined.
    """

    # Extract variables and their values from the code
    var_dict=extract_long(test_case)
    # Match the for loop and extract the range
    for_match = re.search(r'for\s*\([^)]*in\s*(.*?)\s*\.\.\s*(.*?)\)', test_case)
    if for_match:
        start_range = for_match.group(1) 
        end_range = for_match.group(2)  
        # Determine the value of the start range
        r = int(start_range) if start_range.isdigit() else var_dict.get(start_range, None)
        if not r:
            return None
        if end_range.isdigit():
            l = int(end_range)
        else:
            for variable, value in var_dict.items():
                end_range = end_range.replace(variable, str(value))
            if end_range.isdigit():
                l = int(end_range)
                return [r, l]  
            else:
                return None  
    else:
        return None


def extract_array_access_range(test_case):
    """
    Extracts the range of array accesses within a for loop from the given code.

    Args:
        test_case (str): The input code containing a for loop with array accesses.

    Returns:
        list: A list of tuples containing the array name and the lower and upper bounds of the access range.
    """
    # Match the body of the for loop
    for_body_match = re.search(r'for\s*\(.*?\)\s*{(.*?)}', test_case, re.DOTALL)
    # Extract the range of the for loop
    i_range = extract_for_loop_range(test_case)
    if not i_range:
        return []
    var_dict = extract_long(test_case)
    if not for_body_match:
        return []
    for_body = for_body_match.group(1)
    
    array_access_matches = re.findall(r'(\w+)\[(.*?)\]', for_body) 
    results = []
    for array_name, index_expr in array_access_matches:
        # Replace variables in the index expression with their values
        for variable, value in var_dict.items():
            index_expr = index_expr.replace(variable, str(value))
        if  index_expr=="i":
            # Calculate the lower bound using the start of the for loop range
            index_expr_for_lower = index_expr.replace(index_expr, str(i_range[0])) 
            lower_bound = eval(index_expr_for_lower)
            # Calculate the upper bound using the end of the for loop range
            index_expr_for_upper = index_expr.replace(index_expr, str(i_range[1]))
            upper_bound = eval(index_expr_for_upper)
        else:
            lower_bound = upper_bound = eval(index_expr)   
        # Append the array name and its access bounds to the results list
        results.append((array_name, lower_bound, upper_bound))
    
    return  results


def adjust_for_loop_range(test_case: str,count) -> str:
    """
    Adjusts the range of for loops in the given code to ensure they are within valid bounds based on the array lengths.

    Args:
        test_case (str): The input code containing for loops and array accesses.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted for loop ranges.
        int: The updated counter of modifications made.
    """
    # Extract variable lengths from the code
    var_len_dict = extract_long(test_case)
    # Extract array access ranges within the for loops
    results = extract_array_access_range(test_case)
    # Set min_length to 0 if no valid array length was found
    min_length = -10
    for array_name, _, _ in results:
        if array_name in var_len_dict and var_len_dict[array_name] < min_length:
            min_length = var_len_dict[array_name]       
    if min_length == -10:
        min_length = 0
    # Check and adjust for loop bounds if necessary
    for _, lower_bound, upper_bound in results:
        if (lower_bound < 0 or upper_bound >= min_length) or (lower_bound > upper_bound):
            left_matches = re.findall(r'mutable (left\d+) = .*?;', test_case)
            right_matches = re.findall(r'mutable (right\d+) = .*?;', test_case)
            
            if left_matches:
                for match in left_matches:
                    test_case = re.sub(rf'mutable {match} = .*?;', rf'mutable {match} = 0;', test_case)
                    count =count+1
            if right_matches:
                for match in right_matches:
                    test_case = re.sub(rf'mutable {match} = .*?;', rf'mutable {match} = {min_length - 1};', test_case)
            break
    return test_case , count


def check_access_out_of_range(test_case,count):
    """
    Checks for out-of-range array accesses in for loops and adjusts the loop range if necessary.

    Args:
        test_case (str): The input code containing for loops and array accesses.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted for loop ranges if out-of-range accesses were found.
        int: The updated counter of modifications made.
    """
    # Adjust for loop range if 'left' and 'right' variables are present in the code
    if "right" in test_case and "left" in test_case:
        test_case,count = adjust_for_loop_range(test_case,count)
    var_len_dict = extract_long(test_case)
    results = extract_array_access_range(test_case)
    max_diff = 0

    # Check for out-of-range accesses and determine the maximum difference
    for array_name, lower_bound, upper_bound in results:
        if array_name in var_len_dict:
            access_length = upper_bound - lower_bound + 1
            array_length = var_len_dict[array_name]
            if access_length > array_length:
                diff = access_length - array_length
                if diff > max_diff:
                    max_diff = diff

    # If any out-of-range accesses are found, adjust the upper bound of the for loop range
    if max_diff > 0:
        loop_range_match = re.search(r'for\s*\(i\s*in\s*.*?\.\.\s*(.*?)(\)|\s)', test_case)
        if  loop_range_match:
            upper_bound_str = loop_range_match.group(1)
            try:
                upper_bound_val = int(upper_bound_str)
            except ValueError:
                for variable, value in var_len_dict.items():
                    upper_bound_str = upper_bound_str.replace(variable, str(value))
                upper_bound_val = eval(upper_bound_str)
                # Modify the upper bound to prevent out-of-range accesses
            modified_upper_bound = str(upper_bound_val - max_diff)
            modified_test_case = re.sub(re.escape(upper_bound_str), modified_upper_bound, test_case, count=1)
            count =count +1
            return  modified_test_case,count
    return test_case,count


def modify_controlled_x(test_case: str,count) -> str:
    """
    Modifies the input code to ensure the indices used in the Controlled X operation are different.
    If the indices are the same, it adjusts the array size and indices to valid values.

    Args:
        test_case (str): The input code containing the Controlled X operation.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted Controlled X operation.
        int: The updated counter of modifications made.
    """
    # Pattern to match the Controlled X operation and extract relevant variables and indices
    pattern = r'Controlled X\(\[([a-zA-Z0-9_]+)\[([a-zA-Z0-9_]+)\]\],\s*([a-zA-Z0-9_]+)\[([a-zA-Z0-9_]+)\]\);'
    match = re.search(pattern, test_case)
    
    if not match:
        return test_case,count
    
    array_name = match.group(1)
    idx1_name = match.group(2)
    idx2_name = match.group(4)
    # Patterns to find the values of the indices
    idx1_value_pattern = rf"mutable {idx1_name} = (\d+);"
    idx2_value_pattern = rf"mutable {idx2_name} = (\d+);"
    # Extract the values of the indices or use the index name as the value if not found
    idx1_value = int(re.search(idx1_value_pattern, test_case).group(1)) if re.search(idx1_value_pattern, test_case) else int(idx1_name)
    idx2_value = int(re.search(idx2_value_pattern, test_case).group(1)) if re.search(idx2_value_pattern, test_case) else int(idx2_name)
    # If the indices are the same, adjust the array size and indices to valid values
    if idx1_value == idx2_value:
        test_case = re.sub(r'use ' + array_name + r' = Qubit\[\d+\];', 'use ' + array_name + ' = Qubit[2];', test_case)
        
        # Update the values of the indices
        test_case = test_case.replace(f'mutable {idx1_name} = {idx1_value};', f'mutable {idx1_name} = 0;')
        test_case = test_case.replace(f'mutable {idx2_name} = {idx2_value};', f'mutable {idx2_name} = 1;')
        count= count+1
    return test_case,count

def prevent_qubit_overflow(test_case: str, count) -> str:
    """
    Modifies the input code to prevent qubit array sizes from exceeding a specified limit (30 in this case).
    If any qubit array size exceeds the limit, it adjusts the size to the maximum allowed value.

    Args:
        test_case (str): The input code containing variable declarations and qubit array usages.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with adjusted qubit array sizes.
        int: The updated counter of modifications made.
    """
    lines = test_case.split('\n')
    
    variable_values = {}  # Dictionary to store the values of variables
    variables_to_modify = {}  # Dictionary to store variables that may need modification

    for i, line in enumerate(lines):
        # Match let or mutable variable declarations
        let_match = re.match(r'(\s*)(let|mutable)\s+(\w+)\s*=\s*(\d+);', line)
        # Match use statements for qubit arrays
        use_match = re.match(r'^\s*use\s+(\w+)\s*=\s*Qubit\[(\w+)\];', line)
        
        if let_match:
            # Extract details from let/mutable match
            indentation, _, variable, value = let_match.groups()
            variable_values[variable] = int(value)
            variables_to_modify[variable] = [i, indentation, None]
        
        if use_match:
            _, size_variable = use_match.groups()
            size = int(size_variable) if size_variable.isdigit() else variable_values.get(size_variable, 0)

            if size > 30 and size_variable in variables_to_modify:
                variables_to_modify[size_variable][2] = 30
    # Modify lines where necessary
    for variable, [line_index, indentation, new_value] in variables_to_modify.items():
        if new_value is not None:
            count += 1
            lines[line_index] = f"{indentation}let {variable} = {new_value};"

    return '\n'.join(lines), count


def array_process(test_case: str, count):
    """
    Processes the input code to address various issues related to array and variable usage.
    If the input code contains "//wrong", it returns the input code unchanged.

    Args:
        test_case (str): The input code containing array and variable declarations and operations.
        count (int): A counter for the number of modifications made.

    Returns:
        str: The modified code with addressed issues.
        int: The updated counter of modifications made.
    """
    
    # fix the 'inf' issue
    test_case = re.sub(r'\binf\b', '0.0', test_case)
    
    # There is no need to avoid these errors when generating an invalid test case
    if "//wrong" in test_case :
        return test_case,count
    
    # Process the code to handle various issues
    test_case,count = array_max_process_1(test_case,count)
    test_case,count = array_negative_numbers(test_case,count)
    test_case,count = array_max_process(test_case,count)
    test_case,count = modify_input_code(test_case,count)
    test_case,count = fix_negative_exponents(test_case,count)
    test_case,count = modify_code_ControlledOnInt(test_case,count)
    test_case,count = modify_code_ApplyXorInPlace(test_case,count)
    test_case,count = check_access_out_of_range(test_case,count)
    test_case,count = modify_controlled_x(test_case,count)
    test_case,count = prevent_qubit_overflow(test_case,count)
    return test_case,count
