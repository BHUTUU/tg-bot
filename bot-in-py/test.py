str1="https://bhutuu.github.io"
cmd='s/h\/b/:\/'
if (cmd.find('\/') != -1):
    pref=cmd.split('/')[1].removesuffix('\\')
    oldStr=pref+"/"+cmd.split('/')[2]
    print(pref)
    ne1=cmd.split('/')[3]
    if (ne1.find('\\') != -1):
        newStr=ne1.split('\\')[0]+"/"
    else:
        newStr=ne1
    print(oldStr)
    print(newStr)
#    send=str1.replace(str(oldStr), str(newStr))
#    print(send)
