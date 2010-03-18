#
# addjvmarg.py : will set a JVM generic argument to one or all servers
#

# ToDo : - validate JVM arguments
#        - prettify the List output
#        - prettify the "interface"
#        - Be able to select not all but multiple servers to manage
def main():
  serverList = selserv("Select Server")
  print "Do you want to Delete or Add an argument?"
  print "A) Add a JVM argument"
  print "D) Delete a JVM argument"
  print "L) List JVM arguments (not yet fully implemented)"

  action = raw_input()
  if action == "A":
    actiontext = "add"
  elif action == "D":
    actiontext = "delete"
  elif action == "L":
    actiontext = "list"
  if action == "A" or action == "D":
    print "Specify the JVM argument to " + actiontext
    jvmarg = raw_input()
    print "You sepcified :" + jvmarg
  print ""
  print "Specify what JVM types to run this command for"
  print "C) Control Region"
  print "S) Servant Region"
  print "B) Servant and Control Region"
  type = raw_input()
  if type == "C":
    type = "Control"
  elif type == "S":
    type = "Servant"
  else:
    type = "Both"

  print "OK, here we go"


  for server in serverList:
    pos   = server.find("(")
    sname = "/Server:" + server[:pos] + "/"
    sid   = AdminConfig.getid(sname)
    pdefs = AdminConfig.list('ProcessDef', sid).split("\n")
    for pdef in pdefs:
      jvmType = AdminConfig.showAttribute(pdef,'processType')
      jvms = AdminConfig.list('JavaVirtualMachine',pdef).split("\n")
      for jvm in jvms:
        if action == "L":
          # List the stuff
          print AdminConfig.showAttribute(sid, "shortName") + " " + jvmType + " Region"
          print AdminConfig.showAttribute(jvm, "genericJvmArguments")
        elif action == "A" or action == "D":
          if (type == "Both" and (jvmType == "Servant" or jvmType == "Control")) or type == jvmType:
            origJVM = AdminConfig.showAttribute(jvm, "genericJvmArguments")
            if action == "A":
              newArgs = updateJVMArguments(jvmarg, origJVM)
              if newArgs != origJVM:
                log("ADD",jvmarg,AdminConfig.showAttribute(sid, "shortName"),jvmType)
            if action == "D":
              newArgs = removeJVMArgument(jvmarg, origJVM)
              if newArgs != origJVM and origJVM != "":
                log("DEL",jvmarg,AdminConfig.showAttribute(sid, "shortName"),jvmType)
            AdminConfig.modify(jvm, [["genericJvmArguments", newArgs]])

  if action == "A" or action == "D":
    # Now we save
    print "Saving configuration"
    AdminConfig.save()
    # And Sync
    print "Synchronizing changes with nodes"
    sync()

#
def sync():
  endResult='ja'
  nodeList=AdminControl.queryNames('type=NodeSync,*').split(lineSeparator)
  for node in nodeList:
    print 'Node '+node
    result=AdminControl.invoke(node,'sync')
    if result=='true':
      result='ja'
    else:
      result='nee'
      endResult='nee'
    print 'Synchronisatie succesvol: '+result
  if endResult=='ja':
    print 'Totale synchronisatie succesvol'
  else:
    print 'Fouten tijdens synchronisatie!'

def selserv(subtitle):
  # Our result
  result = []


  # Print the header
  print subtitle
  print "Select a server (or select all)"

  # Read all servers
  allservers = AdminTask.listServers("-serverType APPLICATION_SERVER").split("\n")

  # Init our 'selector'
  selopt = 0

  for server in allservers:
    pos   = server.find("(")
    sname = "/Server:" + server[:pos] + "/"
    sid   = AdminConfig.getid(sname)
    print str(selopt) + ") " + AdminConfig.showAttribute(sid, "shortName")
    selopt = selopt + 1

  print ""
  print "A) All Servers"
  print ">",
  answer = raw_input()
  if answer == "A":
    print "All Servers Selected"
    result = allservers
  else:
    print allservers[int(answer)] + " selected"
    result.append(allservers[int(answer)])

  return result

def updateJVMArguments(arg, jvmParms):
  # returns a new set of jvmArgs
  #

  # Sanity Check : is only one arg given?
  if arg.find(" ") <> -1:
    print "Speify only one argument"
    exit(1)

  # first see if our arg is key-value pair or not
  # for now we check on parms like -Dsomething=value and
  #                                -Dother:value
  # more key-value seperators can be added in the seperatorList below :)

  _kv = 'false'
  seperatorList = [":","="]

  for seperator in seperatorList:
    if arg.find(seperator) >= 0:
      _kv = seperator

  if _kv == 'false':
    # no fancy JVM argument
    _set = jvmParms.find(arg)
    if _set == -1:
      newArg = jvmParms + " " + arg


  if _kv <> 'false':
    # the argument is key-value pair
    _key   = arg[:arg.find(_kv)]      # determine key-value pair
    _value = arg[arg.find(_kv):]      # from given argument
    # is our key in jvmParms
    _parmpos = jvmParms.find(_key + _kv)
    if _parmpos >= 0:
      # find where the whole argument ends
      _endpos = jvmParms.find(" ",_parmpos)
      newArg = jvmParms[0:_parmpos] + arg
      if _endpos >= 0:
        # if there are more arguments we need to add them
        newArg = newArg + jvmParms[_endpos:]
    if _parmpos == -1:
      # not there so just add it at the end
      newArg = jvmParms + " " + arg

  # added niftyness : order args
  #if option == "sort":
  #  argList = newArg.split(" ")
  #  argList.sort()
  #  newArg = ""
  #  for arg in argList:
  #    newArg = newArg + arg + " "
  #  newArg.strip()
  newArg = newArg.strip()
  return newArg


def removeJVMArgument(toRemove, currentArgs):
  result = ""
  if currentArgs != None:
    origList = currentArgs.split(" ")
    for arg in origList:
      if arg <> toRemove:
        result = result + arg + " "
    result = result.strip() 

  return result


def log(action, argument, server, jvmType):
  print "INFO : " + action + " " + argument + " (" + server + "/" + jvmType + ")"

# en nu draaien :)
main()
