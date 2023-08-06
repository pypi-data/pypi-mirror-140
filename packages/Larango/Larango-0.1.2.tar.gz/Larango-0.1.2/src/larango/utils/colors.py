class Color():
    
    def _format(formatting):
        return ('\033[1m' if ('b' in formatting) else '') + ('\033[4m' if ('u' in formatting) else '')
    
    def red(string, formatting = ''):
        return Color._format(formatting) + '\033[91m' + string + '\033[0m'
    
    def green(string, formatting = ''):
        return Color._format(formatting) + '\033[92m' + string + '\033[0m'
    
    def violet(string, formatting = ''):
        return Color._format(formatting) + '\033[95m' + string + '\033[0m'
    
    def blue(string, formatting = ''):
        return Color._format(formatting) + '\033[94m' + string + '\033[0m'
    
    def cyan(string, formatting = ''):
        return Color._format(formatting) + '\033[96m' + string + '\033[0m'
    
    def yellow(string, formatting = ''):
        return Color._format(formatting) + '\033[93m' + string + '\033[0m'
