def parse_lines(lines):
    actions = []
    infos = []
    for line in lines:
        if len(line) < 3:
            continue
        elif line[0]=='#':
            infos.append(Info(line[1:].strip()))
        else:
            actions.append(parse_action(line))
    return (actions,infos)


def parse_action(string):
    matching = action_regexp.match(string)
    description = matching.group('description').rstrip(u' \r\n')
    status_string = matching.group('status')
    if (status_string == None):
        status_string = u''
    status = sign_status_map[status_string]
    info = matching.group('info')
    context = parse_context(matching.group('context'))
    if(info==None):
        info=u''
    return Action(description,context,u'',info,status)
def parse_context(context):
    context_matching = context_regexp.match(context)
    context_numbers = context_matching.group('numbers')
    context_text = context_matching.group('text')
    if(context_numbers in ABBREVIATIONS):
        context=(unicode(ABBREVIATIONS[context_numbers])+context_text).rstrip(u'/')
    else:
        context=context_text
    if (len(context)<2):
        context = u'None'
    return context
