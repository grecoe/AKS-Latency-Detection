__version__ = 0.1

import codecs

'''
    Having trouble reading the basic logs I'm pulling from Powershell. They
    are unicode and I can't find a good way to bring them into line so I can 
    search them. So....if the first two characters of the first line are \ff\fe
    then we have unicode and need to translate it to ascii.
'''
def detectUnicode(textLine):
    isUnicode = False
    if len(textLine) >= 2:
        char1 = codecs.encode(textLine[0], encoding="utf-16")
        char2 = codecs.encode(textLine[1], encoding="utf-16")

        # tran1[2] == b'\xff' and tran2[2] == b'\xfe'
        if char1[2] == 255 and char2[2] == 254:
            isUnicode = True
        
    return isUnicode

'''
    Convert unicode to ascii. Interestingly enough when we 
    do translate it, we still end up with a bunch of \x00 so
    we need to replace those as well. Once done, the string
    is usable. 
'''
def converAscii(textLine):
    uni = line.encode("utf-16")
    resx = uni.decode(encoding="ascii", errors="ignore")
    return resx.replace('\x00', '')
