import sys


class Namespace(object):
    def __repr__(self):
        def get_attr():
            attr = []
            for i in self.__dir__():
                if not i.startswith('__'): attr.append(i)
            return attr

        attr = get_attr()
        repr = 'Namespace('

        for c, a in enumerate(attr):
            value = self.__getattribute__(a)
            if isinstance(value, str):
                value = f'"{value}"'

            if c == len(attr) - 1:
                repr += f'{a}={value})'
            else:
                repr += f'{a}={value}, '

        return repr


class ArgEasy(object):
    def __init__(
        self,
        description: str = None,
        version: str = None,
        project_name: str = None
    ) -> None:
        """Inicializes the ArgEasy.

        :param description: Description of CLI, defaults to None
        :type description: str, optional
        :param version: Version of App, defaults to None
        :type version: str, optional
        """

        self._commands = {}
        self._flags = {}

        self._actions = [
            'store_true',
            'store_false',
            'append',
            'default'
        ]

        self._default_namespace = Namespace()

        self.version = version
        self.description = description
        self.project_name = project_name

        # add default flags
        self.add_flag('--help', 'View the help', action='store_true')
        self.add_flag('--version', 'View the version', action='store_true')

    def add_argument(
        self,
        name: str,
        help: str,
        action: str = 'default',
        max_append: str = '*'
    ) -> None:
        """Add argument.

        :param name: Argument name
        :type name: str
        :param help: Help to argument
        :type help: str
        :param action: Argument action
        :type action: str
        :raises Exception: Action not recognized
        """

        if action not in self._actions:
            raise Exception('Action not recognized')

        self._commands[name] = {
            'help': help,
            'action': action,
            'max_append': max_append
        }

        setattr(self._default_namespace, name, None)

    def add_flag(
        self,
        name: str,
        help: str,
        action: str = 'default',
        max_append: str = '*'
    ) -> None:
        """Create a new flag.

        The flag name can have only
        one hyphen if the flag has
        only one letter (-h), or two
        hyphens if it is a word
        (--help).

        :param name: Flag name
        :type name: str
        :param help: Help text
        :type help: str
        :param action: Flag action, defaults to 'default'
        :type action: str, optional
        :param required: If flag is required, defaults to False
        :type required: bool, optional
        """

        if action not in self._actions:
            raise Exception('Action not recognized')

        self._flags[name] = {
            'help': help,
            'action': action,
            'max_append': max_append
        }

        name = name.replace('-', '')
        name = name.replace('--', '')
            
        setattr(self._default_namespace, name, None)

    def _print_help(self) -> None:
        print(f'usage: [command] [**optional] [flags]')
        if self.description:
            print(f'\n{self.description}')

        if self._commands:
            print('\ncommands:')
            for cmd, info in self._commands.items():
                print(f'    {cmd}: {info["help"]}')

        if self._flags:
            print('\nflags:')
            for flag, info in self._flags.items():
                print(f'    {flag}: {info["help"]}')

    def _print_version(self) -> None:
        if not self.project_name:
            print(f'Project: {self.version}')
        else:
            print(f'{self.project_name}: {self.version}')

    def get_args(self) -> Namespace:
        """Get args.
        
        Checks the obtained arguments 
        and determines the value of them
        by returning a Namespace object.

        If the argument has the value of
        "None", it means that it was not
        called by the command line.
        """

        namespace = Namespace()
        args = sys.argv[1:]

        if len(args) == 0:
            self._print_help()
            return self._default_namespace

        command = args[0]
        arg_flags = [a for a in args if a.startswith('-')]

        if command not in self._commands and command not in self._flags:
            print(f'unrecognized command or flag: {command}')
            print('use --help to see commands')

            return self._default_namespace

        for flag, info in self._flags.items():
            value = None

            if flag in arg_flags:
                action = info['action']
                flag_index = args.index(flag)
                max_append = info['max_append']

                if action == 'store_true':
                    value = True
                elif action == 'store_false':
                    value = False
                elif action == 'append':
                    if len(args[flag_index:]) == 1:
                        # invalid argument use
                        print(f'Invalid use of the flag "{flag}":')
                        print(f'    {flag}: {info["help"]}')
                        return self._default_namespace
                    else:
                        if max_append == '*':
                            arg_list = args[flag_index + 1:]
                        else:
                            max_append = int(max_append) + (flag_index + 1)

                            if len(args[flag_index + 1:]) > max_append:
                                print(f'Invalid use of the flag "{flag}":')
                                print(f'    {flag}: {info["help"]}')
                                return self._default_namespace

                            arg_list = args[flag_index + 1:max_append]

                        value = []

                        # filtrando flags da lista
                        # de argumentos
                        for a in arg_list:
                            if a.startswith('-'):
                                break
                            value.append(a)
                elif action == 'default':
                    if len(args[flag_index:]) < 2:
                        # invalid argument use
                        print(f'Invalid use of the flag "{flag}":')
                        print(f'    {flag}: {info["help"]}')
                        return self._default_namespace
                    else:
                        next_arg = flag_index + 1
                        value = args[next_arg]

            flag = flag.replace('-', '')
            flag = flag.replace('--', '')

            setattr(namespace, flag, value)

        # check default flags
        if namespace.help:
            self._print_help()
        elif namespace.version:
            self._print_version()

        for cmd, info in self._commands.items():
            value = None

            if cmd == command:
                action = info['action']
                max_append = info['max_append']

                if action == 'store_true':
                    value = True
                elif action == 'store_false':
                    value = False
                elif action == 'append':
                    if len(args[0:]) == 1:
                        # invalid argument use
                        print(f'Invalid use of the flag "{flag}":')
                        print(f'    {flag}: {info["help"]}')
                        return self._default_namespace
                    else:
                        if max_append == '*':
                            arg_list = args[1:]
                        else:
                            max_append = int(max_append) + 1

                            if len(args[1:]) > max_append:
                                print(f'Invalid use of the flag "{flag}":')
                                print(f'    {flag}: {info["help"]}')
                                return None

                            arg_list = args[1:max_append]

                        value = []

                        # filtrando flags da lista
                        # de argumentos
                        for a in arg_list:
                            if a.startswith('-'):
                                break
                            value.append(a)
                elif action == 'default':
                    if len(args) < 2:
                        # invalid argument use
                        print(f'Invalid use of the command "{cmd}":')
                        print(f'    add: {info["help"]}')
                        return self._default_namespace
                    else:
                        value = args[1]

            setattr(namespace, cmd, value)

        return namespace


if __name__ == '__main__':
    from random import randint

    colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'blue': '\033[34m',
        'close': '\033[m'
    }

    # test argeasy
    argeasy = ArgEasy(
        description='Test of ArgEasy project',
        version='1.0.0',
        project_name='ArgEasy'
    )

    argeasy.add_argument('say', 'Say something')
    argeasy.add_argument('check_numbers', 'Analyzes whether the numbers are even', action='append')
    argeasy.add_argument('random', 'Generate random numbers', action='store_true')

    argeasy.add_flag('-c', 'Select color of text (RGB)')
    argeasy.add_flag('-m', 'Max range numbers')

    args = argeasy.get_args()

    if args.say:
        if args.c:
            get_color = colors.get(args.c)
            close = colors.get('close')

            if not get_color:
                print('\033[31mChoose a valid color\033[m')
            else:
                print(get_color + args.say + close)
        else:
            print(args.say)
    elif args.check_numbers is not None:
        numbers = args.check_numbers
        even_numbers = []
        for n in numbers:
            if int(n) % 2 == 0:
                even_numbers.append(n)

        print(f'The even numbers are: {even_numbers}')
    elif args.random:
        if not args.m:
            print(randint(0, 9999))
        else:
            limit = int(args.m)
            print(randint(0, limit))
