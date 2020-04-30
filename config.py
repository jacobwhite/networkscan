#!/usr/bin/python3

##Raspberry Pi Paths
vendors_path = "/var/www/html/networkscan/vendors.txt"
hosts_path = "/var/www/html/networkscan/hosts/"
logs_path = "/var/www/html/networkscan/logs/"
index_path = "/var/www/html/networkscan/"

#Relative paths for running manually 
#vendors_path = "vendors.txt"
#hosts_path = "hosts/"
#logs_path = "logs/"
#index_path = "./"
#build_path = "./"

number_of_threads = 64                                      #Number of concurrent threads that will run
number_of_ping_attempts = '1'                               #Number of times to ping a host to see if its up
ports = "80,443,22,23,5900,3389"                            #Blank for whatever the NMAP default is.
ip_range = '172.16.1.'
