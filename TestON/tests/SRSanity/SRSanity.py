import pexpect

class SRSanity:

    def __init__(self) :
        self.default = ''

#*****************************************************************************************************************************************************************************************
#Test startup
#Tests the startup of Zookeeper, and ONOS to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time
        main.log.report("Initial setup")

        main.step("Stopping ONOS if it is running") 
        main.ONOS.stop()
        main.step("Restarting Zookeeper and ONOS with default fish-topology")
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-ecmp.conf/' conf/onos.properties") 
        ret = main.ONOS.start()
        data =  main.ONOS.zk_status()
        if ret == main.FALSE or data == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
            
        #main.ONOS.rest_stop()
        #main.ONOS.start_rest()
        test= main.ONOS.rest_status()
        if test == main.FALSE:
            main.ONOS.start_rest()
        main.ONOS.get_version()

        main.case("Checking if the startup was clean...")
        main.step("Testing Zookeeper Status")  
        data =  main.ONOS.zk_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        
        main.step("Testing ONOS Status")   
        data =  main.ONOS.status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up!",onfail="ONOS is down...")
        main.step("Testing Rest Status")
        data =  main.ONOS.rest_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="REST is up!",onfail="REST is down...")
	
#**********************************************************************************************************************************************************************************************
# A simple test for default connectivity in a fish topology

    def CASE2(self,main) :
        import time
        main.log.report("Running mininet")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_6sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit()
        


#**********************************************************************************************************************************************************************************************
# A simple test for verify controller's recovery functionality in a fish topology

    def CASE3(self,main) :
        import time
        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_6sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_normal = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_normal, 
                                  onpass="Default connectivity check PASS", 
                                  onfail="Default connectivity check FAIL")    
        #Yank the cable on switch1-intf3, switch2-intf3 and switch4-intf3
        #to force the traffic to go via s1->s2->s3->s4->s5->s6
        main.Mininet.yankcpqd(SW="s1",INTF="s1-eth3")
        main.Mininet.yankcpqd(SW="s2",INTF="s2-eth3")
        main.Mininet.yankcpqd(SW="s4",INTF="s4-eth3")
        main.step("waiting 20 secs for controller to perform recovery operations")
        time.sleep(20)
        main.step("verifying connectivity between hosts after link down")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        result_during_failure = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_during_failure,
                                onpass="Connectivity check after network element failure PASS",
                                onfail="Connectivity check after network element failure FAIL")

        
        #Plug back the cable on switch1-intf3, switch2-intf3 and switch4-intf3
        #so that traffic moves back to normal ECMP paths
        #main.Mininet.plugcpqd(SW="s1",INTF="s1-eth3")
        #main.Mininet.plugcpqd(SW="s2",INTF="s2-eth3")
        #main.Mininet.plugcpqd(SW="s4",INTF="s4-eth3")
        main.Mininet.link(END1="s1",END2="s3",OPTION="up")
        main.Mininet.link(END1="s2",END2="s5",OPTION="up")
        main.Mininet.link(END1="s4",END2="s6",OPTION="up")
        main.step("waiting 20 secs for controller to perform recovery operations")
        time.sleep(20)
        main.step("verifying connectivity between hosts after link down")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        result_during_recovery = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_during_recovery,
                                onpass="Connectivity check after network element recovery PASS",
                                onfail="Connectivity check after network element recovery FAIL")

        result = result_normal and result_during_failure and result_during_recovery 
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Controller recovery procedure check PASS",
                                onfail="Controller recovery procedure check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit()
        


#**********************************************************************************************************************************************************************************************
# A simple test for verifying tunnels and policies

    def CASE4(self,main) :
        import time
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_6sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_step1 = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_step1, 
                                  onpass="Default connectivity check PASS", 
                                  onfail="Default connectivity check FAIL")    

        main.step("Verifying create tunnel functionality")
        ret = main.ONOS.create_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t1\",\"label_path\":[101,102,103,104,105,106]}")
        result_step2 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step2, 
                                  onpass="Tunnel create check PASS", 
                                  onfail="Tunnel create check FAIL")    
        
        main.step("Verifying groups created as part tunnel t1 : 3groups@s1 and 1group@s5")
        switch_groups = main.ONOS.get_all_groups_of_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      tunnel_id="t1")
        print "Groups created for tunnel t1",switch_groups
        ret_sw1 = main.FALSE
        ret_sw5 = main.FALSE
        ret_sw1_3groups = main.FALSE
        ret_sw5_1groups = main.FALSE
        ret_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                if (entry['SW'] == "00:00:00:00:00:00:00:01"):
                    ret_sw1 = main.TRUE
                    if (len(entry['GROUPS']) == 3):
                        ret_sw1_3groups = main.TRUE
                if (entry['SW'] == "00:00:00:00:00:00:00:05"):
                    ret_sw5 = main.TRUE
                    if (len(entry['GROUPS']) == 1):
                        ret_sw5_1groups = main.TRUE
                before_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "before_stats: ",before_stats
                if (before_stats != main.FALSE):
                    ret_stats = main.TRUE
                    entry['STATS'] = before_stats 
        #print "results for group check: ", ret_sw1, ret_sw1_3groups, ret_sw5, ret_sw5_1groups, ret_stats    
        result_step3 = ret_sw1 and ret_sw1_3groups and ret_sw5 and ret_sw5_1groups and ret_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step3,
                                onpass="Tunnel groups check PASS",
                                onfail="Tunnel groups check FAIL")
        
        main.step("Verifying create policy functionality")
        #ret = main.ONOS.create_policy("http://127.0.0.1:8080/wm/onos/segmentrouting/policy","{\"priority\": 2223, \"dst_tp_port_op\": \"eq\", \"src_tp_port_op\": \"eq\", \"src_tp_port\": \"1000\", \"tunnel_id\": \"t1\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"dst_tp_port\": \"2000\", \"proto_type\": \"ip\", \"policy_id\": \"pol1\"}")
        ret = main.ONOS.create_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"priority\": 2223, \"tunnel_id\": \"t1\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"proto_type\": \"ip\", \"policy_id\": \"pol1\"}")
        result_step4 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step4,
                                onpass="Policy creation check PASS",
                                onfail="Policy creation check FAIL")

        main.step("waiting 5 secs to push the tunnels and policies to the switches")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy creation")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        ret_group_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                after_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "after_stats: ",after_stats
                if after_stats != main.FALSE:
                    before_pkt_count = 0
                    after_pkt_count = 0
                    for group in entry['GROUPS']:
                        for beforeStat in before_stats:
                            if beforeStat['groupId'] == group:
                                before_pkt_count = beforeStat['packetCount']
                                break
                        for afterStat in after_stats:
                            if afterStat['groupId'] == group:
                                after_pkt_count = afterStat['packetCount']
                                break
                    if (((after_pkt_count-before_pkt_count) > 0) and
                        ((after_pkt_count-before_pkt_count) < 3)):
                        ret_group_stats = main.TRUE
                    else:
                        ret_group_stats = main.FALSE
                        break;
                            
        result_step5 = p1 and ret_group_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Connectivity check on tunnel policy PASS",
                                onfail="Connectivity check on tunnel policy FAIL")

        result_phase1 = result_step1 and result_step2 and result_step3 and result_step4 and result_step5 

        main.step("Verifying delete policy functionality")
        ret = main.ONOS.delete_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"policy_id\": \"pol1\"}")
        result_step6 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Policy deletion check PASS",
                                onfail="Policy deletion check FAIL")

        main.step("Verifying delete tunnel functionality")
        ret = main.ONOS.delete_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t1\"}")
        result_step7 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step7,
                                onpass="Tunnel deletion check PASS",
                                onfail="Tunnel deletion check FAIL")
        
        main.step("waiting 5 secs for tunnel and policy remove to happen")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy deletion")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        result_step8 = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_step8,
                                onpass="Connectivity check after tunnel policy deletion PASS",
                                onfail="Connectivity check after tunnel policy deletion FAIL")

        result = result_phase1 and result_step6 and result_step7 and result_step8 
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Tunnel Policy handling check PASS",
                                onfail="Tunnel Policy handling check FAIL")

        #cleanup mininet
        main.Mininet.disconnect()



#**********************************************************************************************************************************************************************************************
# A simple test for verifying tunnels and policies with auto generated adjacencySid

    def CASE5(self,main) :
        import time
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_6sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_step1 = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_step1,
                                  onpass="Default connectivity check PASS",
                                  onfail="Default connectivity check FAIL")

        main.step("Verifying create tunnel functionality")
        ret = main.ONOS.create_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t2\",\"label_path\":[101,102,102002,103,103003,104,105,106]}")
        result_step2 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step2,
                                  onpass="Tunnel create check PASS",
                                  onfail="Tunnel create check FAIL")

        main.step("Verifying groups created as part tunnel t2 : 3groups@s1 and 1group@s5")
        switch_groups = main.ONOS.get_all_groups_of_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      tunnel_id="t2")
        print "Groups created for tunnel t1",switch_groups
        ret_sw1 = main.FALSE
        ret_sw5 = main.FALSE
        ret_sw1_3groups = main.FALSE
        ret_sw5_1groups = main.FALSE
        ret_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                if (entry['SW'] == "00:00:00:00:00:00:00:01"):
                    ret_sw1 = main.TRUE
                    if (len(entry['GROUPS']) == 3):
                        ret_sw1_3groups = main.TRUE
                if (entry['SW'] == "00:00:00:00:00:00:00:05"):
                    ret_sw5 = main.TRUE
                    if (len(entry['GROUPS']) == 1):
                        ret_sw5_1groups = main.TRUE
                before_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "before_stats: ",before_stats
                if (before_stats != main.FALSE):
                    ret_stats = main.TRUE
                    entry['STATS'] = before_stats
        #print "results for group check: ", ret_sw1, ret_sw1_3groups, ret_sw5, ret_sw5_1groups, ret_stats    
        result_step3 = ret_sw1 and ret_sw1_3groups and ret_sw5 and ret_sw5_1groups and ret_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step3,
                                onpass="Tunnel groups check PASS",
                                onfail="Tunnel groups check FAIL")

        main.step("Verifying create policy functionality")
        #ret = main.ONOS.create_policy("http://127.0.0.1:8080/wm/onos/segmentrouting/policy","{\"priority\": 2223, \"dst_tp_port_op\": \"eq\", \"src_tp_port_op\": \"eq\", \"src_tp_port\": \"1000\", \"tunnel_id\": \"t1\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"dst_tp_port\": \"2000\", \"proto_type\": \"ip\", \"policy_id\": \"pol1\"}")
        ret = main.ONOS.create_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"priority\": 3223, \"tunnel_id\": \"t2\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"proto_type\": \"ip\", \"policy_id\": \"pol2\"}")
        result_step4 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step4,
                                onpass="Policy creation check PASS",
                                onfail="Policy creation check FAIL")
                                     
        main.step("waiting 5 secs to push the tunnels and policies to the switches")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy creation")
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        ret_group_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                after_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "after_stats: ",after_stats
                if after_stats != main.FALSE:
                    before_pkt_count = 0
                    after_pkt_count = 0
                    for group in entry['GROUPS']:
                        for beforeStat in before_stats:
                            if beforeStat['groupId'] == group:
                                before_pkt_count = beforeStat['packetCount']
                                break
                        for afterStat in after_stats:
                            if afterStat['groupId'] == group:
                                after_pkt_count = afterStat['packetCount']
                                break
                    if (((after_pkt_count-before_pkt_count) > 0) and
                        ((after_pkt_count-before_pkt_count) < 3)):
                        ret_group_stats = main.TRUE
                    else:
                        ret_group_stats = main.FALSE
                        break;

        result_step5 = p1 and ret_group_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Connectivity check on tunnel policy PASS",
                                onfail="Connectivity check on tunnel policy FAIL")

        result_phase1 = result_step1 and result_step2 and result_step3 and result_step4 and result_step5

        main.step("Verifying delete policy functionality")
        ret = main.ONOS.delete_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"policy_id\": \"pol2\"}")
        result_step6 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Policy deletion check PASS",
                                onfail="Policy deletion check FAIL")

        main.step("Verifying delete tunnel functionality")
        ret = main.ONOS.delete_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t2\"}")
        result_step7 = ret
        
        utilities.assert_equals(expect=main.TRUE,actual=result_step7,
                                onpass="Tunnel deletion check PASS",
                                onfail="Tunnel deletion check FAIL")

        main.step("waiting 5 secs for tunnel and policy remove to happen")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy deletion")
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        result_step8 = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_step8,
                                onpass="Connectivity check after tunnel policy deletion PASS",
                                onfail="Connectivity check after tunnel policy deletion FAIL")

        result = result_phase1 and result_step6 and result_step7 and result_step8
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Tunnel Policy handling check PASS",
                                onfail="Tunnel Policy handling check FAIL")

        #cleanup mininet
        main.Mininet.disconnect()


#**********************************************************************************************************************************************************************************************
# Restarts the controller in a linear 3-node topology

    def CASE10(self,main) :
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-3node.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        #main.Mininet.handle.sendline("sudo mn -c")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/test13_3sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        #main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h6")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.2")
        result = p1 and p2
        
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit()
       

#**********************************************************************************************************************************************************************************************
# Restarts the controller in a ring topology

    def CASE20(self,main) :
        main.ONOS.stop()
        # starts the controller with ring topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-ring.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        #main.Mininet.handle.sendline("sudo mn -c")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testRing_5sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        #main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.2")
        p2 = main.Mininet.pingall()
        result = p1 and p2

        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit() 

#**********************************************************************************************************************************************************************************************
# Restarts the controller in 10 switch topology

    def CASE30(self,main) :
        main.ONOS.stop()
        # starts the controller with 10 switch topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-ecmp10.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        #main.Mininet.handle.sendline("sudo mn -c")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_10sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        #main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        p2 = main.Mininet.pingall()
        result = p1 and p2

        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit() 
