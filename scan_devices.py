#!/usr/bin/python3
import os
import platform
from os import listdir
from os.path import isfile, join
import subprocess
import threading
import time
from urllib.request import urlopen
import config
#config.vendors_path = "/var/www/html/networkscan/vendors.txt"
#config.hosts_path = "/var/www/html/networkscan/hosts/"
#config.logs_path = "/var/www/html/networkscan/logs/"
#config.number_of_threads = 64 
#config.number_of_ping_attempts = '1'                               #Number of times to ping a host to see if its up
#config.ports = "80,443,22,23,5900,3389"                            #Blank for whatever the NMAP defailt is
#config.ip_range = '172.16.1.'


macs_scanned = []

def mac_vendor_write_to_cache(mac_address, vendor):
    print("caching mac address: " + mac_address + " vendor: " + vendor)
    f=open(config.vendors_path,"a+")
    g=open(config.vendors_path,"r")
    if mac_address in g.read():
        return 
    vendor = vendor.replace(", Inc.", "")
    vendor = vendor.replace(" Inc .", "")
    vendor = vendor.replace(" Inc", "")
    vendor = vendor.replace(",LTD", "")
    vendor = vendor.replace(",Ltd", "")
    vendor = vendor.replace("'", "")
    vendor = vendor.replace(" Co.", "")
    vendor = vendor.replace(", Ltd.", "")
    f.write(mac_address + " " + vendor[1:] + "\n")
    f.close()

def mac_vendor_lookup(mac_address):
    mac_address = mac_address[:8]
    with open(config.vendors_path, 'r') as f:
        if mac_address in f.read():
            #print("cached")
            g=open(config.vendors_path, "r")
            tmp=g.read()
            for line in tmp.splitlines():
                if mac_address in line:
                    return line[9:]
        else:
            #print("looking up MAC")
            mac_link = 'https://api.macvendors.com/' + mac_address
            #print("mac_link: " + mac_link)
            try:
                mac_vendor = str(urlopen(mac_link).read())
                mac_vendor_write_to_cache(mac_address,mac_vendor)
            except:
                return ""
        return mac_vendor

def write_host(bonjour_name, ip, mac, vendor, status, response_time, open_ports):
    #write header
    if os.path.isfile(config.logs_path + mac + ".log"):
        f=open(config.logs_path + mac + ".log", "r+")
    else:
        f=open(config.logs_path + mac + ".log", "w+")
    f.seek(0)
    f.write(mac + ",")
    f.write(ip + ",")
    f.write(bonjour_name + ",")
    f.write(vendor + ",")
    f.write(status + ",")
    f.write(open_ports + "\n")
    f.close()
    ts = time.time()

    #write log
    f=open(config.logs_path + mac + ".log", "a+")
    f.write(str(ts) + ", " + response_time + "\n")

def read_host(mac):
    host_path = config.logs_path + mac + ".log"
    if os.path.isfile(host_path):
        f = open(host_path, "r")
        line = f.readline()
        tokens = line.split(",")
        return tokens
    else:
        return []

def do_host_status(ip):
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
                ['ping', '-c', config.number_of_ping_attempts, '-W', '1', ip],
                stdout=DEVNULL,  # suppress output
                stderr=DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False

def do_host_response_time(ip):
        return os.popen("ping -c "+ config.number_of_ping_attempts + " " + ip + "| tail -1| awk '{print $4}' | cut -d '/' -f 2").read().replace("\n", "")

def do_bonjour_name(ip):
    bonjour_name=os.popen("/usr/bin/dig +short -x " + ip + " @224.0.0.251 -p 5353 +timeout=1").read().replace("\n", "")
    if ".local" not in bonjour_name:
        bonjour_name = ""
    return bonjour_name

def do_host_mac_address(ip):
    if platform.system() == 'Linux':
        arp_command = "/usr/sbin/arp -a"
    elif platform.system() == "Darwin":
        arp_command = "/usr/sbin/arp"
    else:
        print("platform: " + platform.system())
    tmp = os.popen(arp_command + " " + ip).read().split(" ")
    print(tmp)
    result = os.popen(arp_command + " " + ip).read().split(" ")[3]
    if len(result) != 17:
        result = ""

    return result

def do_host_open_ports(ip):
    config.ports
    ports_arg = "-p "
    output = ""
    if  config.ports != "":
        ports_arg = ports_arg + config.ports
    else:
        ports_arg = " -F "
    cmd = "/usr/bin/nmap " + ports_arg + " " + ip + " -oG - |" + """awk '/\/open\//{
  l=""
  for (i=3;i<=NF;++i) {
    if ($i~/\/open\//) l=l" "$i;
  };
  print l
 }'"""
    result = os.popen(cmd).read().split(",")
    for port in result:
        fields = port.split("/")
        if len(fields) >=4 :
            #output += "port: " + fields[0] + " name: " + fields[4] + "\n"
            output += fields[0] + "/" + fields[4] + ";"
    return output

def do_host2(ip):
    print("Checking: " + ip)
    status = do_host_status(ip)
    if status:
        response_time = do_host_response_time(ip)
        bonjour_name = do_bonjour_name(ip)
        mac_address = do_host_mac_address(ip)
        macs_scanned.append(mac_address)
        mac_vendor = mac_vendor_lookup(mac_address)
        status = str(status)
        if "True" in status:
            open_ports = do_host_open_ports(ip)
        write_host(bonjour_name, ip, mac_address, mac_vendor, status, response_time, open_ports)
        print("IP: " + ip)
        print("status: " + status)
        print("response time: " + response_time)
        print("bonjour: " + bonjour_name)
        print("MAC: " + mac_address)
        print("MAC Vendor: " + mac_vendor)
        print("Ports: " + open_ports)
        print("########################################")
    #else:
        #response_time = ""
        #bonjour_name = ""
        #mac_address = ""
        #mac_vendor = ""
        #status = str(status)
    thread_limiter.release()


output = '<html><head> <link rel="stylesheet" type="text/css" href="style.css"></head><body>'
output = output + "<h1>Network Devices</h1>\n"
date = os.popen("date").read()
output = output + "<h2>" + date + "</h2>\n"

thread_limiter = threading.BoundedSemaphore(config.number_of_threads)

#SCAN IP ADDRRESSES ON LOCAL SUBNET
threads = []
for i in range(1,254):
    ip = config.ip_range + str(i)
    thread_limiter.acquire()
    try:
        host_check_thread = threading.Thread(target=do_host2, args=(ip,), kwargs={})
        threads.append(host_check_thread)
        host_check_thread.start()
    except:
        print("something happened")

for i in range(1,254):
    threads[i-1].join()

#print("MACs scanned: " + str(macs_scanned))
host_files = [f for f in listdir(config.logs_path) if isfile(join(config.logs_path, f))]
for host_file in host_files:
    if ".log" in host_file:
        host_header = read_host(host_file.replace(".log",""))
        if host_header[0] not in macs_scanned:
            #print("missing host: " + host_header[0] + " " + host_header[4])
            #print("host_header: " + str(host_header))
            #host_header: ['38:00:25:00:36:97', '172.16.1.163', 'dell-24083.local.', 'Intel Corporate', 'True\n']
            write_host(host_header[2], host_header[1], host_header[0], host_header[3], "False", "", "")
os.popen(config.build_path + 'build_html.py')
