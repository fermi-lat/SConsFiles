#  $Id: registerTargets.py,v 1.18 2012/04/27 18:51:31 jrb Exp $
import os, pprint, sys, os.path
from SCons.Script import *
from fermidebug import fdebug
import pprint

if sys.platform == 'win32':
    from makeStudio import *
    
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
##        testAppCxts  - list of 2-item lists [program node,env]
##        binaryCxts  - list of  2-item lists [program node,env]
##        objects  - list of  2-item lists [object node,env]
##        includes - list of file paths
##        topInclude - put includes under $INST_DIR/include/topInclude
##                     or just $INST_DIR/include if special value "*NONE*" is supplied
##                     defaults to package.  
##        data     - list of file paths
##        xml      - list of file paths
##        jo       - list of file paths (applies only to GlastRelease)
##        pfiles   - lift of file paths
##        python   - list of file paths. Will be installed in python subdir,
##                   preserving directory organization
##        wrappedPython - list of python programs to be installed and wrapped
##        wrapper_env
##


def generate(env, **kw):
    if kw.get('package', '') != '':
        if env['PLATFORM'] == "win32": instFiles = []
        pkgname = kw.get('package')
        if pkgname == "*ALL*":
            env.Tool('makeStudio', pkgname)
            return

        pkgtopdir = str(env.Dir('.').srcnode())
        #fdebug('Entered registerTargets:generate for package %s' % pkgname)
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
            #fdebug("getCxtList(%s) found list of length %s" % (argname, len(val)) )
            return val

        # Libraries are handled in two ways depending on whether they
        # build just a .lib or .lib, .dll, etc.
        # Only makeStudio has to distinguish all categories
        cx = []
        if env['PLATFORM'] != "win32":
            cx += getCxtList('libraryCxts')
            cx += getCxtList('rootcintSharedCxts')
            cx += getCxtList('swigLibraryCxts')
        cx += getCxtList('staticLibraryCxts')
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

        # On windows, shared libraries are handled specially.
        # .lib installed target depends on install of the rest
        if env['PLATFORM'] == "win32":
            cx = []
            cx += getCxtList('libraryCxts')
            cx += getCxtList('rootcintSharedCxts')
            cx += getCxtList('swigLibraryCxts')
            winlibs = []

            for c in cx:                # find .lib node
                nondotlib = []
                dotlib = []
                for libentry in c[0]:
                    fname = (os.path.split(libentry.path))[1]
                    cmps = fname.split(".")
                    if (len(cmps) == 2) and (cmps[1] == "lib"):
                        dotlib.append(libentry)
                    else:
                        nondotlib.append(libentry)

                nondotinst = env.Install(env['LIBDIR'], nondotlib)
                dotlibinst = env.Install(env['LIBDIR'], dotlib)
                env.Depends(dotlibinst, nondotinst)
                winlibs.append(nondotinst)
                winlibs.append(dotlibinst)
                
            if winlibs != []:    
                env.Alias(pkgname, winlibs)
                env.Alias(pkgname+'-libraries', winlibs)
                env.Default(winlibs)
                env.Alias('libraries', winlibs)
                env.Alias('all', winlibs)
                    
        cxts = kw.get('binaryCxts','')
        if cxts != '':
            #fdebug('found %s binaries for pkg %s' % (len(cxts),pkgname))
            nodes = []
            for x in cxts:
                nodes.append(x[0])
            binaries = env.Install(env['BINDIR'], nodes)
            exes = []
            for bin in binaries:
                if env['PLATFORM'] == 'win32':
                    if  (str(bin.path)).find("manifest") == -1:
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

        objs = kw.get('objects','')
        if objs != '':
            #fdebug('found %s objects for pkg %s' % (len(objs),pkgname))
            nodes = []
            for x in objs:
                nodes.append(x[0])
            if len(objs) > 0:
                installedObjs = env.Install(env['LIBDIR'], nodes)
                env.Alias('objects', installedObjs)
                env.Alias(pkgname, installedObjs)
                env.Alias('all', installedObjs)

        if kw.get('includes', '') != '':
	    if env['PLATFORM'] == 'win32': instIncludes = []

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
                if topInc == '*NONE*':
                    includes = env.Install(env['INCDIR'].Dir(installPath), header)
                else:
		    if env['PLATFORM'] == 'win32':
		      dstHeader=str(env['INCDIR'].Dir(topInc).Dir(installPath))
		      instIncludes.append([str(header), dstHeader])
                    includes = env.Install(env['INCDIR'].Dir(topInc).Dir(installPath),
                                           header)
                env.Alias(kw.get('package'), includes)
                env.Default(includes)
                env.Alias('to_install', includes)
                env.Alias('includes', includes)
                env.Alias('all', includes)
            if env['PLATFORM'] == 'win32':
                instFiles += instIncludes
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
            if env['PLATFORM'] == 'win32' : instData = []
            for dfile in kw.get('data'):
                dfile = env.File(str(dfile))
                splitFile = str(env.Dir('.').srcnode().rel_path(dfile.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
                installPath = os.path.dirname(installPath)
                if env['PLATFORM'] == 'win32':
                    dstDir = str(env['DATADIR'].Dir(kw.get('package')).Dir(installPath))
                    instData.append([str(dfile), dstDir])
                data = env.Install(env['DATADIR'].Dir(kw.get('package')).Dir(installPath), dfile)
                env.Alias(pkgname, data)
                env.Default(data)
                env.Alias('to_install', data)
                env.Alias('all', data)
            if env['PLATFORM'] == 'win32' : instFiles += instData
        if kw.get('xml', '') != '':
            if env['PLATFORM'] == 'win32' : instXml = []
            for xfile in kw.get('xml'):
                xfile = env.File(str(xfile))
                splitFile = str(env.Dir('.').srcnode().rel_path(xfile.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
                installPath = os.path.dirname(installPath)
                if env['PLATFORM'] == 'win32':
                    instXml.append([str(xfile), str(env['XMLDIR'].Dir(pkgname).Dir(installPath))])
                xml = env.Install(env['XMLDIR'].Dir(kw.get('package')).Dir(installPath), xfile)
                env.Alias(kw.get('package'), xml)
                env.Default(xml)
                env.Alias('to_install', xml)
                env.Alias('all', xml)
            if env['PLATFORM'] == 'win32' : instFiles += instXml
        if kw.get('jo', '') != '':
            if env['PLATFORM'] == 'win32' : instJo = []
            for jfile in kw.get('jo'):
                jfile = env.File(str(jfile))
                splitFile = str(env.Dir('.').srcnode().rel_path(jfile.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
		# Assumption is that all jo paths start with 'src', and
		# that this should not be propagated to install area
                # Uncomment to  *not* strip off first path component
                #installPath = os.path.normpath(os.path.join(parts[1],
                #                                            installPath))
                installPath = os.path.dirname(installPath)
                jobOptions = env.Install(env['JODIR'].Dir(kw.get('package')).Dir(installPath), jfile)
                if env['PLATFORM'] == 'win32' :
                    instJo.append([str(jfile), str(env['JODIR'].Dir(pkgname).Dir(installPath))])
                env.Alias(kw.get('package'), jobOptions)
                env.Default(jobOptions)
                env.Alias('to_install', jobOptions)
                env.Alias('all', jobOptions)
            if env['PLATFORM'] == 'win32' : instFiles += instJo
        if kw.get('python', '') != '':
            #python = env.Install(env['PYTHONDIR'], kw.get('python'))
            if env['PLATFORM'] == 'win32' : instPy = []
            for file in kw.get('python'):
                file = env.File(str(file))
                splitFile = str(env.Dir('.').srcnode().rel_path(file.srcnode()))
                installPath = ''
                while os.path.split(splitFile)[0] != '':
                    parts = os.path.split(splitFile)
                    splitFile = parts[0]
                    installPath = os.path.normpath(os.path.join(parts[1], installPath))
                installPath = os.path.dirname(installPath)
                python = env.Install(env['PYTHONDIR'].Dir(installPath), file)
                if env['PLATFORM'] == 'win32' : 
                    instPy.append([str(file), str(env['PYTHONDIR'].Dir(installPath))])
                env.Alias(kw.get('package'), python)
                env.Default(python)
                env.Alias('to_install', python)
                env.Alias('all', python)
            if env['PLATFORM'] == 'win32' : instFiles += instPy
        if kw.get('wrappedPython', '') != '':
            fdebug("Non-null set of python scripts to be wrapped")
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
### NOTE!!! Need to add something to makeStudio for job options
### NOTE #2!!!    and for objects
        if sys.platform=='win32':
            if env['PLATFORM'] == "win32" and env['COMPILERNAME'] == "vc90":
                # In special case where rootcint lib is first project
                # encountered, directory might not exist
                if not os.path.exists(str(env['STUDIODIR'])):
                    Execute(Mkdir(env['STUDIODIR']))
                # Clearly mark dest as directory
                for p in instFiles: 
                    p[1] += "\\"
                env.Tool('makeStudio', package=kw.get('package',''),
                         libraryCxts=kw.get('libraryCxts',''),
                         staticLibraryCxts=kw.get('staticLibraryCxts',''),
                         swigLibraryCxts=kw.get('swigLibraryCxts',''),
                         rootcintSharedCxts=kw.get('rootcintSharedCxts',''),
                         rootcintStaticCxts=kw.get('rootcintStaticCxts',''),
                         testAppCxts=kw.get('testAppCxts',''),
                         binaryCxts=kw.get('binaryCxts',''),
                         includes = kw.get('includes',''),
                         installFiles = instFiles,
                         data = kw.get('data',''),
                         xml = kw.get('xml',''),
                         pfiles = kw.get('pfiles',''),
                         python = kw.get('python',''))

            
def exists(env):
    return 1;








