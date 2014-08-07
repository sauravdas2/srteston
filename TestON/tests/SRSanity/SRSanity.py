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
        main.Mininet.handle.sendline("sudo ./mininet/custom/testEcmp_6sw.py")
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
# Restarts the controller in a linear 3-node topology

    def CASE3(self,main) :
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
        main.Mininet.handle.sendline("sudo ./mininet/custom/test13_3sw.py")
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
        
