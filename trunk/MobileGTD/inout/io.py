import os,sys


def create_dir_if_necessary(path):
    if len(path) > 0 and not os.path.exists(path):
        os.makedirs(path)

def safe_chdir(path):
    #try:
    #    path = os_encode(path_unicode)
    #except UnicodeError:
    #    #logger.log('Error decoding path %s'%repr(path_unicode))
    #    print 'Error decoding path %s'%repr(path_unicode)
    #    path = path_unicode
    create_dir_if_necessary(path)
    os.chdir(path)

def create_file(file_path):
    dir = os.path.dirname(os_encode(file_path))
    create_dir_if_necessary(dir)
    encoded_file_path = os_encode(file_path)
    file_name = os.path.join(dir,os.path.basename(encoded_file_path))

    f = file(file_name,'w')
    return f


def os_encode(s):
    return s.encode(sys.getfilesystemencoding())

def os_decode(s):
    if type(s) == unicode:
        return s
    else:
        return unicode(s,sys.getfilesystemencoding())

def write(file_path,content):
    f = create_file(file_path)
    f.write(os_encode(content))
    f.close()
    from log.logging import logger
    logger.log(u'Wrote %s to %s'%(content,os.path.abspath(file_path)))    

def list_dir(root,recursive=False,filter=None):
    encoded_root = os_encode(root)
    if not os.path.exists(encoded_root):
        return []
    all_files_and_dirs = []
    for name in os.listdir(encoded_root):
        file_name = os_decode(os.path.join(encoded_root,name))
        if recursive and os.path.isdir(os_encode(file_name)):
            all_files_and_dirs.extend(list_dir(file_name, True,filter))
        if (not filter) or filter(file_name):
            all_files_and_dirs.append(file_name)
    return all_files_and_dirs

def guess_encoding(data):
    #from logging import logger
    encodings = ['ascii','utf-8','utf-16']
    successful_encoding = None
    if data[:3]=='\xEF\xBB\xBF':
        data = data[3:]

    for enc in encodings:
        if not enc:
            continue
        try:
            decoded = unicode(data, enc)
            successful_encoding = enc
            break
        except (UnicodeError, LookupError):
            pass
    if successful_encoding is None:
        raise UnicodeError('Unable to decode input data %s. Tried the'
            ' following encodings: %s.' %(repr(data), ', '.join([repr(enc)
                for enc in encodings if enc])))
    else:
        #logger.log('Decoded %s to %s'%(repr(data),repr(decoded)),6)
        return (decoded, successful_encoding)


def read_text_from_file(unicode_file_name):
    from log.logging import logger
    file_name = os_encode(unicode_file_name)
#    logger.log(u'Reading from %s'%os.path.abspath(file_name).decode('utf-8'))
    f=file(file_name,'r')
    raw=f.read()
    f.close()
    (text,encoding)=guess_encoding(raw)

    return text
def parse_file_to_line_list(unicode_complete_path):
    text = read_text_from_file(unicode_complete_path)
    lines = text.splitlines()
    return lines
def is_dir(unicode_path):
    return os.path.isdir(os_encode(unicode_path))
