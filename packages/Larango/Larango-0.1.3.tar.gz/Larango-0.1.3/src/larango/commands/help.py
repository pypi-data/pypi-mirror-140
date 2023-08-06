import os
import sys
from larango import VERSION, find_all_commands
from larango.commands import BaseCommand
from larango.utils.colors import Color

class Command(BaseCommand):
    
    def __init__(self):
        super().__init__()
        self.need_settings = False
    
    def handle(self, *args):
        prog_name = os.path.basename(sys.argv[0])
        if prog_name == '__main__.py':
            prog_name = 'python -m larango'
        
        print('Larango Framework ' + Color.green(VERSION))
        print(Color.blue('Larango command line tools\n'))
        
        print(Color.yellow('Usage:'))
        print('    %s command [options] [arguments]\n' % prog_name)
        
        print(Color.yellow('Options:'))
        print(Color.green('    -h, --help'))
        print()
        
        print(Color.yellow('Commands:'))
        
        commands = find_all_commands()
        for cmd in commands:
            print('    '+Color.green(cmd))
