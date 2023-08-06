from importlib import import_module
from django.core.management import ManagementUtility
from larango.commands import BaseCommand
from larango.utils.colors import Color
import importlib
import inspect
import sys
import os
import pkgutil
import django


def execute_from_command_line(argv=None):
    argv = argv or sys.argv[:]
    
    larango_commands = find_larango_commands()
    django_commands = find_django_commands()
    user_commands = find_user_commands()
    all_commands = larango_commands + django_commands + user_commands
    
    try:
        command = argv[1]
    except IndexError:
        command = 'help'
    if command=='-h' or command=='--help':
        command = 'help'
    
    if command not in all_commands:
        os.system('color')
        print('Unknown command: ' + Color.red(command))
        return
    
    if command in django_commands:
        if not is_larango_directory():
            os.system('color')
            print(Color.red('No Larango Project in current directory'))
            return
        sys.path.append(os.getcwd())
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.settings')
        django.setup()
        utility = ManagementUtility(argv)
        utility.execute()
        return
    
    os.system('color')
    command_object = load_command(command)
    if command_object == None:
        print('Error in command: ' + Color.red(command))
        return
    command_object.create_parser(command)
    command_object.add_arguments()
    if command_object.need_settings:
        if not command_object.load_settings():
            print(Color.red('No Larango Project in current directory'))
            return
    args = command_object.parser.parse_args(argv[2:])
    command_object.handle(args)

def find_all_commands():
    larango_commands = find_larango_commands()
    django_commands = find_django_commands()
    user_commands = find_user_commands()
    all_commands = larango_commands + django_commands + user_commands
    all_commands = list(set(all_commands))
    all_commands.sort()
    return all_commands

def find_django_commands():
    return ['runserver','showmigrations','makemigrations','migrate']

def find_larango_commands():
    command_dir = os.path.join(__path__[0], 'commands')
    return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
            if not is_pkg and not name.startswith('_')]

def find_user_commands():
    if(is_larango_directory()):
        cwd=os.getcwd()
        command_dir = os.path.join(cwd, 'commands')
        return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
                if not is_pkg and not name.startswith('_')]
    return []

def load_command(command):
    module = None
    command_object = None
    try:
        module = import_module('larango.commands.%s' % command)
    except:
        cwd=os.getcwd()
        p=os.path.join(*[cwd,'commands',command+'.py'])
        spec = importlib.util.spec_from_file_location(command, p)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except:
            pass
    
    if hasattr(module,'Command') and inspect.isclass(module.Command):
        command_object = module.Command()
        if not isinstance(command_object, BaseCommand):
            command_object = None
    else:
        pass
    
    return command_object

def is_larango_directory():
    cwd=os.getcwd()
    required_files = ['settings.py', 'asgi.py', 'wsgi.py', 'urls.py']
    for required_file in required_files:
        if not os.path.isfile(os.path.join(*[cwd,'config','django',required_file])):
            return False
    return True
