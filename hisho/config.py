import os
import shutil
import logging
import tempfile
import ConfigParser

LOG = logging.getLogger()

DEFAULTS = {
  'host': 'localhost',
  'port': '7180',
  'username': 'admin',
  'password': 'admin',
  'use_tls': 'false',
}

class Converter(object):
    CONVERTERS = [
      'bool', 'int',
    ]

    def get(self, name):
        if name not in self.CONVERTERS:
            raise TypeError(name)

        return getattr(self, name)

    def bool(self, value):
        return value.lower() == 'true'

    def int(self, value):
        return int(value)

CONVERSIONS = {
  'port': 'int',
  'use_tls': 'bool',
}

class Config(object):
    DIR_CANDIDATES = ['/dev/shm', '~']
    SECTION_NAME = 'hisho'

    def __init__(self):
        self.filename = self._generate_filename()
        LOG.debug('booting config with filename %s' % self.filename)
        self.parser = self._generate_parser()
        self.converter = Converter()
        self._ensure_section()
        self._set_defaults()

    def _generate_parser(self):
        parser = ConfigParser.RawConfigParser()
        parser.read(self.filename)
        return parser

    def _set_defaults(self):
        for key, value in DEFAULTS.iteritems():
            if self._get(key) is None:
                self.set(key, value)
        self.save()

    @property
    def dir(self):
        for candidate in self.DIR_CANDIDATES:
            fullpath = os.path.realpath(os.path.expanduser(candidate))
            if os.path.isdir(fullpath) and os.access(fullpath, os.R_OK|os.W_OK|os.X_OK):
                return fullpath

    def _generate_filename(self):
        # Temp config is generated using parent process ID, so that
        # values can be memoized and looked up later on in the shell
        #
        # E.g. 
        #
        #   $ hisho config set cluster foo
        #   $ hisho service add hdfs  # automatically uses cluster 'foo'
        #
        return os.path.join(self.dir, '.hisho-%s.cfg' % os.getppid())

    def to_dict(self):
        return dict(list(self.iteritems()))

    def iteritems(self):
        for key in self.parser.options(self.SECTION_NAME):
            yield key, self.get(key)

    def convert(self, key, value):
        if key not in CONVERSIONS:
            return value

        convert_func = self.converter.get(CONVERSIONS.get(key))

        return convert_func(value)

    def _ensure_section(self):
        try:
            self.parser.add_section(self.SECTION_NAME)
        except ConfigParser.DuplicateSectionError:
            pass

    def _set(self, key, value):
        self.parser.set(self.SECTION_NAME, key, value)

    def destroy(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def generate(self, name, num_bytes=64, encoding='hex'):
        value = os.urandom(num_bytes).encode(encoding)
        self._set(name, value)

    def set(self, name, value):
        LOG.debug('setting key "%s" to value "%s"' % (name, value)) 
        self._set(name, value)

    def remove(self, key):
        self.parser.remove_option(self.SECTION_NAME, key)

    def _get(self, key, default=None):
        """
        Returns the raw value of ``key`` from the config file
        """
        try:
            return self.parser.get(self.SECTION_NAME, key)
        except ConfigParser.NoOptionError:
            return default

    def get(self, key, default=None):
        raw_value = self._get(key) or DEFAULTS.get(key, None)

        if raw_value == None:
            return raw_value

        return self.convert(key, raw_value)

    def save(self):
        fdno, filename = tempfile.mkstemp(dir=os.path.dirname(self.filename)) 
        fd = os.fdopen(fdno, 'w')
        self.parser.write(fd)
        fd.close()
        shutil.move(filename, self.filename)
        LOG.debug('successfully saved config')
