# Tested in: Python 3.11.0
# By: LawlietJH
# ArgParser v1.0.3
# Descripción: Módulo para análisis y extracción de argumentos.
#              Permite mediante reglas obtener valores de los argumentos.
#              Permite analizar una cadena o una lista/tupla de
#              argumentos (como 'sys.argv' así directamente).
# TODO: Implementar funcionalidad de Auto Generación de help. Extensión de rules.
# TODO: Implementar selección de Argumentos Obligatorios. Extensión de rules.

from typing import Optional

# =======================================================================
__author__ = 'LawlietJH'   # Desarrollador
__title__ = 'ArgParser'    # Nombre
__version__ = 'v1.0.4'     # Version
# =======================================================================


class ArgParser:

    class MissingArgument(Exception):
        def __init__(self, error_msg: str = ''): self.error_msg = error_msg
        def __str__(self): return repr(self.error_msg)

    def __init__(self, rules: Optional[dict] = None, args: Optional[str | list] = None) -> None:
        """ rules: Rules for parsing arguments.
            args:  Arguments to parse. """
        self.rules = rules
        self.args = args
        self.keys = False
        self.wasv = False
        self.ignored = False
        self.help = '''\n
		\r rules = {
		\r     'pairs':  { # Key Value                  # Use examples:
		\r         'Key 1': ['-i', '--input'],          # -i value, --input value
		\r         'Key 2': '-r',                       # -r value, -r = value, -r: value
		\r         'Key 3': ('-o', '--output'),         # -o=value, --output:value
		\r         'Key 4': '-dn',                      # -dn= value, -dn value, -dn =value
		\r         'Key 5': ['-xn', '-xname', 'xn'],    # -xn: value, -xname = value, xn : value
		\r         'Key 6': '-w'                        # -w value, -w=value, -w:value, -w :value
		\r     },
		\r     'single': { # Bool
		\r         'Key 7': ['-n', '--name'],           # -n, --name
		\r         'Key 8': '-a',                       # -a
		\r         'Key 9': 'val'                       # val
		\r     }
		\r }
		'''

    def _set_args(self, args: tuple | list | str, rules: dict,
                  wasv: bool, keys: bool, ignored: bool) -> None:

        if not self.args and not args:
            raise self.MissingArgument(
                "El argumento 'args' es necesario.")

        if not self.rules and not rules:
            raise self.MissingArgument(
                "El argumento 'rules' es necesario.")

        if args:
            assert isinstance(args, (tuple, list, str))
            self.args = args

        if rules:
            assert isinstance(rules, dict),  self.help
            self.rules = rules

        if isinstance(wasv, bool):
            self.wasv = wasv

        if isinstance(keys, bool):
            self.keys = keys

        if isinstance(ignored, bool):
            self.ignored = ignored

    def pairs_union(self, args: list) -> list:
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

    def pairs_vals(self, arg: str, args: list, pairs: dict, output: dict) -> bool:

        # Pairs united:
        if ':' in arg or '=' in arg:
            tmp_arg = arg.split(':')
            if len(tmp_arg) != 2:
                tmp_arg = tmp_arg[0].split('=')
                if len(tmp_arg) != 2:
                    return True
            arg = tmp_arg[0]
            args.insert(0, tmp_arg[1])

        if not args:
            return True

        for key, val in pairs.items():
            if not arg in val and not arg == val:
                continue
            if isinstance(val, (list, tuple, str)):
                if self.keys and not key in output:
                    output[key] = (arg, args.pop(0))
                elif (self.keys and key in output) or key in self.keys_used:
                    return True
                elif not arg in output:
                    output[arg] = args.pop(0)
                    self.keys_used.append(key)
                return False
        return True

    def single_vals(self, arg: str, single: dict, output: dict) -> bool:
        for key, val in single.items():
            if not arg in val and not arg == val:
                continue
            if isinstance(val, (list, tuple, str)):
                if self.keys and not key in output:
                    output[key] = (arg, True)
                elif (self.keys and key in output) or key in self.keys_used:
                    return True
                elif not arg in output:
                    output[arg] = True
                    self.keys_used.append(key)
                return False
        return True

    def strings_parser(self, args: list) -> list[str]:
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

    def _set_wasv(self, single: dict, output: dict) -> None:
        if self.keys:
            arguments = [argument for argument, _ in output.values()]
            for key, value in single.items():
                if isinstance(value, (list, tuple)):
                    in_output = [False, value[0]]
                    for val in value:
                        if val in arguments:
                            in_output = [True, val]
                            break
                    if not in_output[0]:
                        output[key] = (in_output[1], False)
                elif not key in arguments:
                    output[key] = (value, False)
            return

        for value in single.values():
            if isinstance(value, (list, tuple)):
                in_output = [False, value[0]]
                for val in value:
                    if val in output:
                        in_output = [True, val]
                        break
                if not in_output[0]:
                    output[in_output[1]] = False
            elif not value in output:
                output[value] = False

    def parser(self, args: Optional[str | list] = None, rules: Optional[dict] = None,
               keys: Optional[bool] = False, wasv: Optional[bool] = False,
               ignored: Optional[bool] = False) -> dict | tuple[dict, tuple]:
        """ args:    Arguments to parse.
            rules:   Rules for parsing arguments.
            keys:    Output with key names. Example: {'Key': ('argument', 'value')}.
            wasv:    Output with all single values (True and False).
            ignored: Get two output values: Parsed arguments & Ignored arguments. """

        self._set_args(args, rules, wasv, keys, ignored)

        args = self.args[:]
        self.keys_used = []
        ignored_values = []
        output = {}

        pairs: dict = self.rules.get('pairs')
        single: dict = self.rules.get('single')

        assert pairs or single, self.help

        if isinstance(args, tuple):
            args = list(args)
        elif isinstance(args, list):
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

        assert isinstance(args, list), f"args = {args} is not valid."

        args = self.pairs_union(args)

        while args:
            arg = args.pop(0)

            if pairs:  # Validate Pairs (key value): -Arg Value
                ignore = self.pairs_vals(arg, args, pairs, output)
                if not ignore:
                    continue

            if single:  # Validate Single (bool): -Arg
                ignore = self.single_vals(arg, single, output)
                if not ignore:
                    continue

            ignored_values.append(arg)

        if wasv and single:
            self._set_wasv(single, output)

        if self.ignored:
            # Output Values with Arguments and Ignored Values.
            return output, tuple(ignored_values)

        # Output Argument Values
        return output
