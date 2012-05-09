# -*- python -*-
#  $Id: writeAllSln.py,v 1.1 2012/05/01 02:53:19 jrb Exp $
#
#  Delete old all.sln if there is one
#  Read in *.sln for specified directory (defaults to "."), saving
#        - some boilerplate which is in all sln files and needs to go in our output
#        - dict. of project definitions, keyed by project file name (excluding .vcproj)
#        - dict. of per-project stuff appearing in Global postSolution section
#
#  Write out all.sln, using all of above
import os, os.path, sys, re

class allSln(object):

    def __init__(self):
        self.projectDict = {}
        self.postSolutionDict = {}
        self.header = []

        self.global_presolution1 = []
        self.global_presolution2 = []
        self.global_postsolution_header = ""

        # By default include all projects.  
        self.pkgname = ""

        # Define pattern for first line of Project definition, picking out name (e.g. CalibSvcLib) and
        # unique id, which appears to be of form xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx where each x is
        # a hex digit.
        self.projPat =  re.compile('Project\(".*\s=\s"(.+)"\,\s".*"\,\s"\{([0-9,A-F,-]*)\}"')
        self.endProjPat = re.compile('^EndProject\s*$')
        self.gProjPat = re.compile('\w*\{([0-9,A-F,-]*)\}.*')

    def readProject(self, fp, firstline):
        #  find and save project name and project id in firstline
        mobj = self.projPat.match(firstline)
        if mobj == None:
           print "cannot parse supposed Project definition starting ",
           print firstline
           exit(1)
        #else:
        #    print "match groups are ", mobj.group(1), mobj.group(2)

        #  Save all lines through line with contents "EndProject" in projLines
        projLines = [firstline]
        lenp = len(firstline)

        try:
            ln = fp.readline()
            lenp += len(ln)
        except:
            print "readline inside readProject failed"
            exit(1)

        while ln[:10] != "EndProject":
            projLines.append(ln)
            ln = fp.readline()
            lenp += len(ln)

        projLines.append(ln)

        # Make dictionary entry (a triple) keyed by project name if
        #   (we're including all projects ) OR (project name ends in "Lib") OR
        #   (pkgname is non-null and project name = pkgname or "test_" + package name
        useIt = (self.pkgname == "")
        projName = mobj.group(1)

        if (not useIt) and ((projName[len(projName)-3:] == "Lib") or (projName == self.pkgname) or
                             (projName == "test_" + self.pkgname)): useIt = True
        if projName not in self.projectDict:
            if useIt: self.projectDict[projName] = [projName, mobj.group(2), projLines, lenp]
        else:
            # see if new entry is shorter.  If so, replace old with it
            if self.projectDict[projName][3] > lenp:
                if useIt: self.projectDict[projName] = [projName, mobj.group(2), 
                                                        projLines, lenp]

        # read one more line and return it
        #print "Done parsing project definition for ",  mobj.group(1)
        next = fp.readline()     

        return next

    def readGlobal(self, fp, firstGlobal):
        try:
            next = fp.readline()
        except:
            print "read inside readGlobal failed"
            sys.stdout.flush()
            exit(1)
        
        if next.rfind("EndGlobal") != -1:
            print "found EndGlobal prematurely"
            return 0
        
        if next.rfind("preSolution") != -1:
            sys.stdout.flush()
            if len(self.global_presolution1) == 0:
                self.global_presolution1.append(next)
                try:
                    next = fp.readline()
                    self.global_presolution1.append(next)
                    next = fp.readline()
                    self.global_presolution1.append(next)
                except:
                    print "failed to read all of preSolution1"
                    sys.stdout.flush()
                    exit(1)
            else:
                try:
                    fp.readline()
                    fp.readline()
                except:
                    print "failed to read remainder of presolution1"
                    sys.stdout.flush()
                    exit(1)

            try:
                next = fp.readline()
            except:
                print "failed read past preSolution1"
                sys.stdout.flush()
                exit(1)
                
            sys.stdout.flush()
            
        if next.rfind("postSolution") != -1:
            if self.global_postsolution_header == "":
                self.global_postsolution_header = next

            # read in a line.  Either it signifies end of section or it's the start 
            # of a 2-line entry a particular project.  Store the two lines in a dict, 
            # keyed by project id
            next = fp.readline()

            while next.rfind("EndGlobalSection") == -1:
                plist = [next]
                mobj = self.gProjPat.search(next)
                if mobj == None:
                    print "Bad global postSolution section"
                    sys.stdout.flush()
                    return 1

                plist.append(fp.readline())
                self.postSolutionDict[mobj.group(1)] = plist
                next = fp.readline()

            next = fp.readline()

        sys.stdout.flush()
        if next.rfind("preSolution") != -1:
            if self.global_presolution2 == []:
                self.global_presolution2.append(next)
                self.global_presolution2.append(fp.readline())
                self.global_presolution2.append(fp.readline())
            else:
                fp.readline()
                fp.readline()

            next = fp.readline()

        if next[:9] == "EndGlobal":
            return 0
        else : return 1
        
    def readSln(self, fp):
        h1 = fp.readline()
        h2 = fp.readline()

        if self.header == []: self.header = [h1, h2]

        next = fp.readline()

        
        while next[:8] == "Project(":
            next = self.readProject(fp, next)

        # Next should be Global
        if next[:6] == "Global":
            return self.readGlobal(fp, next)
        elif next != '':
            print "Unexpected section ", next, " in input solution file"
            fp.close()
            exit(1)
        else:
            return 0
        
    def writeAllSln(self, path):
        print "Writing ", path
        try:
            fp = open(path, 'w')
        except:
            print "Cannot open ", path, " for write"
            exit(1)

        try:
            fp.write(self.header[0])
            fp.write(self.header[1])

            # Write out all the projects
            for k in self.projectDict:
                for ln in self.projectDict[k][2]:
                    fp.write(ln)

            fp.write("Global\n")
            for ln in self.global_presolution1:
                fp.write(ln)

            fp.write(self.global_postsolution_header)
            for ps in self.postSolutionDict:
                fp.write(self.postSolutionDict[ps][0])
                fp.write(self.postSolutionDict[ps][1])

            fp.write("\tEndGlobalSection\n")
            for ln in self.global_presolution2:
                fp.write(ln)

            fp.write("EndGlobal\n")
        except:
            print "Failure writing to ", path
        finally:
            fp.close()

# main
# We assume we're in the same directory as the solution files

obj = allSln()

if len(sys.argv) > 1:
    sdir = sys.argv[1]
else:
    sdir = (".")

if len(sys.argv) > 2:
    obj.pkgname = sys.argv[2]

outfile = "all" + obj.pkgname + ".sln"
# get rid of old all.sln if there is one
try:
    os.remove(os.path.join(sdir, outfile))
except:
    # Don't care if it fails; probably just means the file didn't exist
    pass


studiofiles = os.listdir(sdir)

readAFile = True
for fname in studiofiles:
    if fname[len(fname)-4:] == ".sln":
        if fname[0:2] != "all":    # we use it
            try:
                #print "Found file ", fname
                f = open(os.path.join(sdir, fname))
                obj.readSln(f)
                f.close()
            except:
                print "Unable to read file ", fname
                if f != None: f.close()

obj.writeAllSln(os.path.join(sdir, outfile))
exit(0)

