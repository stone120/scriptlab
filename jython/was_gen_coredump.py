def gen_javacore(servername):
        objParms='type=JVM,process=' + servername + ',*'
        objNameString = AdminControl.completeObjectName(objParms)
        AdminControl.invoke(objNameString, 'dumpThreads')
 
def gen_javadump(servername):
        objParms='type=JVM,process=' + servername + ',*'
        objNameString = AdminControl.completeObjectName(objParms)
        AdminControl.invoke(objNameString, 'generateHeapDump')
 
def gen_coredump(servername):
        objParms='type=JVM,process=' + servername + ',*'
        objNameString = AdminControl.completeObjectName(objParms)
        AdminControl.invoke(objNameString, 'generateHeapDump')
        AdminControl.invoke(objNameString, 'dumpThreads')
 
#--------------------------------------------------------------------------------
# program start
argLen = len(sys.argv)
print 'args count: ' + str(argLen)
 
if argLen < 1:
  print 'arguments invalid, expected 2, actual ' + str(argLen)
  sys.exit()
 
if argLen == 1:
        gen_coredump(sys.argv[0])
        sys.exit()
 
if int(sys.argv[0]) == 1:
        gen_javacore(sys.argv[1])
else:
        gen_javadump(sys.argv[1])