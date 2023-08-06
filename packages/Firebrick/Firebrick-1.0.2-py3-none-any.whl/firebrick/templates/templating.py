import firebrick
import os


class File:
    def __init__(self, local_path, data):
        self.local_path = local_path
        # checking if the data is bytes
        self.data = data if type(data) == bytes else data.encode()
        

class Template:
    def __init__(self, files):
        self.files = files
        
    def insert_context(self, context):
        for file in self.files:
            for item in context:
                file.local_path = file.local_path.replace(item, context[item])
                # replace args are encoded as the data is bytes
                file.data = file.data.replace(item.encode(), context[item].encode())
        


class TemplateFromFiles(Template):
    def __init__(self, name, base_local_path='', path=None):
        self.name = name
        self.base_local_path = base_local_path
        if path is not None:
            self.path = os.path.join(firebrick.__path__[0], 'templates', path)
        else:
            self.path = os.path.join(firebrick.__path__[0], 'templates', self.name)
        self.files = []
        self.files_to_data()
        
    def files_to_data(self):
        for path, subdirs, files in os.walk(self.path):
            for name in files:
                # removing non local path
                local_path = path.replace(self.path, '')
                # reomoving slashs from start of path
                if local_path and (local_path[0] == '/' or local_path[0] == '\\'):
                    local_path = local_path[1:]
                # add base local path to local path if base local path
                if self.base_local_path:
                    local_path = os.path.join(self.base_local_path, local_path, name)
                else:
                    local_path = os.path.join(local_path, name)
                with open(os.path.join(path, name), 'rb') as f:
                    file_data = f.read()
                self.files.append(File(local_path, file_data))
                    
                    


class GenerateFromTemplate:
    def __init__(self, templates, context={}):
        self.templates = templates
        self.context = context
        
        # adding context for all files
        for template in self.templates:
            template.insert_context(context)
        
        self.write_files()
        
    def write_files(self):
        for template in self.templates:
            for file in template.files:
                # split up the local path to get a list of folders
                folders = file.local_path.split(os.sep)[:-1]
                # going though all folders and check if it exists if not make it
                for i in range(len(folders)):
                    folder_path = os.path.join(*folders[:i+1])
                    if not os.path.isdir(folder_path):
                        os.mkdir(folder_path)
                with open(file.local_path, 'wb') as f:
                    f.write(file.data)