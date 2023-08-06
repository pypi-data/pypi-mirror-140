import argparse
import importlib
import os
import sys


class BaseCommand():
    
    def __init__(self):
        self.parser = None
        self.need_settings = True
        self.settings = None
        self.description = None
    
    def create_parser(self, command):
        prog_name = os.path.basename(sys.argv[0])
        if prog_name == '__main__.py':
            prog_name = 'python -m larango'
        
        self.parser = argparse.ArgumentParser(
            prog=prog_name + ' ' + command,
            usage='%(prog)s [options] [args]',
            description= self.description or 'Larango command line tools.'
        )
    
    def add_arguments(self):
        pass

    def handle(self, *args):
        pass
    
    def load_settings(self):
        try:
            cwd=os.getcwd()
            p=os.path.join(*[cwd,'config','django','settings.py'])
            spec = importlib.util.spec_from_file_location("settings", p)
            self.settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.settings)
            return True
        except:
            return False
