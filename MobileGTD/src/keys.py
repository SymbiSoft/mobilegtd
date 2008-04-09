def get_key(key_name):
    if key_name == '':
        key = None
    else:
        key=eval('EKey%s'%key_name)
    return key

def all_key_names():
    return filter(lambda entry:entry[0:4]=='EKey',dir(key_codes))
def all_key_values():
    key_values=[
                EKey0,
                EKey1,
                EKey2,
                EKey3,
                EKey4,
                EKey5,
                EKey6,
                EKey7,
                EKey8,
                EKey9,
                EKeyStar,
                EKeyHash,
                ]
    return key_values
