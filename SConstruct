# -*- python -*-
# $Header: /nfs/slac/g/glast/ground/cvs/SConsFiles/SConstruct,v 1.30 2009/09/30 18:17:09 glastrm Exp $
# Authors: Navid Golpayegani <golpa@slac.stanford.edu>, Joanne Bogart <jrb@slac.stanford.edu
# Version: SConsFiles-00-01-05

import os,platform,SCons,glob,re,atexit,sys,traceback,commands,subprocess
#########################
#   Global Environment  #
#########################

EnsureSConsVersion(1, 2, 0)
baseEnv=Environment()
baseEnv.Tool('generateScript')
baseEnv.Tool('doxygen')
baseEnv.Alias('NoTarget')
baseEnv.SourceCode(".", None)
variant = "Unknown"
baseEnv['OSNAME'] = "Unknown"
baseEnv['MACHINENAME'] = "Unknown"
baseEnv['ARCHNAME'] = "Unknown"
if baseEnv['PLATFORM'] == "posix":
    variant = platform.dist()[0]+platform.dist()[1]+"-"+platform.machine()+"-"+platform.architecture()[0]
    baseEnv['OSNAME'] = platform.dist()[0]+re.sub('\.\d+', '', platform.dist()[1])
    baseEnv['MACHINENAME'] = platform.machine()
    baseEnv['ARCHNAME'] = platform.architecture()[0]

if baseEnv['PLATFORM'] == "darwin":
    version = commands.getoutput("sw_vers -productVersion")
    cpu = commands.getoutput("arch")
    baseEnv['MACHINENAME'] = cpu
    if version.startswith("10.5"):
        variant="leopard-"
        baseEnv['OSNAME'] = "leopard"
    if version.startswith("10.4"):
        variant="tiger-"
        baseEnv['OSNAME'] = "tiger"
    variant+=cpu+"-"
    if cpu.endswith("64"):
        variant+="64bit"
        baseEnv['ARCHNAME'] = '64bit'
    else:
        variant+="32bit"
        baseEnv['ARCHNAME'] = '32bit'
if baseEnv['PLATFORM'] == "win32":
    variant = platform.release()+"-"+"i386"+"-"+platform.architecture()[0]
    baseEnv['WINDOWS_INSERT_MANIFEST'] = 'true'
    baseEnv['OSNAME'] = platform.release()
    baseEnv['MACHINENAME'] = 'i386'
    baseEnv['ARCHNAME'] = platform.architecture()[0]
	
baseEnv.AppendUnique(CPPDEFINES = ['SCons'])

AddOption('--compile-debug', dest='debug', action='store_true', help='Compile with debug flags')
AddOption('--compile-opt', dest='opt', action='store_true', help='Compile with optimization flags')
AddOption('--rm', dest='rm', action='store_true', help='Enable output helpful for RM output parsing')
AddOption('--ccflags', dest='ccflags', action='store', nargs=1, type='string', metavar='FLAGS', help='Compiler flags to pass to the C compiler')
AddOption('--cxxflags', dest='cxxflags', action='store', nargs=1, type='string', metavar='FLAGS', help='Compiler flags to pass to the C++ compiler')
AddOption('--variant', dest='variant', action='store', nargs=1, type='string', help='The variant to use instead of the computed one')
AddOption('--supersede', dest='supersede', action='store', nargs=1, type='string', default='.', metavar='DIR', help='Directory containing packages superseding installed ones. Relative paths not supported!')
AddOption('--exclude', dest='exclude', action='append', nargs=1, type='string', metavar='DIR', help='Directory containing a SConscript file that should be ignored.')
AddOption('--user-release', dest='userRelease', nargs=1, type='string', action='store', metavar='FILE', help='Creates a compressed user release and stores it in FILE')
AddOption('--source-release', dest='sourceRelease', nargs=1, type='string', action='store', metavar='FILE', help='Creates a compressed source release and stores it in FILE')
AddOption('--devel-release', dest='develRelease', nargs=1, type='string', action='store', metavar='FILE', help='Creates a compressed developer release and stires it in FILE')
AddOption('--doxygen', dest='doxygenOutput', nargs=1, type='string', default='${HTML-OUTPUT}', action='store', metavar='DIRECTORY', help='Sets up Doxygen configuration to write html in DIRECTORY')

if baseEnv['PLATFORM'] != 'win32':
    AddOption('--with-cc', dest='cc', action='store', nargs=1, type='string', metavar='COMPILER', help='Compiler to use for compiling C files')
    AddOption('--with-cxx', dest='cxx', action='store', nargs=1, type='string', metavar='COMPILER', help='Compiler to user for compiling C++ files')
    AddOption('--32bit', dest='bits', action='store_const', const='32', help='Force 32bit compiles even on 64bit machines')
    AddOption('--64bit', dest='bits', action='store_const', const='64', help='Force 64bit compiles even on 32bit machines')
else:
    AddOption('--vc7', dest='vc', action='store_const', const='7.1', help='Use the Visual C++ 7.1 compiler')
    AddOption('--vc8', dest='vc', action='store_const', const='8.0', help='Use the Visual C++ 8.0 compiler')
    AddOption('--vc9', dest='vc', action='store_const', const='9.0', help='Use the Visual C++ 9.0 compiler')


if baseEnv['PLATFORM'] != 'win32':
    if baseEnv.GetOption('cc'):
        baseEnv.Replace(CC = baseEnv.GetOption('cc'))
        pipe = SCons.Action._subproc(baseEnv, [baseEnv['CC'], '-dumpversion'], stdin = 'devnull', stderr = 'devnull', stdout = subprocess.PIPE)
        line = pipe.stdout.read().strip()
        if line:
            baseEnv['CCVERSION'] = line
    if baseEnv.GetOption('cxx'):
        baseEnv.Replace(CXX = baseEnv.GetOption('cxx'))
        pipe = SCons.Action._subproc(baseEnv, [baseEnv['CXX'], '-dumpversion'],stdin = 'devnull', stderr = 'devnull', stdout = subprocess.PIPE)
        line = pipe.stdout.read().strip()
        if line:
            baseEnv['CXXVERSION'] = line
    if baseEnv.GetOption('bits') == '32':
        baseEnv.AppendUnique(CCFLAGS = ['-m32'])
        baseEnv.AppendUnique(LINKFLAGS = ['-m32'])
    if baseEnv.GetOption('bits') == '64':
        baseEnv.AppendUnique(CCFLAGS = ['-m64'])
        baseEnv.AppendUnique(LINKFLAGS = ['-m64'])
else:
    if baseEnv.GetOption('vc'):
        baseEnv['MSVS_VERSION'] = baseEnv.GetOption('vc')
        baseEnv.Tool('msvs')
        Tool('msvc')(baseEnv)

if baseEnv['PLATFORM'] == "win32":
    ### Uncomment next line when local msvs is installed
    ### import msvs
    ### For now..
    import SCons.Tool.msvs as msvs
    num,suite = msvs.msvs_parse_version(baseEnv['MSVS_VERSION'])
    compiler = 'vc'+''.join(str(num).split('.')[0:2])
    # visual_variant will be used as working directory in VS project files
    visual_variant = "Visual-" + compiler
else:
    compiler = 'gcc'+''.join(baseEnv['CXXVERSION'].split('.')[0:2])

baseEnv['COMPILERNAME'] = compiler
variant += "-" + compiler

if baseEnv.GetOption('debug'):
    if baseEnv['PLATFORM'] == 'win32':
        baseEnv.AppendUnique(CPPDEFINES = ['_DEBUG'])
        baseEnv.AppendUnique(CCFLAGS = '/Od')
        visual_variant +=  "-Debug"
    else:
        baseEnv.AppendUnique(CCFLAGS = '-g')
    variant+="-Debug"
    
if baseEnv.GetOption('opt'):
    if baseEnv['PLATFORM'] == 'win32':
        baseEnv.AppendUnique(CCFLAGS = "/O2")
        visual_variant += "-Optimized"
    else:
        baseEnv.AppendUnique(CCFLAGS = '-O2')
    variant+='-Optimized'
    
if baseEnv.GetOption('ccflags'):
    baseEnv.AppendUnique(CCFLAGS = baseEnv.GetOption('ccflags'))
if baseEnv.GetOption('cxxflags'):
    baseEnv.AppendUnique(CXXFLAGS = baseEnv.GetOption('cxxflags'))
if baseEnv.GetOption('variant'):
    variant = baseEnv.GetOption('variant')
override = baseEnv.GetOption('supersede')
SConsignFile(os.path.join(override,'.sconsign.dblite'))
baseEnv['VARIANT'] = variant

Export('baseEnv')

#########################
#OS Specific Compile Opt#
#########################
if baseEnv['PLATFORM'] == "win32":
    baseEnv.AppendUnique(CPPDEFINES = ['WIN32','_USE_MATH_DEFINES'])

    baseEnv.AppendUnique(CCFLAGS = "/EHsc")
    baseEnv.AppendUnique(CCFLAGS = "/FC")    # helps with debugging
    baseEnv.AppendUnique(CCFLAGS = "/W3") # warning level 3
    baseEnv.AppendUnique(CCFLAGS = "/wd4068")
    baseEnv.AppendUnique(CCFLAGS = "/wd4244") # disable warning C4244: 'initializing' : conversion from 'const double' to 'float'
    baseEnv.AppendUnique(CCFLAGS = "/wd4305") # disable warning C4305: 'initializing' : truncation from double to float
    baseEnv.AppendUnique(CCFLAGS = "/wd4290") # disable warning C4290: C++ exception specification ignored except to indicate a function is not __declspec(nothrow)
    baseEnv.AppendUnique(CCFLAGS = "/wd4800") # disable warning C4800: 'type' : forcing value to bool 'tru' or 'false' (performance warning)
    ## baseEnv.AppendUnique(CCFLAGS = "/Zm500") probably not necessary
    baseEnv.AppendUnique(CCFLAGS = "/Z7")
    baseEnv.AppendUnique(CCFLAGS = "/GR")
    baseEnv.AppendUnique(LINKFLAGS = "/SUBSYSTEM:CONSOLE")
    baseEnv.AppendUnique(LINKFLAGS = "/NODEFAULTLIB:LIBCMT")

    if baseEnv.GetOption('debug'):
        baseEnv.AppendUnique(CCFLAGS = "/MDd")
        baseEnv.AppendUnique(CCFLAGS = "/LDd")
        baseEnv.AppendUnique(CCFLAGS = "/Ob0")

    else:
        baseEnv.AppendUnique(CCFLAGS = "/MD")
        baseEnv.AppendUnique(CCFLAGS = "/LD")
        baseEnv.AppendUnique(CCFLAGS = "/Ob2")

    # Disable compiler warning number 4812 having to do with
    # obsolete form of explicit constructor specialization
    if (baseEnv['MSVS_VERSION'] == "8.0") or (baseEnv['MSVS_VERSION']=="9.0") :
        baseEnv.AppendUnique(CPPDEFINES = ['_CRT_SECURE_NO_WARNINGS'])
        baseEnv.AppendUnique(CPPFLAGS = "/wd4812")
        if baseEnv.GetOption('debug'):
            baseEnv.AppendUnique(LINKFLAGS = "/DEBUG")
            baseEnv.AppendUnique(LINKFLAGS = "/ASSEMBLYDEBUG")

    # Used as Studio working directory
    baseEnv['VISUAL_VARIANT'] = visual_variant
    
            
else:
    baseEnv.AppendUnique(CXXFLAGS = "-fpermissive")

if baseEnv['PLATFORM'] == "posix":
    if platform.machine() == "x86_64":
        baseEnv.AppendUnique(CCFLAGS = "-fPIC")
    baseEnv.AppendUnique(CPPDEFINES = ['TRAP_FPE'])

if baseEnv['PLATFORM'] == "darwin":
    baseEnv.AppendUnique(SHLINKFLAGS = ["-Wl,-install_name", "-Wl,${TARGET.file}"])
        
#########################
#  Project Environment  #
#########################
baseEnv.Append(LIBDIR         = Dir(override).Dir('lib').Dir(variant))
baseEnv.Append(BINDIR         = Dir(override).Dir('exe').Dir(variant))
baseEnv.Append(SCRIPTDIR      = Dir(override).Dir('bin').Dir(variant))
baseEnv.Append(INCDIR         = Dir(override).Dir('include'))
baseEnv.Append(PFILESDIR      = Dir(override).Dir('syspfiles'))
baseEnv.Append(DATADIR        = Dir(override).Dir('data'))
baseEnv.Append(XMLDIR         = Dir(override).Dir('xml'))
baseEnv.Append(TOOLDIR        = Dir(override).Dir('sconsTools'))
baseEnv.Append(TESTDIR        = baseEnv['BINDIR'])
baseEnv.Append(TESTSCRIPTDIR  = baseEnv['SCRIPTDIR'])
baseEnv.Append(PYTHONDIR      = Dir(override).Dir('python'))
baseEnv.Append(DOCDIR         = Dir(override).Dir('Doxygen'))
baseEnv.Append(DEFAULTDOCFILE = Dir('.').Dir('Doxygen').File('Default'))
baseEnv.Append(DOXYGENOUTPUT  = baseEnv.GetOption('doxygenOutput'))
baseEnv['CONFIGURELOG']       = str(Dir(override).File("config.log"))
baseEnv['CONFIGUREDIR']       = str(Dir(override).Dir(".sconf_temp"))
baseEnv.Append(CPPPATH = ['.'])
baseEnv.Append(CPPPATH = ['src'])
baseEnv.Append(CPPPATH = [baseEnv['INCDIR']])
baseEnv.Append(LIBPATH = [baseEnv['LIBDIR']])
baseEnv.AppendUnique(CPPPATH = os.path.join(os.path.abspath('.'),'include'))
baseEnv.AppendUnique(LIBPATH = os.path.join(os.path.abspath('.'),'lib',variant))
## STUDIODIR is where project and solution files will go
if baseEnv['PLATFORM'] == 'win32':
    baseEnv.Append(STUDIODIR = Dir(override).Dir('studio').Dir(variant))
                   
##################
# Create release #
##################
if baseEnv.GetOption('userRelease'):
    if baseEnv['PLATFORM'] != 'win32':
        baseEnv['TARFLAGS']+=' -z'
        baseEnv.Default(baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['LIBDIR']))
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['BINDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['SCRIPTDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['INCDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['PFILESDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['DATADIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['XMLDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['TOOLDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['TESTDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['TESTSCRIPTDIR'])
        baseEnv.Tar(baseEnv.GetOption('userRelease'), baseEnv['PYTHONDIR'])
    else:
        baseEnv.Default(baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['LIBDIR']))
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['BINDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['SCRIPTDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['INCDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['PFILESDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['DATADIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['XMLDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['TOOLDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['TESTDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['TESTSCRIPTDIR'])
        baseEnv.Zip(baseEnv.GetOption('userRelease'), baseEnv['PYTHONDIR'])
    Return()

if baseEnv.GetOption('sourceRelease'):
    if baseEnv['PLATFORM'] != 'win32':
        baseEnv['TARFLAGS']+=' -z'
        for exclude in (baseEnv['BINDIR'].path, baseEnv['SCRIPTDIR'].path, baseEnv['INCDIR'].path, baseEnv['PFILESDIR'].path,
                        baseEnv['DATADIR'].path, baseEnv['XMLDIR'].path, baseEnv['TOOLDIR'].path, baseEnv['TESTDIR'].path,
                        baseEnv['TESTSCRIPTDIR'].path, baseEnv['PYTHONDIR'].path, baseEnv['LIBDIR'].path, 'build'):
            baseEnv['TARFLAGS']+='--exclude '+exclude
        baseEnv.Default(baseEnv.Tar(baseEnv.GetOption('sourceRelease'), glob.glob('*')))
    else:
        for exclude in (baseEnv['BINDIR'].path, baseEnv['SCRIPTDIR'].path, baseEnv['INCDIR'].path, baseEnv['PFILESDIR'].path,
                                                baseEnv['DATADIR'].path, baseEnv['XMLDIR'].path, baseEnv['TOOLDIR'].path, baseEnv['TESTDIR'].path,
                        baseEnv['TESTSCRIPTDIR'].path, baseEnv['PYTHONDIR'].path, baseEnv['LIBDIR'].path, 'build'):
            baseEnv['ZIPFLAGS']+='-x '+exclude
        baseEnv.Default(baseEnv.Zip(baseEnv.GetOption('sourceRelease'), glob.glob('*')))
    Return()

if baseEnv.GetOption('develRelease'):
    if baseEnv['PLATFORM'] != 'win32':
       baseEnv['TARFLAGS'] += ' -z'
       baseEnv['TARFLAGS'] += ' --exclude build'
       baseEnv.Default(baseEnv.Tar(baseEnv.GetOption('develRelease'), glob.glob('*')))
    else:
        baseEnv['ZIPFLAGS'] += '-x build'
        baseEnv.Default(baseEnv.Zip(baseEnv.GetOption('develRelease'), glob.glob('*')))
    Return()

#########################
#  External Libraries   #
#########################
allExternals = SConscript('allExternals.scons')
usedExternals = SConscript('externals.scons', exports = 'allExternals')
SConscript('processExternals.scons', exports = 'allExternals usedExternals')

############################
# Package Specific Options #
############################
SConscript('package.scons')

def listFiles(files, **kw):
    allFiles = []
    for file in files:
        globFiles = Glob(file)
        newFiles = []
        for globFile in globFiles:
	    if 'recursive' in kw and kw.get('recursive') and os.path.isdir(globFile.srcnode().abspath) and os.path.basename(globFile.srcnode().abspath) != 'CVS':
	        allFiles+=listFiles([str(Dir('.').srcnode().rel_path(globFile.srcnode()))+"/*"], recursive = True)
	    if os.path.isfile(globFile.srcnode().abspath):
	        allFiles.append(globFile)
    return allFiles

Export('listFiles')

if not baseEnv.GetOption('help'):
    directories = [override]
    packages = []
    # Add pkgs to package list and add pkgs to tool path if they have one
    while len(directories)>0:
        directory = directories.pop(0)
        members = os.listdir(directory)
        # filter out non-directories
        listed = [e for e in members if os.path.isdir(os.path.join(directory,e))]
        listed.sort()
        pruned = []
        # Remove excluded directories
        if not baseEnv.GetOption('exclude') == None:
	    for excluded in baseEnv.GetOption('exclude'):
	        if excluded in listed:
		    listed.remove(excluded)

	# Remove duplicate packages
	while len(listed)>0:
	    curDir = listed.pop(0)
	    package = re.compile('-.*$').sub('', curDir)
	    while len(listed)>0 and re.match(package+'-.*', listed[0]):
	        curDir = listed.pop(0)
	    pruned.append(curDir)

        # Check if they contain SConscript and tools
        for name in pruned:
            package = re.compile('-.*$').sub('',name)
            if not name in ['build', 'CVS', 'src', 'cmt', 'mgr', 'data', 'xml', 'pfiles', 'doc', 'bin', 'lib']:
                fullpath = os.path.join(directory,name)
                if os.path.isdir(fullpath):
                    directories.append(fullpath)
                    if os.path.isfile(os.path.join(fullpath,"SConscript")):
                        packages.append(fullpath)
                    if os.path.isfile(os.path.join(fullpath, package+'Lib.py')):
                        SCons.Tool.DefaultToolpath.append(os.path.abspath(fullpath))

    if not override == '.':
        SCons.Tool.DefaultToolpath.append(os.path.abspath(str(Dir('.').Dir('sconsTools'))))

    Export('packages')

    for pkg in packages:
        try:
	    baseEnv.SConscript(os.path.join(pkg,"SConscript"),
                               build_dir = os.path.join(pkg, 'build', variant))
	except Exception, inst:
	    print "scons: Skipped "+pkg.lstrip(override+os.sep)+" because of exceptions: "+str(inst)
	    traceback.print_tb(sys.exc_info()[2])

    if baseEnv.GetOption('clean'):
        baseEnv.Default('test')

setupScript = baseEnv.GenerateSetupScript()
baseEnv.Default(setupScript)
baseEnv.Alias('all', setupScript)
baseEnv.Alias('setup', setupScript)

def print_build_failures():
    from SCons.Script import GetBuildFailures
    print "scons: printing failed nodes"
    for bf in GetBuildFailures():
        if str(bf.action) != "installFunc(target, source, env)":
	    print bf.node
    print "scons: done printing failed nodes"

atexit.register(print_build_failures)
