from colorama import init, Fore

class length_value_too_long(Exception):
    def __init__(self, length=None):

        #### Init colorama
        init(autoreset=True)

        #### Create error message
        if not length == None:
            self.message = 'Length is set to a value larger than the maximun allowed length of {}.'.format(length)
        else:
            self.message = 'Length is set to a value larger than the maximun allowed length.'

        self.message += ' set "ignore_max_length" to "True" to ignore.'
        
        super().__init__(Fore.RED + self.message)