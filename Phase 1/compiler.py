from scanner import *

def main():
    error_exists = False
    f = open('input.txt')
    symbol = open('symbol_table.txt', 'w')
    errors = open('lexical_errors.txt', 'w')
    tokens = open('tokens.txt', 'w')
    symbols = []
    lines = f.readlines()
    lines[-1] = lines[-1].strip() + '\n'
    unclosed_comment_line = None
    for i, line in enumerate(lines):
        scanner = Scanner(line)
        tokens_list = []
        errors_list = []
        while not scanner.is_end():
            tmp = scanner.next_token()
            if tmp[0] == 'ERROR' and tmp[1][0] == 'Unclosed comment' and i + 1 < len(lines):
                if unclosed_comment_line is None:
                    unclosed_comment_line = i
                lines[i + 1] = tmp[1][1].strip() + lines[i + 1]
            elif tmp[0] == 'ERROR':
                if tmp[1][0] == 'Unclosed comment':
                    tmp = (tmp[0], (tmp[1][0], tmp[1][1].strip()))
                    if len(tmp[1][1]) > 7:
                        tmp = (tmp[0], (tmp[1][0], tmp[1][1][:7] + '...'))
                error_exists = True
                if len(errors_list) == 0:
                    if unclosed_comment_line is not None:
                        errors_list.append(f'{unclosed_comment_line + 1}.\t({tmp[1][1]}, {tmp[1][0]})')
                        unclosed_comment_line = None
                    else:
                        errors_list.append(f'{i + 1}.\t({tmp[1][1]}, {tmp[1][0]})')
                else:
                    errors_list.append(f' ({tmp[1][1]}, {tmp[1][0]})')
            elif not tmp[0] == 'WHITESPACE' and tmp[0] != 'COMMENT':
                if len(tokens_list) == 0:
                    tokens_list.append(f'{i + 1}.\t({tmp[0]}, {tmp[1]})')
                else:
                    tokens_list.append(f' ({tmp[0]}, {tmp[1]})')
        if len(tokens_list):
            tokens_list.append('\n')
        if len(errors_list):
            errors_list.append('\n')
        tokens.writelines(tokens_list)
        errors.writelines(errors_list)
        for sym in scanner.identikey:
            if sym not in symbols:
                symbols.append(sym)
        for s in scanner.symbol_table_keywords:
            if s not in symbols:
                symbols.append(s)
    for i, symb in enumerate(symbols):
        symbol.writelines(f'{i + 1}.\t{symb}\n')
    if not error_exists:
        errors.writelines('There is no lexical error.')


if __name__ == '__main__':
    main()
