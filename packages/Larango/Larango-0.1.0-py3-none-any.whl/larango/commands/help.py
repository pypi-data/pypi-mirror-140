import os
import sys
from larango import find_all_commands
from larango.commands import BaseCommand

class Command(BaseCommand):
    
    def __init__(self):
        super().__init__()
        self.need_settings = False
    
    def handle(self, *args):
        prog_name = os.path.basename(sys.argv[0])
        if prog_name == '__main__.py':
            prog_name = 'python -m larango'
        
        print('usage: %s command [options] [args]' % prog_name)
        print('Larango command line tools.')
        print('commands:')
        
        commands = find_all_commands()
        for cmd in commands:
            print('\t'+cmd)
