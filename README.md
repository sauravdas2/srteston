TestON, a testing infastructure by Paxterra
=======================================
TestON is the testing platform that all the ONOS tests are being run on currently. 
This is a private fork of TestOn meant only for the segment routing tests.

Setup 
-------------

0. Pull the git repo from 

    $ git clone https://github.com/sauravdas2/srteston.git

1. Make a symbolic link for TestON on the HOMEDIR 
   Execute the following from the home directory  

    $ ln -s srteston/TestON TestON

2. Make sure python path is correct 

    $ export PYTHONPATH={PATH TO HOMEDIR}/TestON/

    $ echo $PYTHONPATH 


Dependencies
------------
1. Zookeeper

2. ONOS

3. Mininet

4. Install python packages configObj and pexpect. they can be installed as :

     $ sudo pip install configObj

     $ sudo easy_install pexpect 

Configuration
------------

1. Config file at TestON/config/teston.cfg

    Change the file paths to the appropriate TestON paths. 
    Actually you probably don't need to change anything here unless
    your TestON root folder is different from /home/admin/TestON.

2. The .topo file for each test
 
    Must change the IPs/login/etc to point to the nodes you want to run on.
    Specifically you need to change TestON/tests/SRSanity/SRSanity.topo
    You need to give the IP addr, login and password for the VM that is running Mininet
    and the VM that is running the controller. Please do not commit/push this information.
    You need to do this even if you are running TestON on the same VM as your controller
    or Mininet VM. 

3. onossanityclidriver.py

    Change the ONOS root folder path and assign to self.home variable
 
Running TestON
------------
0. Remember that the controller jar file should be up to date with the changes you are testing
   i.e. you should have run 'mvn package' in the ONOS directory

1. TestON must be run from its bin directory 

    $ cd TestON/bin

2. Launch cli

    $ ./cli.py 

3. Run the test 

    teston> run SRSanity 

The Tests
-----------------------------------------------

The tests are all located it TestON/tests/
Each test has its own folder with the following files: 

1. .ospk file

    - This is written in Openspeak, an word based language developed by Paxterra.

    - It defines the cases and sequence of events for the test 

2. .py file
 
    - This file serves the same exact function as the openspeak file. 

    - It will only be used if there is NO .ospk file, so if you like python, delete or rename the .ospk file 
 
3. .topo file  

    - This defines all the components that TestON creates for that test and includes data such as IP address, login info, and device drivers  
 
    - The Components must be defined in this file to be uesd in the openspeak or python files. 
    
4. .params file

    - Defines all the test-specific variables that are used by the test. 

    - NOTE: The variable `testcases` which defines which testcases run when the test is ran. 

Troubleshooting
-----------------------------------------------
Here are a few things to check if it doesn't work

1. Double check the topo file for that specific test the nodes must be able to run that specific component ( Mininet IP -> machine with mn installed)

2. Enable passwordless logins between your nodes and the TestON node.  
