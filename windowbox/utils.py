def id_to_directory(id):
    id_str = str(id)

    if len(id_str) <= 1:
        return ('0', '0')
    elif len(id_str) == 2:
        return ('0', id_str[0])
    else:
        return (id_str[0], id_str[1])
