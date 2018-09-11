from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile as _FieldFile
from django.utils.encoding import smart_str
import datetime
import os

CONFIGSTORE_FILE_PATH = getattr(settings, 'CONFIGSTORE_FILE_PATH', u'configstore/')
CONFIGSTORE_FILE_STORAGE = getattr(settings, 'CONFIGSTORE_FILE_STORAGE', default_storage)

class FieldFile(_FieldFile):
    """A file-like object, returned for `FileField` and `ImageField`."""
    
    def __init__(self, name):
        File.__init__(self, None, name)
        self.storage = CONFIGSTORE_FILE_STORAGE
        self._committed = True

    def _require_file(self):
        if not self:
            raise ValueError("This instance has no file associated with it.")

    def get_directory_name(self):
        return os.path.normpath(datetime.datetime.now().strftime(smart_str(CONFIGSTORE_FILE_PATH)))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))
        
    def save(self, name, content):
        name = os.path.join(self.get_directory_name(), self.get_filename(name))
        self.name = self.storage.save(name, content)
        # Update the filesize cache:
        self._size = content.size
        self._committed = True
    save.alters_data = True
    
    def delete(self):
        # Only close the file if it's already open, which we know
        # by the presence of self._file:
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)
        self.name = None

        # Delete the filesize cache
        if hasattr(self, '_size'):
            del self._size
        self._committed = False
    delete.alters_data = True
    
    