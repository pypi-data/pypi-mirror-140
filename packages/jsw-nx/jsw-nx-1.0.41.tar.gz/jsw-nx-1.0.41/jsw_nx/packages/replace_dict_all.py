# https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string

def replace_dict_all(text, dic):
    for key in dic:
        val = dict[key]
        text = text.replace(key, val)
    return text
