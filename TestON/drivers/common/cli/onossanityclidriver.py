#!/usr/bin/env python
'''
'''

import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import core.teston
import time
import json
import traceback
import requests
import urllib2
from urllib2 import URLError, HTTPError

sys.path.append("../")
from drivers.common.clidriver import CLI

class onossanityclidriver(CLI):
    '''
    '''
    def __init__(self):
        super(CLI, self).__init__()

    def connect(self,**connectargs):
        '''
        Creates ssh handle for ONOS.
        '''
        try:
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            self.home = "~/ONOS"
            for key in self.options:
                if key == "home":
                    self.home = self.options['home']
                    break

            
            self.name = self.options['name']
            self.handle = super(onossanityclidriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)

            if self.handle:
                return self.handle
            else :
                main.log.info("NO ONOS HANDLE")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()   
 
    def start(self):
        '''
        Starts ONOS on remote machine.
        Returns false if any errors were encountered.
        '''
        try:
            main.log.info("Hello Saurav")
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("pwd")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            main.log.info(self.name + " : " + self.handle.before)

            self.handle.sendline("./onos.sh  start")
            i=self.handle.expect(["STARTED","FAILED",pexpect.EOF,pexpect.TIMEOUT])
            response = self.handle.before + str(self.handle.after)
            if i==0:
                j = self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT], timeout=60)
                if re.search("Killed",response):
                    main.log.warn(self.name + ": Killed existing process")
                if j==0:
                    main.log.info(self.name + ": ONOS Started ")
                    return main.TRUE
                elif j==1:
                    main.log.error(self.name + ": EOF exception found")
                    main.log.error(self.name + ":     " + self.handle.before)
                    main.cleanup()
                    main.exit()
                elif j==2:
                    main.log.info(self.name + ": ONOS NOT Started, stuck while waiting for it to start ")
                    return main.FALSE
                else:
                    main.log.warn(self.name +": Unexpected response in start")
                    return main.TRUE
            elif i==1:
                main.log.error(self.name + ": ONOS Failed to start")
                return main.FALSE
            elif i==2:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            elif i==3:
                main.log.error(self.name + ": ONOS timedout while starting")
                return main.FALSE
            else:
                main.log.error(self.name + ": ONOS start  expect script missed something... ")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    
    def status(self):
        '''
        Calls onos.sh core status and returns TRUE/FALSE accordingly
        '''
        try:
            self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd="./onos.sh core status ",prompt="\d+\sinstance\sof\sonos\srunning",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            if re.search("1\sinstance\sof\sonos\srunning",response):
                return main.TRUE
            elif re.search("0\sinstance\sof\sonos\srunning",response):
                return main.FALSE
            else :
                main.log.info( self.name + " WARNING: status recieved unknown response")
		main.log.info( self.name + " For details: check onos core status manually")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def zk_status(self):
        '''
        Calls the zookeeper status and returns TRUE if it has an assigned Mode to it. 
        '''
        try:
	    self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
	    self.handle.sendline("./onos.sh zk status")
	    i=self.handle.expect(["standalone","Error",pexpect.EOF,pexpect.TIMEOUT])
            if i==0: 
	        main.log.info(self.name + ": Zookeeper is running.") 
                return main.TRUE
            elif i==1:
	        main.log.error(self.name + ": Error with zookeeper") 
                main.log.info(self.name + ": Directory used: "+self.home)
		return main.FALSE
	    elif i==3:
		main.log.error(self.name + ": Zookeeper timed out")
		main.log.info(self.name + ": Directory used: "+self.home)
		return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()	

    def rcs_status(self):
        '''
        This Function will return the Status of the RAMCloud Server
        '''
        main.log.info(self.name + ": Getting RC-Server Status")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-server status")
        self.handle.expect(["onos.sh rc-server status",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after

        if re.search("0\sRAMCloud\sserver\srunning", response) :
            main.log.info(self.name+": RAMCloud not running")
            return main.TRUE
        elif re.search("1\sRAMCloud\sserver\srunning",response):
            main.log.warn(self.name+": RAMCloud Running")
            return main.TRUE
        else:
            main.log.info( self.name+":  WARNING: status recieved unknown response")
            return main.FALSE
            
    def rcc_status(self):
        '''
        This Function will return the Status of the RAMCloud Coord
        '''
        main.log.info(self.name + ": Getting RC-Coord Status")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-coord status")
        i=self.handle.expect(["onos.sh rc-coord status",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        #return response
        
        if re.search("0\sRAMCloud\scoordinator\srunning", response) :
            main.log.warn(self.name+": RAMCloud Coordinator not running")
            return main.TRUE
        elif re.search("1\sRAMCloud\scoordinator\srunning", response):
            main.log.info(self.name+": RAMCloud Coordinator Running")
            return main.TRUE
        else:
            main.log.warn( self.name+": coordinator status recieved unknown response")
            return main.FALSE

    def stop(self):
        '''
        Runs ./onos.sh core stop to stop ONOS
        '''
        try:
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.sendline("./onos.sh stop")
            i=self.handle.expect(["Stop",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT], 60)
            result = self.handle.before
            if re.search("Killed", result):
                main.log.info(self.name + ": ONOS Killed Successfully")
                return main.TRUE
            else :
                main.log.warn(self.name + ": ONOS wasn't running")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def start_rest(self):
        '''
        Starts the rest server on ONOS.
        '''
        try:
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd= "./start-rest.sh start",prompt="\$",timeout=10)
            if re.search(self.user_name,response):
                main.log.info(self.name + ": Rest Server Started Successfully")
                time.sleep(5)
                return main.TRUE
            else :
                main.log.warn(self.name + ": Failed to start Rest Server")
		main.log.info(self.name + ": Directory used: "+self.home )
		main.log.info(self.name + ": Rest server response: "+response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def rest_stop(self):
        '''
        Runs ./start-rest.sh stop to stop ONOS rest server
        '''
        try:
            response = self.execute(cmd= self.home + "./start-rest.sh stop ",prompt="killing",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            if re.search("killing", response):
                main.log.info(self.name + ": Rest Server Stopped")
                return main.TRUE
            else :
                main.log.error(self.name + ": Failed to Stop, Rest Server is not Running")
		main.log.info(self.name + ": Directory used: "+self.home)
		main.log.info(self.name + ": Rest server response: " + response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def rest_status(self):
        '''
        Checks if the rest server is running.
        '''
        #this function does not capture the status response correctly...
        #when cmd is executed, the prompt expected should be a string containing
        #status message, but instead returns the user@user$ Therefore prompt="running"
        #was changed to prompt="\$"
        try:
            response = self.execute(cmd= self.home + "./start-rest.sh status ",prompt="\$",timeout=10)
            if re.search(self.user_name,response):
                main.log.info(self.name + ": Rest Server is running")
                return main.TRUE
            elif re.search("rest\sserver\sis\snot\srunning",response):
                main.log.warn(self.name + ": Rest Server is not Running")
                return main.FALSE
            else :
                main.log.error(self.name + ": No response" +response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def disconnect(self):
        '''
        Called when Test is complete to disconnect the ONOS handle.
        '''
        response = ''
        try:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except:
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response
 
    def print_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller | grep -A 5 \"commit\"; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            main.log.report(response)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
    def get_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller | grep -A 5 \"commit\"; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            lines=response.splitlines()
            for line in lines:
                print line
            return lines[2]
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def create_tunnel(self, onosRESTIP, onosRESTPort, tunnelURL, params):
        url = "http://%s:%s/%s"%(self.ip_address,"8080",tunnelURL)
        main.log.info(self.name+": with url & params =" +url + " " + params)
        try:
            request = urllib2.Request(url,params)
            request.get_method = lambda: "POST"
            request.add_header("Content-Type", "application/json")
            response=urllib2.urlopen(request)
            result = response.read()
            response.close()
            #if len(result) != 0:
            #    parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
            main.log.error(self.name+": HTTPError="+error_payload)
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
            main.log.error(self.name+": URLError="+exc.reason)
        main.log.info(self.name+": result="+result)
        if re.search('success',result):
            main.log.info(self.name+": success")
            main.last_result = main.TRUE 
            return main.TRUE
        else:
            main.log.info(self.name+": failed")
            main.last_result = main.FALSE 
            return main.FALSE
        
    def convert_from_unicode(self, input):
        if isinstance(input, dict):
            return {self.convert_from_unicode(key): self.convert_from_unicode(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self.convert_from_unicode(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    
    def get_all_groups_of_tunnel(self, onosRESTIP, onosRESTPort, tunnelURL, tunnel_id):
        url = "http://%s:%s/%s"%(self.ip_address,"8080",tunnelURL)
        main.log.info(self.name+": with url & params =" +url + " " + tunnel_id)
        try:
            result = urllib2.urlopen(url, None).read()
            if len(result) != 0:
                parsed_result = self.convert_from_unicode(json.loads(result))
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
            main.log.error(self.name+": HTTPError="+error_payload)
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
            main.log.error(self.name+": URLError="+exc.reason)
        #main.log.info(self.name+": result="+parsed_result)
        #print "parsed_result:",parsed_result
        groups = [{}]
        for entry in parsed_result:
            if entry.has_key("tunnelId"):
                if entry["tunnelId"] == tunnel_id:
                    for swgroupstr in entry["dpidGroup"]:
                        swgroup = swgroupstr.split('/')
			swgroup1 = swgroup[1]
			swgroup = swgroup[0].split('(')
                        #print "SW:GROUP is",swgroup[0],swgroup[1]
                        #Get all groups from this switch
                        url2 = "http://%s:%s/%s/%s/%s"%(self.ip_address,"8080",
                                    "wm/floodlight/core/switch",swgroup[0],
                                    "groupDesc/json")
                        print "url2:",url2
                        try:
                            result2 = urllib2.urlopen(url2, None).read()
                            if len(result2) != 0:
                                parsed_result2 = self.convert_from_unicode(json.loads(result2))
                        except HTTPError as exc:
                            print "HTTP ERROR:"
                        except URLError as exc:
                            print "URL ERROR:"
                        allGroups = {}
                        #print "parsed_result2: ", parsed_result2
                        for groupStat in parsed_result2[swgroup[0]]:
                            gotoGroup = -1
                            if groupStat['bucketsActions'][0].has_key('goToGroup'):
                                gotoGroup = groupStat['bucketsActions'][0]['goToGroup']
                            allGroups[groupStat['groupId']] = gotoGroup
                        #print "All groups: ",allGroups
                        groupChain = []
                        groupChain.append(int(swgroup1))
                        nextInChain = allGroups[int(swgroup1)]
                        while nextInChain != -1:
                            groupChain.append(nextInChain)
                            nextInChain = allGroups[nextInChain]
                        groups.append({"SW": swgroup[0],
                                       "GROUPS":groupChain,
                                      })
        #print "groups for tunnel are:",groups
        return groups
    
    def get_switch_group_stats(self, onosRESTIP, onosRESTPort, dpid):
        url = "http://%s:%s/%s/%s/%s"%(self.ip_address,"8080",
                    "wm/floodlight/core/switch",dpid,
                    "groupStats/json")
        main.log.info(self.name+": with url =" +url)
        try:
            result = urllib2.urlopen(url, None).read()
            if len(result) != 0:
                parsed_result = self.convert_from_unicode(json.loads(result))
                #print parsed_result
                return parsed_result[dpid]
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
            main.log.error(self.name+": HTTPError="+error_payload)
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
            main.log.error(self.name+": URLError="+exc.reason)
            
        return main.FALSE
            
    def delete_tunnel(self, onosRESTIP, onosRESTPort, tunnelURL, params):
        url = "http://%s:%s/%s"%(self.ip_address,"8080",tunnelURL)
        main.log.info(self.name+": Delete a Tunnel in ONOS controller with url & params ="
                      +url + " " + params)
        try:
            request = urllib2.Request(url,params)
            request.get_method = lambda: "DELETE"
            request.add_header("Content-Type", "application/json")
            response=urllib2.urlopen(request)
            result = response.read()
            response.close()
            #if len(result) != 0:
            #    parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
            main.log.error(self.name+": HTTPError="+error_payload)
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
            main.log.error(self.name+": URLError="+exc.reason)
        main.log.info(self.name+": result="+result)
        if re.search('success',result):
            main.log.info(self.name+": success")
            main.last_result = main.TRUE 
            return main.TRUE
        else:
            main.log.info(self.name+": failed")
            main.last_result = main.FALSE 
            return main.FALSE
    
    def create_policy(self, onosRESTIP, onosRESTPort, policyURL, params):
        url = "http://%s:%s/%s"%(self.ip_address,"8080",policyURL)
        main.log.info(self.name+": Create a Policy in ONOS controller with url & params ="
                      +url + " " + params)
        try:
            request = urllib2.Request(url,params)
            request.get_method = lambda: "POST"
            request.add_header("Content-Type", "application/json")
            response=urllib2.urlopen(request)
            result = response.read()
            response.close()
            #if len(result) != 0:
            #    parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
            main.log.error(self.name+": HTTPError="+error_payload)
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
            main.log.error(self.name+": URLError="+exc.reason)
        main.log.info(self.name+": result="+result)
        if re.search('success',result):
            main.log.info(self.name+": Create tunnel success")
            main.last_result = main.TRUE 
            return main.TRUE
        else:
            main.log.info(self.name+": Create tunnel failed")
            main.last_result = main.FALSE 
            return main.FALSE

    def delete_policy(self, onosRESTIP, onosRESTPort, policyURL, params):
        url = "http://%s:%s/%s"%(self.ip_address,"8080",policyURL)
        main.log.info(self.name+": Delete a Policy in ONOS controller with url & params ="
                      +url + " " + params)
        try:
            request = urllib2.Request(url,params)
            request.get_method = lambda: "DELETE"
            request.add_header("Content-Type", "application/json")
            response=urllib2.urlopen(request)
            result = response.read()
            response.close()
            #if len(result) != 0:
            #    parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
            main.log.error(self.name+": HTTPError="+error_payload)
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
            main.log.error(self.name+": URLError="+exc.reason)
        main.log.info(self.name+": result="+result)
        if re.search('deleted',result):
            main.log.info(self.name+": success")
            main.last_result = main.TRUE 
            return main.TRUE
        else:
            main.log.info(self.name+": failed")
            main.last_result = main.FALSE 
            return main.FALSE

    def add_flow(self, intentFile, path):
	try:
            main.log.info("add_flow running...")
	    main.log.info("using directory: "+path) 
            time.sleep(10)
            self.handle.sendline("cd " + path)
            self.handle.expect("tests")
            self.handle.sendline("./"+intentFile)
            time.sleep(10)
            self.handle.sendline("cd "+self.home)
            return main.TRUE
	except pexepct.EOF:
	    main.log.error(self.name + ": EOF exception found")
	    main.log.error(self.name + ":    " + self.handle.before)
	    main.cleanup()
	    main.exit()
	except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.log.error( traceback.print_exc() )	       
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.cleanup()
	    main.exit()

    def delete_flow(self, intentFile, path):
	try:
            main.log.info("delete_flow running...")
	    main.log.info("using directory: " + path)
	    main.log.info("using file: " + intentFile)
            self.handle.sendline("cd " + path)
            self.handle.expect("tests")
            self.handle.sendline("./" + intentFile)
            time.sleep(10)
            self.handle.sendline("cd "+self.home)
            return main.TRUE
	except pexepct.EOF:
	    main.log.error(self.name + ": EOF exception found")
	    main.log.error(self.name + ":    " + self.handle.before)
	    main.cleanup()
	    main.exit()
	except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.log.error( traceback.print_exc() )	       
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.cleanup()
	    main.exit()	

    def check_flow(self):
        '''
        Calls the ./get_flow.py all and checks:
        - If each FlowPath has at least one FlowEntry
        - That there are no "NOT"s found
        returns TRUE/FALSE
        '''
        try:
            flowEntryDetect = 1
            count = 0
            self.handle.sendline("clear")
            time.sleep(1)
            self.handle.sendline(self.home + "/web/get_flow.py all")
            self.handle.expect("get_flow")
            while 1:
                i=self.handle.expect(['FlowPath','FlowEntry','NOT','\$',pexpect.TIMEOUT],timeout=180)
                if i==0:
                    count = count + 1
                    if flowEntryDetect == 0:
                        main.log.info(self.name + ": FlowPath without FlowEntry")
                        return main.FALSE
                    else:
                        flowEntryDetect = 0
                elif i==1:
                    flowEntryDetect = 1
                elif i==2:
                    main.log.error(self.name + ": Found a NOT")
                    return main.FALSE
                elif i==3:
                    if count == 0:
                        main.log.info(self.name + ": There don't seem to be any flows here...")
                        return main.FALSE
                    else:
                        main.log.info(self.name + ": All flows pass")
                        main.log.info(self.name + ": Number of FlowPaths: "+str(count))
                        return main.TRUE
                elif i==4:
                    main.log.error(self.name + ":Check_flow() - Command Timeout!")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def get_flow(self, *flowParams):
        '''
        Returns verbose output of ./get_flow.py
        '''
        try:
            if len(flowParams)==1:
                if str(flowParams[0])=="all":
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    main.log.info(self.name + ": Getting all flow data...")
                    data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh all",prompt="done",timeout=150)
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    return data
                else:
                    main.log.info(self.name + ": Retrieving flow "+str(flowParams[0])+" data...")
                    data = self.execute(cmd=self.home +"/scripts/TestON_get_flow.sh "+str(flowParams[0]),prompt="done",timeout=150)
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    return data
            elif len(flowParams)==5:
                main.log.info(self.name + ": Retrieving flow installer data...")
                data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3])+" "+str(flowParams[4]),prompt="done",timeout=150)
                self.execute(cmd="\n",prompt="\$",timeout=60)
                return data
            elif len(flowParams)==4:
                main.log.info(self.name + ": Retrieving flow endpoints...")
                data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3]),prompt="done",timeout=150)
                self.execute(cmd="\n",prompt="\$",timeout=60)
                return data
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


# http://localhost:8080/wm/onos/ng/switches/json
# http://localhost:8080/wm/onos/ng/links/json
# http://localhost:8080/wm/onos/registry/controllers/json
# http://localhost:8080/wm/onos/registry/switches/json"

    def get_json(self, url):
        '''
        Helper functions used to parse the json output of a rest call
        '''
        try:
            try:
                command = "curl -s %s" % (url)
                result = os.popen(command).read()
                parsedResult = json.loads(result)
            except:
                print "REST IF %s has issue" % command
                parsedResult = ""
        
            if type(parsedResult) == 'dict' and parsedResult.has_key('code'):
                print "REST %s returned code %s" % (command, parsedResult['code'])
                parsedResult = ""
            return parsedResult
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_switch(self,RestIP,correct_nr_switch, RestPort ="8080" ):
        '''
        Used by check_status
        '''
        try:
            buf = ""
            retcode = 0
            url="http://%s:%s/wm/onos/topology/switches" % (RestIP, RestPort)
            parsedResult = self.get_json(url)
            if parsedResult == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
            url = "http://%s:%s/wm/onos/registry/switches" % (RestIP, RestPort)
            registry = self.get_json(url)
        
            if registry == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
        
            cnt = 0
            active = 0

            for s in parsedResult:
                cnt += 1
                if s['state'] == "ACTIVE":
                   active += 1

            buf += "switch: network %d : %d switches %d active\n" % (0+1, cnt, active)
            if correct_nr_switch != cnt:
                buf += "switch fail: network %d should have %d switches but has %d\n" % (1, correct_nr_switch, cnt)
                retcode = 1

            if correct_nr_switch != active:
                buf += "switch fail: network %d should have %d active switches but has %d\n" % (1, correct_nr_switch, active)
                retcode = 1
        
            return (retcode, buf)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_link(self,RestIP, nr_links, RestPort = "8080"):
        '''
        Used by check_status
        '''
        try:
            buf = ""
            retcode = 0
        
            url = "http://%s:%s/wm/onos/topology/links" % (RestIP, RestPort)
            parsedResult = self.get_json(url)
        
            if parsedResult == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
        
            buf += "link: total %d links (correct : %d)\n" % (len(parsedResult), nr_links)
            intra = 0
            interlink=0
        
            for s in parsedResult:
                intra = intra + 1
        
            if intra != nr_links:
                buf += "link fail\n"
                retcode = 1
        
            return (retcode, buf)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_status_report(self, ip, numoswitch, numolink, port="8080"):
        '''
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the report log.
        '''
        try:
            main.log.info(self.name + ": Making some rest calls...")
            switch = self.check_switch(ip, int(numoswitch), port)
            link = self.check_link(ip, int(numolink), port)
            value = switch[0]
            value += link[0]
            main.log.report( self.name + ": \n-----\n%s%s-----\n" % ( switch[1], link[1]) )
            if value != 0:
                return main.FALSE
            else:
                # "PASS"
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_status(self, ip, numoswitch, numolink, port = "8080"):
        '''
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the main log.
        '''
        try:
            main.log.info(self.name + ": Making some rest calls...")
            switch = self.check_switch(ip, int(numoswitch), port)
            link = self.check_link(ip, int(numolink), port)
            value = switch[0]
            value += link[0]
            main.log.info(self.name + ": \n-----\n%s%s-----\n" % ( switch[1], link[1]) )
            if value != 0:
                return main.FALSE
            else:
                # "PASS"
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
 
    def check_for_no_exceptions(self):
        '''
        TODO: Rewrite
        Used by CassndraCheck.py to scan ONOS logs for Exceptions
        '''
        try:
            self.handle.sendline("dsh 'grep Exception ~/ONOS/onos-logs/onos.*.log'")
            self.handle.expect("\$ dsh")
            self.handle.expect("\$")
            output = self.handle.before
            main.log.info(self.name + ": " + output )
            if re.search("Exception",output):
                return main.FALSE
            else :
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def git_pull(self, comp1=""):
        '''
        Assumes that "git pull" works without login
        
        This function will perform a git pull on the ONOS instance.
        If used as git_pull("NODE") it will do git pull + NODE. This is
        for the purpose of pulling from other nodes if necessary.

        Otherwise, this function will perform a git pull in the 
        ONOS repository. If it has any problems, it will return main.ERROR
        If it successfully does a git_pull, it will return a 1.
        If it has no updates, it will return a 0.

        '''
        try:
            main.log.info(self.name + ": Stopping ONOS")
            self.stop()
            self.handle.sendline("cd " + self.home)
            self.handle.expect("ONOS\$")
            if comp1=="":
                self.handle.sendline("git pull")
            else:
                self.handle.sendline("git pull " + comp1)
           
            uptodate = 0
            i=self.handle.expect(['fatal','Username\sfor\s(.*):\s','Unpacking\sobjects',pexpect.TIMEOUT,'Already up-to-date','Aborting'],timeout=1800)
            #debug
           #main.log.report(self.name +": \n"+"git pull response: " + str(self.handle.before) + str(self.handle.after))
            if i==0:
                main.log.error(self.name + ": Git pull had some issue...")
                return main.ERROR
            elif i==1:
                main.log.error(self.name + ": Git Pull Asking for username!!! BADD!")
                return main.ERROR
            elif i==2:
                main.log.info(self.name + ": Git Pull - pulling repository now")
                self.handle.expect("ONOS\$", 120)
                return 0
            elif i==3:
                main.log.error(self.name + ": Git Pull - TIMEOUT")
                return main.ERROR
            elif i==4:
                main.log.info(self.name + ": Git Pull - Already up to date")
                return 1
            elif i==5:
                main.log.info(self.name + ": Git Pull - Aborting... Are there conflicting git files?")
                return main.ERROR
            else:
                main.log.error(self.name + ": Git Pull - Unexpected response, check for pull errors")
                return main.ERROR
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
#********************************************************           


    def git_compile(self):
        '''
        Compiles ONOS
        First runs mvn clean then mvn compile
        '''
        try:
            main.log.info(self.name + ": mvn clean")
            self.handle.sendline("cd " + self.home)
            self.handle.sendline("mvn clean")
            while 1:
                i=self.handle.expect(['There\sis\sinsufficient\smemory\sfor\sthe\sJava\sRuntime\sEnvironment\sto\scontinue','BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=30)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory for the Java Runtime Environment to continue.")
                    return main.FALSE
                elif i == 1:
                    main.log.error(self.name + ": Clean failure!")
                    return main.FALSE
                elif i == 2:
                    main.log.info(self.name + ": Clean success!")
                elif i == 3:
                    main.log.info(self.name + ": Clean complete")
                    break;
                elif i == 4:
                    main.log.error(self.name + ": mvn clean TIMEOUT!")
                    return main.FALSE
                else:
                    main.log.error(self.name + ": unexpected response from mvn clean")
                    return main.FALSE
        
            main.log.info(self.name + ": mvn compile")
            self.handle.sendline("mvn compile")
            while 1:
                i=self.handle.expect(['There\sis\sinsufficient\smemory\sfor\sthe\sJava\sRuntime\sEnvironment\sto\scontinue','BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=60)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory for the Java Runtime Environment to continue.")
                    return main.FALSE
                if i == 1:
                    main.log.error(self.name + ": Build failure!")
                    return main.FALSE
                elif i == 2:
                    main.log.info(self.name + ": Build success!")
                    return main.TRUE
                elif i == 3:
                    main.log.info(self.name + ": Build complete")
                    return main.TRUE
                elif i == 4:
                    main.log.error(self.name + ": mvn compile TIMEOUT!")
                    return main.FALSE
                else:
                    main.log.error(self.name + ": unexpected response from mvn compile")
                    return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def tcpdump(self, intf = "eth0"):
        '''
        Runs tpdump on an intferface and saves in onos-logs under the ONOS home directory
        intf can be specified, or the default eth0 is used
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("sudo tcpdump -n -i "+ intf + " -s0 -w " + self.home +"/onos-logs/tcpdump &")
            i=self.handle.expect(['No\ssuch\device','listening\son',pexpect.TIMEOUT],timeout=10)
            if i == 0:
                main.log.error(self.name + ": tcpdump - No such device exists. tcpdump attempted on: " + intf)
                return main.FALSE
            elif i == 1:
                main.log.info(self.name + ": tcpdump started on " + intf)
                return main.TRUE
            elif i == 2:
                main.log.error(self.name + ": tcpdump command timed out! Check interface name, given interface was: " + intf)
                return main.FALSE
            else:
                main.log.error(self.name + ": tcpdump - unexpected response")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def kill_tcpdump(self):
        '''
        Kills any tcpdump processes running
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("sudo kill -9 `ps -ef | grep \"tcpdump -n\" | grep -v grep | awk '{print $2}'`")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def find_host(self,RestIP,RestPort,RestAPI,hostIP):
        retcode = 0
        retswitch = []
        retport = []
        retmac = []
        foundIP = []
        try:
            ##### device rest API is: 'host:8080/wm/onos/ng/switches/json' ###
            url ="http://%s:%s%s" %(RestIP,RestPort,RestAPI)
            print url

            try:
                command = "curl -s %s" % (url)
                result = os.popen(command).read()
                parsedResult = json.loads(result)
                print parsedResult
            except:
                print "REST IF %s has issue" % command
                parsedResult = ""

            if parsedResult == "":
                return (retcode, "Rest API has an error", retport, retmac)
            else:
                for switch in enumerate(parsedResult):
                    #print switch
                    for port in enumerate(switch[1]['ports']):
                        if ( port[1]['devices'] != [] ):
                            try:
                                foundIP = port[1]['devices'][0]['ipv4addresses'][0]['ipv4']
                            except:
                                print "Error in detecting IP address."
                            if foundIP == hostIP:
                                retswitch.append(switch[1]['dpid'])
                                retport.append(port[1]['desc'])
                                retmac.append(port[1]['devices'][0]['mac'])
                                retcode = retcode +1
                                foundIP =''
            return(retcode, retswitch, retport, retmac)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

#Perf test related functions

    def addPerfFlows(self, flowdef, numflows):
        main.log.info("ADD_FLOW RUNNING!!!! ")
        startTime=time.time()
        self.execute(cmd="/home/admin/ONOS/scripts"+"/add_"+str(numflows)+".py",prompt="\$",timeout=10)
        elapsedTime=time.time()-startTime
        main.log.info("AddFlows script run time: " + str(elapsedTime) + " seconds")
        time.sleep(15)
        return main.TRUE

    def removePerfFlows(self, flowdef, numflows):
        main.log.info("REMOVE_FLOW RUNNING!!!! ")
        startTime=time.time()
        self.execute(cmd="/home/admin/ONOS/scripts"+"/remove_"+str(numflows)+".py",prompt="\$",timeout=10)
        elapsedTime=time.time()-startTime
        main.log.info("RemoveFlows script run time: " + str(elapsedTime) + " seconds")
        time.sleep(15)
        return main.TRUE

    def start_tshark(self,flowtype, numflows):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.execute(cmd='''rm /tmp/wireshark*''')
        self.handle.sendline("y")
        self.handle.expect("\$")
        self.execute(cmd='''tshark -i lo -t e | grep --color=auto CSM | grep --color=auto -E 'Flow|Barrier' > /tmp/tdump_'''+flowtype+"_"+str(numflows)+".txt &",prompt="Capturing",timeout=10)
        self.handle.sendline("")
        self.handle.expect("\$")
        main.log.info("TSHARK STARTED!!!")
        return main.TRUE

    def stop_tshark(self):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("sudo kill -9 `ps -ef | grep \"tshark -i\" | grep -v grep | awk '{print $2}'`")
        self.handle.sendline("")
        self.handle.expect("\$")
        main.log.info("TSHARK STOPPED!!!")
        return main.TRUE

    def generateFlows(self, flowdef, flowtype, numflows, ip):
        main.log.info("GENERATE FLOWS RUNNING!!!")
        #main.log.info("Test" + flowdef+"/"+flowtype+"_"+str(numflows)+".py")
        f = open(flowdef+"/"+flowtype+"_"+str(numflows)+".py", 'w')
        f.write('''#! /usr/bin/python\n''')
        f.write('import json\n')
        f.write('import requests\n')
        f.write('''url = 'http://'''+ip+''':8080/wm/onos/datagrid/add/intents/json'\n''')
        f.write('''headers = {'Content-type': 'application/json', 'Accept': 'application/json'}\n''') 
        
        intents = []
        idx = 0
        for i in range(6,(numflows+6)):
	    mac3 = idx / 255
	    mac4 = idx % 255
	    str_mac3 = "%0.2x" % mac3
	    str_mac4 = "%0.2x" % mac4
	    srcMac = '00:01:'+str_mac3+':'+str_mac4+':00:00'
	    dstMac = '00:02:'+str_mac3+':'+str_mac4+':00:00'
	    srcSwitch = '00:00:00:00:00:00:10:00'
	    dstSwitch = '00:00:00:00:00:00:10:00'
	    srcPort = 1
	    dstPort = 2
	
	    intent = {'intent_id': '%d' %(i),'intent_type':'shortest_intent_type','intent_op':flowtype,'srcSwitch':srcSwitch,'srcPort':srcPort,'srcMac':srcMac,'dstSwitch':dstSwitch,'dstPort':dstPort,'dstMac':dstMac}
	    intents.append(intent)
	    idx = idx + 1
        f.write('''s=''')
        f.write(json.dumps(intents, sort_keys = True))
        f.write('''\nr = requests.post(url, data=json.dumps(s), headers = headers)''')
        #f.flush()
        #subprocess.Popen(flowdef, stdout=f, stderr=f, shell=True)
        #f.close()
        os.system("chmod a+x "+flowdef+"/"+flowtype+"_"+str(numflows)+".py")
        
        return main.TRUE
    
    def getFile(self, numflows, ip, directory, flowparams):
        main.log.info("GETTING FILES FROM TEST STATION: "+str(ip))
        #for i in range(0,3):
        print str(numflows) + " "+str(flowparams[numflows])
        self.handle.sendline("scp admin@10.128.7.7:/home/admin/TestON/tests/OnosFlowPerf/add_"+str(flowparams[numflows])+".py admin@10.128.5.51:/home/admin/ONOS/scripts/" )
            
        self.handle.sendline("scp admin@10.128.7.7:/home/admin/TestON/tests/OnosFlowPerf/remove_"+str(flowparams[numflows])+".py admin@10.128.5.51:/home/admin/ONOS/scripts/" ) 

        return main.TRUE

    def printPerfResults(self, flowtype, numflows, stime):
        import datetime  
        self.handle.sendline("")
        self.handle.expect("\$")
        for (i,j) in zip(numflows,stime):
            startTime=datetime.datetime.fromtimestamp(j)
            tshark_file=open("/tmp/tdump_"+flowtype+"_"+str(i)+".txt",'r')
            allFlowmods=tshark_file.readlines()
            time.sleep(5)
            firstFlowmod=allFlowmods[0]
            lastBarrierReply=allFlowmods[-1]
            #self.handle.sendline("")
            #self.handle.expect("\$")
            #self.handle.sendline("head -1 /tmp/tdump_"+flowtype+"_"+str(i)+".txt")
            #self.handle.expect("\(CSM\)")
            #firstFlowmod=self.handle.before
            #firstFlowmod=self.execute(cmd="head -1 /tmp/tdump_"+flowtype+"_"+str(i)+".txt",prompt="\$",timeout=10)
            #lastBarrierReply=self.execute(cmd="tail -n 1 /tmp/tdump_"+flowtype+"_"+str(i)+".txt",prompt="\$",timeout=10)
            firstFlowmodSplit=firstFlowmod.split()
            firstFlowmodTS=datetime.datetime.fromtimestamp(float(firstFlowmodSplit[0]))
            lastBarrierSplit=lastBarrierReply.split()
            lastBarrierTS=datetime.datetime.fromtimestamp(float(lastBarrierSplit[0]))
            main.log.report("Number of Flows: " + str(i))
            #main.log.info("Add Flow Start Time: " + str(startTime))
            main.log.report("First Flow mod seen after: " + str(float(datetime.timedelta.total_seconds(firstFlowmodTS-startTime)*1000))+"ms")
            main.log.report("Last Barrier Reply seen after: " + str(float(datetime.timedelta.total_seconds(lastBarrierTS-startTime)*1000))+"ms\n")
            main.log.report("Total Flow Setup Delay(from first flowmod): " + str(float(datetime.timedelta.total_seconds(lastBarrierTS-firstFlowmodTS)*1000))+"ms")
            main.log.report("Total Flow Setup Delay(from start): " + str(float(datetime.timedelta.total_seconds(lastBarrierTS-startTime)*1000))+"ms\n")
            main.log.report("Flow Setup Rate (using first flowmod TS): " + str(int(1000/datetime.timedelta.total_seconds(lastBarrierTS-firstFlowmodTS)))+" flows/sec")
            main.log.report("Flow Setup Rate (using start time): " + str(int(1000/datetime.timedelta.total_seconds(lastBarrierTS-startTime)))+" flows/sec")
            print "*****************************************************************"
            #main.log.info("first: " + str(firstFlowmod))
            #main.log.info(firstFlowmodSplit)
            #main.log.info("last: " + str(lastBarrierReply))
            tshark_file.close()
        return main.TRUE

    def isup(self):
        '''
        A more complete check to see if ONOS is up and running properly.
        First, it checks if the process is up.
        Second, it reads the logs for "Exception: Connection refused"
        Third, it makes sure the logs are actually moving.
        returns TRUE/FALSE accordingly.
        '''
        try:
            self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd= "./onos.sh core status ",prompt="running",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            tail1 = self.execute(cmd="tail " + self.home + "/onos-logs/onos.*.log",prompt="\$",timeout=10)
            time.sleep(10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            tail2 = self.execute(cmd="tail " + self.home + "/onos-logs/onos.*.log",prompt="\$",timeout=10)
            pattern = '(.*)1 instance(.*)'
            patternUp = 'Sending LLDP out'
            pattern2 = '(.*)Exception: Connection refused(.*)'
           # if utilities.assert_matches(expect=pattern,actual=response,onpass="ONOS process is running...",onfail="ONOS process not running..."):
            
            if re.search(pattern, response):
                if re.search(patternUp,tail2):
                    main.log.info(self.name + ": ONOS process is running...")
                    if tail1 == tail2:
                        main.log.error(self.name + ": ONOS is frozen...")#logs aren't moving
                        return main.FALSE
                    elif re.search( pattern2,tail1 ):
                        main.log.info(self.name + ": Connection Refused found in onos log")
                        return main.FALSE
                    elif re.search( pattern2,tail2 ):
                        main.log.info(self.name + ": Connection Refused found in onos log")
                        return main.FALSE
                    else:
                        main.log.info(self.name + ": Onos log is moving! It's looking good!")
                        return main.TRUE
                else:
                    main.log.info(self.name + ": ONOS not yet sending out LLDP messages")
                    return main.FALSE
            else:
                main.log.error(self.name + ": ONOS process not running...")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def sendline(self, cmd):
        self.handle.sendline(cmd)
