def safe_chdir(path_unicode):
    try:
        path = path_unicode.encode('utf-8')
    except UnicodeError:
        logger.log('Error decoding path %s'%repr(path_unicode))
        return
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

def write(file_path,content):
        safe_chdir(os.path.dirname(file_path.encode('utf-8')))
        f = file(os.path.basename(file_path.encode('utf-8')),'w')
        f.write(content.encode('utf-8'))
        f.close()

def list_dir(root,recursive=False,filter=None):
    if not os.path.exists(root.encode('utf-8')):
        return []
    all_files_and_dirs = []
    for name in os.listdir(root.encode('utf-8')):
        file_name = u_join(root,name.decode('utf-8'))
        if recursive and os.path.isdir(file_name.encode('utf-8')):
            all_files_and_dirs.extend(list_dir(file_name, True,filter))
        if filter and filter(file_name):
            all_files_and_dirs.append(file_name)
    return all_files_and_dirs

def guess_encoding(data):
    encodings = ['ascii','utf-8','utf-16']
    successful_encoding = None
    if data[:3]=='\xEF\xBB\xBF':
        logger.log('Unicode BOM in %s'%repr(data),6)
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
    f=file(unicode_file_name.encode('utf-8'),'r')
    raw=f.read()
    (text,encoding)=guess_encoding(raw)

    return text
def parse_file_to_line_list(unicode_complete_path):
    text = read_text_from_file(unicode_complete_path)
    lines = text.splitlines()
    return lines
def is_dir(unicode_path):
    return os.path.isdir(unicode_path.encode('utf-8'))
