import os, pprint
from SCons.Script import *
#from makeStudio import *
## * Install various specified objects (includes, libraries, etc.) and
##   xxLib.py
## * Add to the list of default targets and to definition of 'all'
## * Generate wrappers for programs
## Recognized keywords are
##        package - string
##        libraryCxts - list of 2-item lists [library node, env]
##        staticLibraryCxts - list of 2-item lists [library node, env]
##        componentLibraryCxts - list of 2-item lists [library node, env]
##        swigLibraryCxts - list of 2-item lists [library node, env]
##        rootcintSharedCxts - list of 2-item lists [library node, env]
##           env must have key rootcint_node
##        rootcintStaticCxts - list of 2-item lists [library node, env]
##           env must have key rootcint_node
##        testAppCxts  - list of 2-item lists [program nodes,env]
##        binaryCxts  - list of  2-item lists [program nodes,env]
##        includes - list of file paths
##        topInclude - put includes under $INST_DIR"/include/"topInclude
##                     defaults to package
##        data     - list of file paths
##        xml      - list of file paths
##        pfiles   - lift of file paths
##        python   - list of file paths. Will be installed in python subdir
##        wrappedPython - list of python programs to be installed and wrapped
##        wrapper_env
##


def generate(env, **kw):
    if kw.get('package', '') != '':
        pkgname = kw.get('package')
        pkgtopdir = str(env.Dir('.').srcnode())
        #print 'Entered registerTargets:generate for package ', pkgname
        if os.path.exists(os.path.join(str(env.Dir('.').srcnode()),kw.get('package')+"Lib.py")):
            tools = env.Install(env['TOOLDIR'], os.path.join(str(env.Dir('.').srcnode()),kw.get('package')+"Lib.py"))
            env.Default(tools)
            env.Alias('tools', tools)
            env.Alias('all', tools)
            env.Alias(pkgname, tools)

        doxyFiles = env.CreateDoxygen(target = env['DOCDIR'].Entry(pkgname))
        env.Default(doxyFiles)
        env.Alias('all', doxyFiles)
        env.Alias(pkgname, doxyFiles)
        env.Alias("doxygen", doxyFiles)

        def getCxtList(argname):
            val = kw.get(argname, '')
            if val == '': return []
            #print "getCxtList(", argname, ") found list of length ", len(val)
            return val

        # All kinds of libraries are handled identically here
        # Only makeStudio has to distinguish
        cx = []
        cx += getCxtList('libraryCxts')
        cx += getCxtList('staticLibraryCxts')
        cx += getCxtList('swigLibraryCxts')
        cx += getCxtList('rootcintSharedCxts')
        cx += getCxtList('rootcintStaticCxts')
        if cx != []:
            nodes = []
            for x in cx:
                nodes.append(x[0])
            libraries = env.Install(env['LIBDIR'], nodes)
            env.Alias(pkgname, libraries)
            env.Alias(pkgname+'-libraries', libraries)
            env.Default(libraries)
            env.Alias('libraries', libraries)
            env.Alias('all', libraries)

        cxts = kw.get('binaryCxts','')
        if cxts != '':
            #print 'found ', len(cxts), ' binaries for pkg ', pkgname
            nodes = []
            for x in cxts:
                nodes.append(x[0])
            binaries = env.Install(env['BINDIR'], nodes)
            exes = []
            for bin in binaries:
                if env['PLATFORM'] == 'win32':
                    if  (str(bin.path)).find("manifest") != -1:
                        exes.append(bin)
                else:
                    exes.append(bin)
                
            wrappers = env.GenerateWrapperScript(exes)
            env.Depends(wrappers, binaries)
            env.Alias(pkgname, wrappers)
            env.Alias(pkgname + '-programs', exes)
            env.Default(wrappers)
            env.Alias('binaries', wrappers)
            env.Alias('all', wrappers)
        if kw.get('includes', '') != '':
            for header in kw.get('includes'):
                header = env.File(str(header))
                splitFile = str(env.Dir('.').srcnode().rel_path(header.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
                installPath = os.path.dirname(installPath)
                topInc = kw.get('topInclude', pkgname)
                includes = env.Install(env['INCDIR'].Dir(topInc).Dir(installPath), header)
                #includes = env.Install(env['INCDIR'].Dir(kw.get('package')).Dir(installPath), header)
                env.Alias(kw.get('package'), includes)
                env.Default(includes)
                env.Alias('to_install', includes)
                env.Alias('includes', includes)
                env.Alias('all', includes)
        cxts = kw.get('testAppCxts', '')
        if cxts != '':
            nodes = []
            for x in cxts:
                nodes.append(x[0])
            testApps = env.Install(env['TESTDIR'], nodes)
            exes = []
            for app in testApps:
                if env['PLATFORM'] == 'win32':
                    if  (str(app.path)).find("manifest") == -1:
                        exes.append(app)
                else:
                    exes.append(app)
            wrappers = env.GenerateWrapperScript(exes)
            env.Alias(pkgname + '-programs', exes)            
            env.Depends(wrappers, testApps)
            env.Alias(pkgname, wrappers)
            env.Alias('test', wrappers)
            env.Alias('all', wrappers)
            env.Clean('test', wrappers)
        if kw.get('pfiles', '') != '':
            pfiles = env.Install(env['PFILESDIR'], kw.get('pfiles'))
            env.AppendUnique(PFILES = pfiles)
            env.Alias(kw.get('package'), pfiles)
            env.Default(pfiles)
            env.Alias('to_install', pfiles)
            env.Alias('all', pfiles)
        if kw.get('data', '') != '':
            for file in kw.get('data'):
                file = env.File(str(file))
                splitFile = str(env.Dir('.').srcnode().rel_path(file.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
                installPath = os.path.dirname(installPath)
                data = env.Install(env['DATADIR'].Dir(kw.get('package')).Dir(installPath), file)
                #env.Alias(kw.get('package'), data)
                env.Alias(pkgname, data)
                env.Default(data)
                env.Alias('to_install', data)
                env.Alias('all', data)
        if kw.get('xml', '') != '':
            for file in kw.get('xml'):
                file = env.File(str(file))
                splitFile = str(env.Dir('.').srcnode().rel_path(file.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
                installPath = os.path.dirname(installPath)
                xml = env.Install(env['XMLDIR'].Dir(kw.get('package')).Dir(installPath), file)
                env.Alias(kw.get('package'), xml)
                env.Default(xml)
                env.Alias('to_install', xml)
                env.Alias('all', xml)
        if kw.get('python', '') != '':
            python = env.Install(env['PYTHONDIR'], kw.get('python'))
            env.Alias(kw.get('package'), python)
            env.Default(python)
            env.Alias('to_install', python)
            env.Alias('all', python)

        if kw.get('wrappedPython', '') != '':
            print "Non-null set of python scripts to be wrapped"
            pythonPrg = env.Install(env['PYTHONDIR'], kw.get('wrappedPython'))
            pyWrappers = env.GeneratePythonWrapper(pythonPrg)
            env.Alias(kw.get('package'), pythonPrg)
            env.Alias(kw.get('package'), pyWrappers)
            env.Depends(pyWrappers, pythonPrg)
            env.Default(pythonPrg)
            env.Default(pyWrappers)
            env.Alias('to_install', pythonPrg)
            env.Alias('all', pythonPrg)
            env.Alias('all', pyWrappers)
            
        if 'wrapper_env' in kw:
            # user has passed in a list of (exename, envdict) tuples
            # to be registered in the construction environment and eventually
            # emitted into the wrapper scripts
            #print 'registerTargets: registering env dicts for %s' % list(x[0] for x in kw.get('wrapper_env'))
            env.Append( WRAPPER_ENV = kw.get('wrapper_env') )

        ##   COMMENT OUT  FOR PRODUCTION (requires SCons 1.2.0.d20090223
        ##   Windows Project files
        #if env['PLATFORM'] == "win32" and env['COMPILERNAME'] == "vc90":
        #    env.Tool('makeStudio', package=kw.get('package',''),
        #             libraryCxts=kw.get('libraryCxts',''),
        #             staticLibraryCxts=kw.get('staticLibraryCxts',''),
        #             swigLibraryCxts=kw.get('swigLibraryCxts',''),
        #             rootcintSharedCxts=kw.get('rootcintSharedCxts',''),
        #             rootcintStaticCxts=kw.get('rootcintStaticCxts',''),
        #             testAppCxts=kw.get('testAppCxts',''),
        #             binaryCxts=kw.get('binaryCxts',''),
        #             includes = kw.get('includes',''),
        #             data = kw.get('data',''),
        #             xml = kw.get('xml',''),
        #             pfiles = kw.get('pfiles',''),
        #             python = kw.get('python',''))

            
def exists(env):
    return 1;








