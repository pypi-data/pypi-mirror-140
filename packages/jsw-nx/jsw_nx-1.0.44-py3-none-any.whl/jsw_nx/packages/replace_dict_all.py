# https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
import re

def replace_dict_all(text, dic):
    for key in dic:
        val = dic[key]
        text = re.sub(key, val, text)
    return text
