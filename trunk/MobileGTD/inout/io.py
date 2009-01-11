import os


def create_dir_if_necessary(path):
    if len(path) > 0 and not os.path.exists(path):
        os.makedirs(path)

def safe_chdir(path):
    #try:
    #    path = path_unicode.encode('utf-8')
    #except UnicodeError:
    #    #logger.log('Error decoding path %s'%repr(path_unicode))
    #    print 'Error decoding path %s'%repr(path_unicode)
    #    path = path_unicode
    create_dir_if_necessary(path)
    os.chdir(path)

def create_file(file_path):
	dir = os.path.dirname(file_path.encode('utf-8'))
	create_dir_if_necessary(dir)
	file_name = os.path.join(dir,os.path.basename(file_path.encode('utf-8')))
	
	f = file(file_name,'w')
	return f


def write(file_path,content):
    f = create_file(file_path)
    f.write(content.encode('utf-8'))
    f.close()
    from log.logging import logger
    logger.log(u'Wrote %s to %s'%(content,os.path.abspath(file_path)))    

def list_dir(root,recursive=False,filter=None):
    if not os.path.exists(root.encode('utf-8')):
        return []
    all_files_and_dirs = []
    for name in os.listdir(root.encode('utf-8')):
        file_name = u_join(root,name.decode('utf-8'))
        if recursive and os.path.isdir(file_name.encode('utf-8')):
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


def u_join(father,son):
    return u'%s/%s'%(father,son)


def read_text_from_file(unicode_file_name):
    from log.logging import logger
    file_name = unicode_file_name.encode('utf-8')
    logger.log("Reading from %s"%os.path.abspath(file_name))
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
    return os.path.isdir(unicode_path.encode('utf-8'))
