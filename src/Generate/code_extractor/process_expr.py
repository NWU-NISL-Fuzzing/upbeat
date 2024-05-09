def remove_redundant_brackets(expr: str):
    if expr.startswith("(") and expr.endswith(")"):
        expr = expr[1:-1]
    return expr


def has_closed_brackets(expr: str):
    return expr.count("(") == expr.count(")")


def find_matched_bracket(expr: str) -> str:
    left_bracket_pos = 0
    while left_bracket_pos < len(expr):
        left_bracket_pos = expr.find(")", left_bracket_pos + 1)
        tmp_expr = expr[:left_bracket_pos + 1]
        # print("tmp_expr:"+tmp_expr)
        if has_closed_brackets(tmp_expr):
            return tmp_expr


def cut_proper_bracket(expr: str):
    # print("start:"+expr)
    if expr.startswith("(Controlled ") or expr.startswith("(Adjoint "):
        param_str = expr[expr.find(")")+1:]
        real_param_str = find_matched_bracket(param_str)
        return expr[:expr.find(")")+1]+real_param_str
    else:
        return find_matched_bracket(expr)
    return None


if __name__ == "__main__":
    print(cut_proper_bracket(
        "(Controlled AddI) ([result![i]],(LittleEndian(paddedxs![0..2*n-1-i]),LittleEndian(lhs[i..2*n-1])))"))
