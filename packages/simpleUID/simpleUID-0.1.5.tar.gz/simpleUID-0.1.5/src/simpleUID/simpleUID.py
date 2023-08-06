from .include import length_check
import string as _string ## Function string is defined in code
import random
import secrets

#### 0123456789
digits = _string.digits

#### Return random integer value
def integer(length:int=6, prefix:int=None, ignore_max_length:bool=False):

    #### Check if specified length is allowed
    length_check(length, ignore_max_length) ## Will fail if returns True

    #### Prefix should be of type int
    if not isinstance(prefix, int):
        if not prefix == None:
            raise TypeError('Prefix should be of type int')
    
    generated = ""
    
    #### Create random integer
    c = length
    while not c == 0:
        cur_random_int = random.choice(digits)
        if not int(cur_random_int) == 0: ## If an integer starts with 0 the 0 will be ignored
            generated += ''.join(cur_random_int)
            c -= 1

    generated = int(generated)

    #### Add prefix
    if not prefix == None:
        generated = int(str(prefix) + str(generated)) ## Workaround with int and str functions TODO clean up
        
    return generated

#### Return random string value
def string(length:int=6, prefix:str=None, ignore_max_length:bool=False, type:str="string"):

    #### Check if specified length is allowed
    length_check(length, ignore_max_length) ## Will fail if returns True

    #### Prefix should be of type str
    if not isinstance(prefix, str):
        if not prefix == None:
            raise TypeError('Prefix should be of type str')

    #### Check if 'type' is 'integer'
    if type == "integer":
        generated = str(integer(length=length)) ## Why write duplicate code?
    else:
        alphabet = _string.ascii_letters + _string.digits ## Returns abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
        generated = ''.join(secrets.choice(alphabet) for i in range(length))

    if not prefix == None:
        generated = prefix + generated

    return str(generated)

def password(length:int=10, ignore_max_length:bool=False):

    #### Check if specified length is allowed
    length_check(length, ignore_max_length) ## Will fail if returns True

    alphabet = _string.ascii_letters + _string.digits ## Returns abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3):
            break

    return password

#### Wrapper for secrets
def secret(*args, length:int=32, type:str='bytes', ignore_max_length:bool=False):

    #### Check if specified length is allowed
    length_check(length, ignore_max_length) ## Will fail if returns True

    if type == 'bytes':
        return secrets.token_bytes(length)
    elif type == 'hex':
        return secrets.token_hex(length)
    elif type == 'urlsafe':
        generated = secrets.token_urlsafe(length)
        if 'padding' in args:
            generated  += '='
        if 'encoded' in args:
            generated  = generated.encode()
        return generated
    else:
        raise Exception('Unable to generate a secret key of type {}'.format(type))


#### Check database cursor
def database(cursor, *args, **kwargs):
    
    if not "method" in kwargs:
        method = "string"
    else:
        method = kwargs['method']
        del kwargs['method'] ## Kwargs need to be passed to generation functions, method is useless here

    #### Generate new until 'id_exists' becomes False
    id_exists = True
    while id_exists:

        generated_id = string(*args, **kwargs) if method == 'string' else integer(*args, **kwargs) if method == 'integer' else None

        cursor['cursor'].execute('SELECT "{}" FROM {} WHERE {} = "{}"'.format(cursor['column'], cursor['table'], cursor['column'], generated_id))

        if not len(cursor['cursor'].fetchall()):
            id_exists = False

    return generated_id