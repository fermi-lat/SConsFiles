import os,platform,os.path

#class forStatic:
#   first = True
## Find path to specified package
def generate(env, **kw):
    pkgName = kw.get('package', '')
    if pkgName == '': 
        print 'findPkgPath called with no arg'
        return None
    path = None

    # paths all start with .\ so strip it off
    #if forStatic.first == True: 
    #    print 'findPkgPath called with argument ', pkgName
    for p in env['packageNameList']:
        bname = os.path.basename(str(p[2:]))
        #if forStatic.first == True: 
        #    print 'bname is ', bname
        if pkgName == bname: path = '#' + str(p[2:])
        if pkgName + '-' == bname[:len(bname)+1]: path = '#' + str(p[2:])

    #if forStatic.first == True:  
    #    print 'returning path = ', path
    #    forStatic.first = False
    if path != None:
        env.AppendUnique(CPPPATH = [path])

def exists(env):
    return 1
