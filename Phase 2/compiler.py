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

if __name__ == '__main__':
    main()
