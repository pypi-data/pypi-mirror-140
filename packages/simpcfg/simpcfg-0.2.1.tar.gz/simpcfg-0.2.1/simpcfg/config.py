from simplogger import simplog
from copy import deepcopy
import json
from random import randint
import logging

class config():

    __slots__ = ('name','params','dflt','use_logs','log','set_loglvl',\
                 'get_loglvl','dflt_loglvl','badval_loglvl','track_rqrmnts',\
                 'rqrmnts','track_usage','usage')

    configs = {}

    def __new__(cls, *args, **kargs):

        if len(args) == 0:
            x = random.randint(0,9999999)
            while x.__str__() in cls.configs:
                x = random.randint(0,9999999)
            cfgkey = x.__str__()
        elif len(args) == 1:
            cfgkey = args[0]
        else:
            raise ValueError('Should be passed no value or a str')

        # If cfgkey already exists, return it
        if cfgkey in cls.configs:
            cfg = cls.configs.get(cfgkey)
            if len(args) > 1 or len(kargs) > 0:
                cfg.logger.warn('Tried calling cfg with already existing '+\
                                'name and provided parameters')
            return cfg
        else:
            newcfg = super(config, cls).__new__(cls)
            newcfg.name = cfgkey
            newcfg.dflt = {}
            newcfg.params = {}
            newcfg.use_logs = kargs.get('use_logs', True)

            if newcfg.use_logs:
                newcfg.log = newcfg.__setup_logging(**kargs)

            # Set up log lvls for different actions
            dflt_log_val = kargs.pop('loglvl',logging.DEBUG)
            newcfg.set_loglvl = kargs.pop('set_loglvl',dflt_log_val)
            newcfg.get_loglvl = kargs.pop('get_loglvl',dflt_log_val)
            newcfg.dflt_loglvl = kargs.pop('dflt_loglvl',dflt_log_val)
            newcfg.badval_loglvl = kargs.pop('badval_loglvl',dflt_log_val)

            # Requirement tracking
            newcfg.track_rqrmnts = kargs.get('track_rqrmnts', False)
            if newcfg.track_rqrmnts:
                newcfg.rqrmnts = {}

            # Track usage
            newcfg.track_usage = kargs.get('track_usage', False)
            if newcfg.track_usage:
                newcfg.usage = {}

            cls.configs[cfgkey] = newcfg
            return newcfg

    def __init__(self, *args, **kargs):
        return

    # Clear default and params (useful if changing parameters)
    def clear(self, clear_rqrmnts=True, clear_usage=True):
        self.dflt.clear()
        self.params.clear()
        if clear_rqrmnts and self.track_rqrmnts:
            self.rqrmnts.clear()
        if clear_usage and self.track_usage:
            self.usage.clear()

    ''' Getting the values '''
    # Handles getting parameters from user input and default
    def __get(self, *args):
        if len(args) == 1:
            try:
                return self.params.__getitem__(args[0])
            except KeyError:
                try:
                    return self.dflt.__getitem__(args[0])
                except KeyError:
                    self.log.exception(f'Failed to get {args[0]}', err=KeyError)
        elif len(args) == 2:
            try:
                return self.params.__getitem__(args[0])
            except KeyError:
                try:
                    return self.dflt.__getitem__(args[0])
                except KeyError:
                    try:
                        self.dflt.__setitem__(args[0], args[1])
                        return args[1]
                    except KeyError:
                        self.log.exception(f'Failed to get {args[0]}', \
                                                err=KeyError)


        else:
            self.log.exception(f'Should have two inputs', err=ValueError)
        self.log.exception(f'Should not get to this point', err=RuntimeError)

    # Returns an item, applies validation
    def get(self, *args, **kargs):
        # Get the item
        key, item = args[0], self.__get(*args)
        # Track the requirements / usage if enabled
        if self.track_rqrmnts:
            self.rqrmnts[key] = self.rqrmnts.get(key,[]).append(kargs)
        if self.track_usage:
            self.usage[key] = self.usage.get(key,0)+1

        # Place raise err in
        kargs['raise_err'] = kargs.get('raise_err',True)

        # Validates values
        self.validate(item, **kargs)

        # Returns item
        return item

    # Returns item, uses brackets
    def __getitem__(self, key):
        # Track the requirements / usage if enabled
        if self.track_usage:
            self.usage[key] = self.usage.get(key,0)+1
        return self.__get(key)

    ''' Setting user input '''
    # Sets an item in user input
    def __setitem__(self, key, item):
        self.log.log(self.set_loglvl, f'{item} saved for {key}')
        self.params.__setitem__(key, item)

    # Sets an item in user input
    def set(self, key, item):
        self.__setitem__(key, item)

    ''' Validate the values '''
    # Validates an item given special flags from kargs
    def validate(self, item, **kargs):

        def badvalerr(msg, err=ValueError):
            if kargs.get('raise_err', False):
                self.log.exception(msg, err=err)
            self.log.log(self.badval_loglvl,msg)
            return False

        if 'always_allow' in kargs:
            if item in kargs.get('always_allow'):
                return True

        # Sees if item is <
        if 'min' in kargs:
            try:
                if item <= kargs.get('min'):
                    min = kargs.get('min')
                    return badvalerr(f'{item} is < min ({min})')
            except:
                return badvalerr(f'{item} cannot be numerically compared')
        # Sees if item is <=
        if 'mineq' in kargs:
            try:
                if item < kargs.get('mineq'):
                    mineq = kargs.get('mineq')
                    return badvalerr(f'{item} is < mineq ({mineq})')
            except:
                return badvalerr(f'{item} cannot be numerically compared')
        # Sees if item is >
        if 'max' in kargs:
            try:
                if item >= kargs.get('max'):
                    max = kargs.get('max')
                    return badvalerr(f'{item} is >= max ({max})')
            except:
                return badvalerr(f'{item} cannot be numerically compared')
        # Sees if item is >=
        if 'maxeq' in kargs:
            try:
                if item > kargs.get('maxeq'):
                    maxeq = kargs.get('maxeq')
                    return badvalerr(f'{item} is > maxeq ({maxeq})')
            except:
                return badvalerr(f'{item} cannot be numerically compared')
        # Sees if item is iterable
        if 'isIter' in kargs:
            if kargs.get('isIter'):
                if not self.__isIter(item):
                    return badvalerr(f'{item} is not iterable', err=TypeError)
            else:
                if self.__isIter(item):
                    return badvalerr(f'{item} is iterable', err=TypeError)
        # Sees if item is hashable
        if 'isHashable' in kargs:
            if kargs.get('isHashable'):
                if not self.__isHashable(item):
                    return badvalerr(f'{item} is not hasable', err=TypeError)
            else:
                if self.__isHashable(item):
                    return badvalerr(f'{item} is hashable', err=TypeError)
        # Sees if item is callable
        if 'callable' in kargs:
            if kargs.get('callable'):
                if not callable(item):
                    return badvalerr(f'{item} provided is not callable', \
                                            err=TypeError)
            else:
                if callable(item):
                    return badvalerr(f'{item} provided is callable',
                                            err=TypeError)

        # Verifies if item is in list of provided options
        if 'options' in kargs:
            options = kargs.get('options')
            if not self.__isIter(options):
                return badvalerr(f'{type(options)} given for options, however '+\
                                    'needs an iterable item')
            if item not in options:
                return badvalerr(f'{item} not in list of given options.')
        # Verifies object type
        if 'dtype' in kargs:
            if not isinstance(item, kargs.get('dtype')):
                return badvalerr(f'{item} is {type(item)}',err=TypeError)

        # Sees if divisible by a certain number
        #   useful for checking if even, odd, can be grouped into groups
        #   of certain sizes
        if 'divisible_by' in kargs:
            div_by = kargs.get('divisible_by')
            if not (item % div_by == 0):
                return badvalerr(f'{item} is not divisible by {div_by}')

        return True

    ''' Import / Export '''
    # Exports as dict
    def to_dict(self):
        dct = {}
        dct.update(self.dflt)
        dct.update(self.params)
        return dct
    def toDict(self, *args, **kargs): # Alais for to_dict
        return self.to_dict(*args, **kargs)
    # Loads the dict
    def load_dict(self, dct, update=False):
        if update:
            self.params.update(dct)
        else:
            self.params = deepcopy(dct)
    def loadDict(self, *args, **kargs):
        self.load_dict(*args, **kargs)
    # Turns into tuple of parameters
    def to_tuple(self):
        return tuple([(key,item) for key,item in self.items()])
    # Turns into set
    def to_set(self):
        return set([(key,item) for key,item in self.items()])
    # Turns into frozen set (hashable)
    def to_frozen_set(self):
        return frozenset([(key,item) for key,item in self.items()])

    # Turns into a string representation
    def __str__(self):
        return self.to_dict().__str__()
    def __repr__(self):
        return self.to_dict().__str__()

    def load_jsonstr(self, jsonstr):
        self.load_dict(json.loads(jsonstr))
    def to_jsonstr(self):
        return json.dumps(self.to_dict())
    def load_jsonfile(self, filename):
        with open(filename, 'r') as F:
            self.load_dict(json.load(F))
    def save_jsonfile(self, filename):
        with open(filename, 'w') as F:
            json.dump(F, self.to_dict())

    ''' Other '''
    def __iter__(self):
        return self.to_dict().__iter__()
    def items(self):
        return self.to_dict().items()
    def values(self):
        return self.to_dict().values()
    def keys(self):
        return self.to_dict().keys()
    def __len__(self):
        return len(self.to_dict())
    def items(self):
        return self.to_dict().items()
    def keys(self):
        return self.to_dict().keys()
    def __hash__(self):
        return self.to_frozen_set().__hash__()
    def __eq__(self,other):
        if isinstance(other, config):
            return self.to_frozen_set().__eq__(other.to_frozen_set())
        elif isinstance(other, dict):
            return self.to_frozen_set().__eq__(\
                frozenset([(key,item) for key,item in other.items()]))
        return self.to_frozen_set().__eq__(other)

    ''' Setup '''
    # Setup log
    def __setup_logging(self, **kargs):
        log = simplog(__name__)

        if kargs.get('console_log', True):
            log.addHandler(htype='stream', \
                h_lvl=kargs.get('console_loglvl',simplog.DEBUG), \
                formatter=kargs.get('console_log_formatter',4))

        if kargs.get('file_log', False):
            log.addHandler(htype='file', \
                           filename=kargs.get('log_filename','config.logs'),\
                           formatter=kargs.get('file_log_formatter',4))

        if 'custom_handler' in kargs:
            for hndlr in kargs.get('custom_handler'):
                log.addHandler(hndlr)

        return log

    ''' Utililty fxns '''
    # Returns whether an item is iterable
    @staticmethod
    def __isIter(item):
        try:
            iter(item)
            return True
        except:
            return False

    # Returns whether an item is hashable
    @staticmethod
    def __isHashable(item):
        try:
            hash(item)
            return True
        except:
            return False
