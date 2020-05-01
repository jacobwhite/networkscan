# networkscan
Networkscan is a couple of python scripts to scan your local network and gather information about the devices on your network.
It will graph ping times for devices, scan for a few common open ports and look up vendor ids from MAC addresses.

I use it on a Raspberry Pi.

## Setup
Set up a webserver on your raspberry pi and create a folder in the web root folder called "networkscan". On the Raspberry Pi it will be '/var/www/html/networkscan/'

Put all the files from this repository in there.

Then edit config.py
if you're running on a Raspberry Pi and using the default folder above, you don't need to change any of the paths.
The main thing you'll need to change in here is ip_range. Thats usually the first 3 digits of your ip address.

Then give the scripts execute permissions with 
	
	chmod +x scan_devices.py
and

	chmod +x build_html.py

Then run scan_devices.py if if it runs successfully, you should see index.html and a bunch of html files in the hosts folder.

Then you can set the script to run automatically.

Edit your crontab with 

	sudo crontab -e

Add the following line.

	0,5,10,15,20,25,30,35,40,45,50,55 * * * * /var/www/html/networkscan/scan_devices.py >/tmp/networkscan.log 2>&1

That tells your Raspberry Pi to run the script every 5 minutes.

If everything is working as it should be you should be able to go to http://[your raspberry pi's ip or hostname]/networkscan and see a bunch of hosts with graphs.

I hope this is useful to you.
