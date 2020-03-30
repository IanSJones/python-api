#!/bin/python

import sys, getopt, purestorage, json, re
# We need the following to prevent a security warning
import urllib3
urllib3.disable_warnings()
# import requests 
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def usage():
   print '{} [ -a | --array ] <array_name> [ -p | --password ] <api token> [ -f | --function ] <function name> [-v | --verbose]'.format(sys.argv[0])
   print 'where <function name> can be:'
   print '      list_luns [-l | --lun_name] <comma separated list of lun names (no spaces!)>'
   print '      list_snapshot_luns [-l | --lun_name] <comma separated list of lun names (no spaces!)>'
   print '      list_all_luns [-l | --lun_name] <comma separated list of lun names (no spaces!)> (lists luns and snapshot luns)'
   print '      list_deleted_luns'
   print '      list_hosts [-h | --host_name] <comma separated list of hostnames (no spaces!)>'
   print '         If you specify the hostname you will see the LUNs presented to the host(s)'
   print '         If you do not specify a hostname you will see all hostnames, groups and WWNs'
   print '      list_hostgroups [ -g | --group_name ] [-v]'
   print ''
   print '      create_lun [-l | --lun_name] <lun name> [-s | --lun_size] <lun size>'
   print '                                                      where <lun size> can be in G or T (eg. 1T, 20G)'
   print '      extend_lun [-l | --lun_name] <lun name> [-s | --lun_size] <lun size>'
   print '                                                      where <lun size> can be in G or T (eg. 1T, 20G)'
   print '      create_host [ -h | --host_name ] <hostname> [ -w | --wwn ] <comma separated list of WWNs (no spaces!)>'
   print '      create_hostgroup [ -g | --group_name ] <hostgroup_name>'
   print ''
   print '      add_host_to_hostgroup [ -h | --host_name ] <comma separated list of hostnames (no spaces!)> [ -g | --group_name ] <hostgroup_name>'
   print '      add_lun_to_hostgroup [ -l | --lun_name ] <lun name> [ -g | --group_name ] <hostgroup_name>'
   print '      add_lun_to_host [ -l | --lun_name ] <lun_name> [ -h | --host_name ] <hostname>'
   print ''
   print '      create_snapshot [ -l | --lun_name ]  <comma separated list of LUNs (no spaces!)> [ -x | --suffix snapshot_suffix ]'
   print '      copy_lun [ -l | --lun_name ]  source_lun_name [ -d | --destination ] destination_lun_name'
   print ''
   print '      remove_host_from_hostgroup [ -h | --host_name ] <comma separated list of hostnames (no spaces!)> [ -g | --group_name ] <hostgroup_name>'
   print '      remove_lun_from_host [ -l | --lun_name ] <lun name> [ -h | --host_name ] <hostname>'
   print '      remove_lun_from_hostgroup [ -l | --lun_name ] <lun name> [ -g | --group_name ] <hostgroup_name>'
   print ''
   print '      delete_host [-h --host_name ] <hostname>'
   print '      delete_hostgroup [-g | --group_name ] <hostgroup_name>'
   print '      delete_lun [ -l | --lun_name ] <lun_name>'
   print ''
   print ''
   print '	list_ports'
   print ''
   print ''
   print ''
   print ''
   print ''
   print '-v | --verbose:  will give you more detail relating to that function.'
   print '                 without "verbose" any successful actions (creates, adds etc) will simply exit with a 0 return code'
   sys.exit(2)
#
#
def main(argv):
   array_name = ''
   api_token = ''
   verbose = False
   try:
      opts, args = getopt.getopt(argv,"?h:l:a:p:f:s:vw:x:g:d:",["help", "host_name=", "lun_name=", "array=","password=","function=","lun_size=","verbose","wwn=","suffix=","group_name=","destination=","personality="])
   except:
      print str(getopt.GetoptError)
      usage()
   for opt, arg in opts:
      if opt in ("-?", "--help"):
         usage()
      elif opt in ("-a", "--array"):
         array_name = arg
      elif opt in ("-d", "--destination"):
         destination = arg
      elif opt in ("-f", "--function"):
         function = arg
      elif opt in ("-g", "--group_name"):
         group_name = arg
      elif opt in ("-h", "--host_name"):
         host_name = arg
      elif opt in ("-l", "--lun_name"):
         lun_name = arg
      elif opt in ("-p", "--password"):
         api_token = arg
      elif opt in ("--personality"):
         personality = arg
      elif opt in ("-s", "--lun_size"):
         lun_size = arg
      elif opt in ("-v", "--verbose"):
         verbose = True
      elif opt in ("-w", "--wwn"):
         wwn_list = arg
      elif opt in ("-x", "--suffix"):
         snapshot_suffix = arg

# If no function is specified then send a usage message
   try:
      function
   except:
      print "ERROR: You must specify a function to perform"
      usage()
   
   array = purestorage.FlashArray(array_name, api_token=api_token)
#   
   if function == 'list_luns':
      try:
         lun_name
      except:
         response=array.list_volumes()
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Created", "Serial"))
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
         else:
            for x in range(len(response)):
               print response[x]['name']
      else:
         response=array.list_volumes(names=lun_name, connect=True)
#         response=array.list_volumes(names=lun_name)
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Host Name", "Host Group"))
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['host'], response[x]['hgroup']))
         else:
            print "If you're wanting information on specific lun(s) then use the '-v' option"
#   
   if function == 'list_snapshot_luns':
      try:
         lun_name
      except:
         response=array.list_volumes(snap=True)
         if verbose:
            print("%-48s%-48s%-24s%-26s%s" % ("Snapshot Source Name", "Name", "Size in GB", "Created", "Serial"))
            for x in range(len(response)):
               print("%-48s%-48s%-24s%-26s%s" % (response[x]['source'], response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
         else:
            for x in range(len(response)):
               print response[x]['name']
      else:
         response=array.list_volumes(names=lun_name, snap=True )
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Host Name", "Host Group"))
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
         else:
            print "If you're wanting information on specific lun(s) then use the '-v' option"
#   
   if function == 'list_all_luns':
      try:
         lun_name
      except:
         response=array.list_volumes()
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Created", "Serial"))
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
            response=array.list_volumes(snap=True)
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
         else:
            for x in range(len(response)):
               print response[x]['name']
            response=array.list_volumes(snap=True)
            for x in range(len(response)):
               print response[x]['name']
      else:
         response=array.list_volumes(names=lun_name)
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Host Name", "Host Group"))
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
            response=array.list_volumes(names=lun_name, snap=True)
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
         else:
            print "If you're wanting information on specific lun(s) then use the '-v' option"
#
   if function == 'list_deleted_luns':
      response=array.list_volumes(pending_only=True)
      if verbose:
         print("%-48s%-24s%-26s%-18s%s" % ("Name", "Size in GB", "Created", "Time Remaining", "Serial"))
         for x in range(len(response)):
            print("%-48s%-24s%-26s%-18s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['time_remaining'], response[x]['serial']))
         response=array.list_volumes(pending_only=True,snap=True)
         for x in range(len(response)):
            print("%-48s%-24s%-26s%-18s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['time_remaining'], response[x]['serial']))
      else:
         for x in range(len(response)):
            print response[x]['name']
         response=array.list_volumes(pending_only=True,snap=True)
         for x in range(len(response)):
            print response[x]['name']

#
#     if host_name has been passed then let's just get info about this else do all hosts
#     lists_hosts will give you all hosts along with their wwns and hgroup
#     list_hostrs specifying hostname gives you vols and hgroup
#
   elif function == 'list_hosts':
      try:
         host_name
      except:
         response=array.list_hosts()
         if verbose:
            print("%-26s%-49s%-48s" % ("Hostname", "Group Name", "WWNs"))
         for x in range(len(response)):
# Note trailing comma for no newline.  This is Python 2 speak - use end = " " for Python 3
            print("%-26s%-48s" % (response[x]['name'], response[x]['hgroup'])),
            for y in range(len(response[x]['wwn'])):
               print(''.join([ char if not ind or ind % 2 else ':' + char for ind,char in enumerate((response[x]['wwn'][y]).lower())])),
#              print ("%s " % (response[x]['wwn'][y])).lower(),
            print ""
      else:
         response=array.list_host_connections(host=host_name)
         if verbose:
            print("%-26s%-48s%-48s%-4s" % ("Hostname", "Group Name", "LUN Name", ""))
         for x in range(len(response)):
               print("%-26s%-48s%-48s%-4s" % (response[x]['name'], response[x]['hgroup'],  response[x]['vol'],  ""))

#
   elif function == 'list_hostgroups':
      try:
        group_name
      except: 
         if verbose:
            response=array.list_hgroups()
            print("%-28s%-48s" % ("Host Group", "Host Name"))
            for x in range(len(response)):
               for y in range(len(response[x]['hosts'])):
                  print("%-48s%s" % (response[x]['name'], response[x]['hosts'][y]))
#                  response[x]['name']=""
         else:
            response=array.list_hgroups()
            for x in range(len(response)):
               print response[x]['name']
      else:
            response=array.list_hgroup_connections(hgroup=group_name)
            print("%-26s%-48s%-26s" % ("Host Group", "LUN Name", "LUN Number"))
            for x in range(len(response)):
               print("%-26s%-48s%-26s" % (response[x]['name'], response[x]['vol'], response[x]['lun']))
# 
#   
   elif function == 'list_ports':
         response=array.list_ports()
         for x in range(len(response)):
            print("%-10s%-26s" % (response[x]['name'], ':'.join(re.findall('..', response[x]['wwn'].lower()))))
#   
   elif function == 'create_lun':
      try:
         response=array.create_volume(lun_name, lun_size)
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Created", "Serial"))
            print("%-48s%-24s%-26s%s" % (response['name'], response['size']/1024/1024/1024, response['created'], response['serial']))
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "LUN Creation failed: {}: {}".format(lun_name, y[0]['msg'])
         sys.exit(1)
#   
   elif function == 'extend_lun':
      try:
         response=array.extend_volume(lun_name, lun_size)
         if verbose:
            print("%-48s%-24s" % ("Name", "Size in GB"))
            print("%-48s%-24s" % (response['name'], response['size']/1024/1024/1024))
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "LUN Creation failed: {}: {}".format(lun_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'create_host':
      try:
         response=array.create_host(host_name)
         if verbose:
            print "host creation succeeded: {}".format(host_name)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "host creation failed: {}: {}".format(host_name, y[0]['msg'])
         sys.exit(1)
      try:
         wwn_list=wwn_list.split(',')
         response=array.set_host(host_name, wwnlist=wwn_list)
         if verbose:
            print "WWNs added"
            for y in range(len(response['wwn'])):
               print "{}".format(response['wwn'][y])
#           sys.exit(0)
      except purestorage.PureHTTPError as response:
         print response
         y=json.loads(response.text)
         print "Failed to allocate WWNs to {}: {}".format(host_name, y[0]['msg'])
         sys.exit(1)
      try:
         response=array.set_host(host_name, personality=personality)
         if verbose:
            print "Personality set to {}".format(personality)
            sys.exit(0)
      except purestorage.PureHTTPError as response:
         print response
         y=json.loads(response.text)
         print "Failed to set personality to {}: {}".format(personality, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'create_hostgroup':
      try:
         response=array.create_hgroup(group_name)
         if verbose:
            print "hostgroup creation succeeded: {}".format(group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "hostgroup creation failed: {}: {}".format(group_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'add_host_to_hostgroup':
      try:
         host_list=host_name.split(',')
         response=array.set_hgroup(group_name, addhostlist=host_list)
         if verbose:
            print "Successfully added {} to hostgroup {}".format(host_list, group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Adding {} to hostgroup {} failed: {}".format(host_list, group_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'add_lun_to_hostgroup':
      try:
         response=array.connect_hgroup(group_name, lun_name)
         if verbose:
            print "Successfully added lun {} to hostgroup {}".format(lun_name, group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Adding lun {} to hostgroup {} failed: {}".format(lun_name, group_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'add_lun_to_host':
      try:
         response=array.connect_host(host_name, lun_name)
         if verbose:
            print "Successfully added lun {} to host {}: lun={}".format(lun_name, host_name, response['lun'])
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Adding lun {} to host {} failed: {}".format(lun_name, host_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'copy_lun':
      try:
         response=array.copy_volume(lun_name, destination, overwrite=True)
         if verbose:
            print "Successfully copied lun {} to {}".format(lun_name, response['name'])
         else:
            sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Copy of lun {} failed: {}".format(lun_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'create_snapshot':
      try:
         lun_list=lun_name.split(',')
         response=array.create_snapshots(lun_list, suffix=snapshot_suffix)
         print "Successfully create snapshot lun:"
         if verbose:
            print("%-48s%-24s%-26s%s" % ("Name", "Size in GB", "Created", "Serial"))
            for x in range(len(response)):
               print("%-48s%-24s%-26s%s" % (response[x]['name'], response[x]['size']/1024/1024/1024, response[x]['created'], response[x]['serial']))
         else:
            for x in range(len(response)):
               print response[x]['name']
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Creating snapshot lun {} failed: {}".format(lun_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'delete_host':
      try:
         response=array.delete_host(host_name)
         if verbose:
            print "Successfully deleted host {}".format(host_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Deletion of host {} failed: {}".format(host_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'delete_hostgroup':
      try:
         response=array.delete_hgroup(group_name)
         if verbose:
            print "Successfully deleted hostgroup {}".format(group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Deletion of hostgroup {} failed: {}".format(group_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'delete_lun':
      try:
         response=array.destroy_volume(lun_name)
         if verbose:
            print "Successfully deleted volume {}".format(lun_name)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Deletion of lun {} failed: {}".format(lun_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'eradicate_lun':
     try:
        response=array.eradicate_volume(lun_name)
        if verbose:
           print "Successfully eradicated volume {}".format(lun_name)
        sys.exit(0)
     except purestorage.PureHTTPError as response:
        y=json.loads(response.text)
        print "eradication of lun {} failed: {}".format(lun_name, y[0]['msg'])
        sys.exit(1)
#
   elif function == 'remove_host_from_hostgroup':
      try:
         host_list=host_name.split(',')
         response=array.set_hgroup(group_name, remhostlist=host_list)
         if verbose:
            print "Successfully removed {} from hostgroup {}".format(host_list, group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Removal of hosts {} from hostgroup {} failed: {}".format(host_list, group_name, y[0]['msg'])
         sys.exit(1)
#
   elif function == 'remove_lun_from_host':
      try:
         response=array.disconnect_host(host_name, lun_name)
         if verbose:
            print "Successfully removed lun {} from host {}".format(lun_name, host_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Removing lun {} from host {} failed: {}".format(lun_name, host_name, y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'remove_lun_from_hostgroup':
      try:
         response=array.disconnect_hgroup(group_name, lun_name)
         if verbose:
            print "Successfully removed lun {} from hostgroup {}".format(lun_name, group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Removing lun {} from hostgroup {} failed: {}".format(lun_name, group_name, y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'create_alert_recipient':
      try:
         response=array.create_alert_recipient(group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Eeek create_alert_recipients failed: {}".format(y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'delete_alert_recipient':
      try:
         response=array.delete_alert_recipient(group_name)
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Eeek delete_alert_recipients failed: {}".format(y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'list_alert_recipients':
      try:
         response=array.list_alert_recipients()
         print("%-48s%-24s" % ("Recipient","Enabled"))
         for x in range(len(response)):
            print("%-48s%-24s" % (response[x]['name'], response[x]['enabled']))
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Eeek list_alert_recipients failed: {}".format(y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'enable_remote_assist':
      try:
         print "Please wait..."
         response=array.enable_remote_assist()
         print("%-10s%-48s" % (response['status'], response['port']))
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Eeek enable_remote_assist failed: {}".format(y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'disable_remote_assist':
      try:
         response=array.disable_remote_assist()
         print("%-10s" % (response['status']))
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Eeek disable_remote_assist failed: {}".format(y[0]['msg'])
         sys.exit(1)
#      
   elif function == 'get_remote_assist_status':
      try:
         response=array.get_remote_assist_status()
         print("%-10s" % (response['status']))
         sys.exit(0)
      except purestorage.PureHTTPError as response:
         y=json.loads(response.text)
         print "Eeek get_remote_assist_status failed: {}".format(y[0]['msg'])
         sys.exit(1)


   #disconnect from API
   array.invalidate_cookie()

if __name__ == "__main__":
  main(sys.argv[1:])
