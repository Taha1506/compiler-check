from Parser import *

def main():
    parser = Parser('input.txt')
    tree = parser.parse()
    parse_tree = open('parse_tree.txt', 'w', encoding='utf-8')
    if tree:
        parse_tree.write(tree.print_all())
    parse_tree.close()
    syntax_errors = open('syntax_errors.txt', 'w')
    if parser.syntax_errors:
        syntax_errors.write('\n'.join(parser.syntax_errors))
    else:
        syntax_errors.write('There is no syntax error.')
    syntax_errors.close()
    parser.code_generator.set_start()
    generated_code = open('output.txt', 'w')
    semantic_errors = open('semantic_errors.txt', 'w')
    if parser.semantic_errors:
        generated_code.write('The code has not been generated.')
        semantic_errors.write('\n'.join(parser.semantic_errors))
    else:
        semantic_errors.write('The input program is semantically correct.')
        generated_code_lines = [f'{i}\t{content}' for i, content in enumerate(parser.code_generator.code_block)]
        generated_code.write('\n'.join(generated_code_lines))

if __name__ == '__main__':
    main()
