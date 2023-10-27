# Tested in: Python 3.11.0
# By: LawlietJH
# ArgParser v1.0.1
# Descripción: Módulo para análisis y extracción de argumentos.
#              Permite mediante reglas obtener valores de los argumentos.
#              Permite analizar una cadena o una lista/tupla de
#              argumentos (como 'sys.argv' así directamente).

from typing import Optional

# =======================================================================
__author__ = 'LawlietJH'   # Desarrollador
__title__ = 'ArgParser'    # Nombre
__version__ = 'v1.0.1'     # Version
# =======================================================================


class ArgParser:

    class MissingArgument(Exception):
        def __init__(self, error_msg=''): self.error_msg = error_msg
        def __str__(self): return repr(self.error_msg)

    def __init__(self, rules: Optional[dict] = None, args: Optional[str | list] = None,
                 wasv: Optional[bool] = False, wn: Optional[bool] = False):
        """
        rules: Rules for parsing arguments.
        args:  Arguments to parse.
        wasv:  Output with all single values (true and false).
        wn:    Output with names. example: {'Name': ('argument', 'value')}.
        """
        self.rules = rules
        self.args = args
        self.wasv = wasv
        self.wn = wn
        self.help = '''Example...\n
		\r rules = {
		\r     'pairs':  {  # 'arg value'               # Use:
		\r         'Name 1': ['-e', '--example'],       # -e value, --example value
		\r         'Name 2': '-o',                      # -o value
		\r         'Wordlist': '-w'                     # -w value
		\r     },
		\r     'single': {  # 'arg'
		\r         'Name 3': ['-n', '--name'],          # -n, --name
		\r         'Name 4': '-a',                      # -a
		\r         'Name 5': 'val'                      # val
		\r     },
		\r     'united': {  # 'arg = value' or 'arg: value'
		\r         'Name 6': ('-vn', '--valuename'),    # -vn=value, --valname:value
		\r         'Name 7': '-dn',                     # -dn= value
		\r         'Name 8': ['-xn', '-xname', 'xn'],   # -xn: value, -xname = value, xn : value
		\r         'Wordlist': '-w'                     # -w: value
		\r                                              # (-w alternative value to -w in 'pairs' rules)
		\r     }
		\r }
		'''

    def _set_args(self, rules, args, wasv, wn):

        if not self.rules and not rules:
            raise self.MissingArgument(
                "El argumento 'rules' es obligatorio.")

        if not self.args and not args:
            raise self.MissingArgument(
                "El argumento 'args' es obligatorio.")

        assert isinstance(rules, dict),  self.help
        assert isinstance(args, (tuple, list, str))

        self.rules = rules
        self.args = args

        if not self.wasv and wasv:
            self.wasv = True

        if not self.wn and wn:
            self.wn = wn

    def pairs_union(self, args):
        # Union of params with '=' or ':'
        tmp = []
        concat = ''

        for i, arg in enumerate(args):
            try:
                if i+1 < len(args) and args[i+1] == '=':
                    concat += arg
                    continue
                elif arg == '=':
                    concat += arg
                    continue
                elif i > 0 and args[i-1] == '=':
                    concat += arg
                    tmp.append(concat)
                    concat = ''
                    continue
            except:
                pass

            try:
                if i+1 < len(args) and args[i+1] == ':':
                    concat += arg
                    continue
                elif arg == ':':
                    concat += arg
                    continue
                elif args[i-1] == ':':
                    concat += arg
                    tmp.append(concat)
                    concat = ''
                    continue
            except:
                pass

            try:
                if i+1 < len(args) and args[i+1].startswith('='):
                    concat += arg
                    continue
                elif arg.startswith('='):
                    concat += arg
                    tmp.append(concat)
                    concat = ''
                    continue
            except:
                pass

            try:
                if i+1 < len(args) and args[i+1].startswith(':'):
                    concat += arg
                    continue
                elif arg.startswith(':'):
                    concat += arg
                    tmp.append(concat)
                    concat = ''
                    continue
            except:
                pass

            try:
                if arg.endswith('='):
                    concat += arg
                    continue
                elif i > 0 and args[i-1].endswith('='):
                    concat += arg
                    tmp.append(concat)
                    concat = ''
                    continue
            except:
                pass

            try:
                if arg.endswith(':'):
                    concat += arg
                    continue
                elif i > 0 and args[i-1].endswith(':'):
                    concat += arg
                    tmp.append(concat)
                    concat = ''
                    continue
            except:
                pass

            if concat:
                tmp.append(concat)
                concat = ''
            else:
                tmp.append(arg)

        args = tmp

        return args

    def pairs_vals(self, arg, args, pairs, output, wn):
        for key, val in pairs.items():
            if isinstance(val, (list, tuple)) and not arg in val:
                continue
            elif isinstance(val, str) and not arg == val:
                continue
            if isinstance(val, (list, tuple, str)):
                if wn and not key in output:
                    output[key] = (arg, args.pop(0))
                elif (wn and key in output) or key in self.keys_used:
                    return True
                elif not arg in output:
                    output[arg] = args.pop(0)
                    self.keys_used.append(key)
                return False
        return True

    def single_vals(self, arg, single, output, wn):
        ignore = True

        for key, val in single.items():

            if val.__class__ in [list, tuple]:
                if arg in val:
                    if wn:
                        output[key] = (arg, True)
                    else:
                        output[arg] = True
                    ignore = False
                    break
            elif val.__class__ == str:
                if arg == val:
                    if wn:
                        output[key] = (arg, True)
                    else:
                        output[arg] = True
                    ignore = False
                    break

        return ignore

    def united_vals(self, arg, united, output, ignored, wn):
        tmp_arg = arg.split(':')

        if len(tmp_arg) != 2:
            tmp_arg = tmp_arg[0].split('=')
            if len(tmp_arg) != 2:
                ignored.append(arg)
                return 'continue'

        ignore = True

        for key, val in united.items():

            if val.__class__ in [list, tuple]:
                if tmp_arg[0] in val:
                    if wn and not key in output:
                        output[key] = (tmp_arg[0], tmp_arg[1])
                    elif not tmp_arg[0] in output:
                        output[tmp_arg[0]] = tmp_arg[1]
                    ignore = False
                    break
            elif val.__class__ == str:
                if tmp_arg[0] == val:
                    if wn and not key in output:
                        output[key] = (tmp_arg[0], tmp_arg[1])
                    elif not tmp_arg[0] in output:
                        output[tmp_arg[0]] = tmp_arg[1]
                    ignore = False
                    break

        return ignore

    def strings_parser(self, args):
        tmp = []
        init = False
        char = ''
        for arg in args:
            if (arg.startswith('"') or arg.startswith("'")) \
                    and not ('"' in arg[1:] or "'" in arg[1:]) and not init:
                tmp.append(arg[1:])
                init = True
                if arg.startswith('"'):
                    char = '"'
                else:
                    char = "'"
            elif (arg.startswith('="') or arg.startswith("='")) and not init:
                tmp.append('='+arg[2:])
                init = True
                if arg.startswith('="'):
                    char = '"'
                else:
                    char = "'"
            elif ('="' in arg or "='" in arg) and not init:
                if '="' in arg:
                    arg = arg.replace('="', '=')
                    char = '"'
                else:
                    arg = arg.replace("='", '=')
                    char = "'"
                tmp.append(arg)
                init = True
            elif (arg.startswith('"') or arg.startswith("'")) and not init:
                tmp.append(arg[1:])
                init = True
                if arg.startswith('"'):
                    char = '"'
                else:
                    char = "'"
            elif (arg.endswith('"') or arg.endswith("'")) and init:
                tmp[-1] += ' ' + arg[:-1]
                init = False
                if arg.endswith('"'):
                    char = '"'
                else:
                    char = "'"
            elif init:
                tmp[-1] += ' ' + arg
            else:
                if char == '"':
                    arg = arg.replace('"', '')
                else:
                    arg = arg.replace("'", '')
                tmp.append(arg)
        return tmp

    def parser(self, rules: Optional[dict] = None, args: Optional[str | list] = None,
               wasv: Optional[bool] = False, wn: Optional[bool] = False):

        self._set_args(rules, args, wasv, wn)

        ignored = []
        output = {}

        pairs = rules.get('pairs')
        single = rules.get('single')
        united = rules.get('united')

        assert pairs or single or united, self.help

        if isinstance(args, tuple):
            args = list(args)
        elif isinstance(args, list):
            # while '' in args:
            # args.remove('')
            tmp = []
            for arg in args:
                if ' ' in arg and not ('="' in arg or "='" in arg) and \
                    (not (arg.startswith('"') and arg.endswith('"')) or
                     (not (arg.startswith("'") and arg.endswith("'")))):
                    arg = '"' + arg + '"'
                arg = arg.split(' ')
                tmp.extend(arg)
            args = tmp
        elif isinstance(args, str):
            c = False
            s = False
            tmp = ''
            for char in args:
                if char in ['"', "'"] and not c:
                    c = char
                    s = False
                elif char in ['"', "'"] and c:
                    c = False
                elif not char == ' ' and s and not c:
                    s = False
                elif char == ' ' and not c and s:
                    char = ''
                elif char == ' ' and not c and not s:
                    s = True
                tmp += char
            args = tmp.split(' ')

        args = self.strings_parser(args)

        assert isinstance(args, list), f'args = {args} is not valid.'

        args = self.pairs_union(args)

        self.keys_used = []

        while args:
            arg = args.pop(0)
            ignore = True

            if pairs and args:  # Validate Pairs: -Arg Value
                ignore = self.pairs_vals(arg, args, pairs, output, wn)

            if not ignore:
                continue

            if single:  # Validate Single: -Arg
                ignore = self.single_vals(arg, single, output, wn)

            if not ignore:
                continue

            if united:  # Validate United: -Arg = Value, -Arg: Value
                ignore = self.united_vals(
                    arg, united, output, ignored, wn)

            if ignore == 'continue' or not ignore:
                continue

            ignored.append(arg)

        if single and wn and wasv:
            arguments = [argument for argument, content in output.values()]
            for key, value in single.items():
                if value.__class__ in (list, tuple):
                    in_output = [False, value[0]]
                    for val in value:
                        if val in arguments:
                            in_output = [True, val]
                            break
                    if not in_output[0]:
                        output[key] = (in_output[1], False)
                elif not key in arguments:
                    output[key] = (value, False)
        elif single and not wn and wasv:
            for value in single.values():
                if value.__class__ in (list, tuple):
                    in_output = [False, value[0]]
                    for val in value:
                        if val in output:
                            in_output = [True, val]
                            break
                    if not in_output[0]:
                        output[in_output[1]] = False
                elif not value in output:
                    output[value] = False

        # Reset params:
        self.wasv = False
        self.wn = False

        # Output Values with Arguments and Values Ignored.
        return output, tuple(ignored)
