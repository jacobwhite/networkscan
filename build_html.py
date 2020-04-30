#!/usr/bin/python3
import os
import subprocess
from datetime import datetime, timedelta
from urllib.request import urlopen
import config
#hosts_path = "/var/www/html/networkscan/hosts/"
#logs_path = "/var/www/html/networkscan/logs/"

def host_to_html(host, hours, link):
    if host == '.log' or ".swp" in host:
        return ""
    html_output = ''
    #print("rendering: " + host)
    with open(config.logs_path + host) as f:
        line = f.readline()
        fields = line.split(',')
        try:
            status = fields[4].replace("\n", "")
        except:
            status = ""
        try:
            bonjour_name = fields[2]
        except:
            bonjour_name = ""
        try:
            ip = fields[1]
        except:
            ip = ""
        try:
            mac = fields[0]
        except:
            mac = ""
        try:
            vendor = fields[3]
        except:
            vendor = ""
        try:
            status = "Up" if fields[4].replace("\n", "") == "True" else "Down"
        except:
            status = ""
        try:
            ports = fields[5]
        except:
            ports = ""

        if link == "":
            html_output += '<h1><a href="../">Network Devices</a> / Device Detail</h1>'
        html_output += '<div class='
        html_output += '"' + status + '">' 
        if link != "":
            html_output += '<a href="' + link + '">'
        #html_output += 'Bonjour Name: ' + bonjour_name + '<br>'
        bonjour_name = (bonjour_name[:18] + '..') if len(bonjour_name) > 18 else bonjour_name
        host_title = bonjour_name
        vendor = (vendor[:18] + '..') if len(vendor) > 18 else vendor

        if(host_title == ""):
            host_title = vendor
            host_title += "<br>" + ip
        if(ip == ""):
            host_title = mac

        html_output += '<div class="host_name_div">' + host_title + '</div>'
        #html_output += 'IP: ' + ip + '<br>'
        #html_output += 'MAC: ' + mac + '<br>'
        #html_output += '<div class="host_vendor_div">Vendor: ' + vendor + '</div><br>'
        #html_output += 'Status: ' + status + '<br>'
        if link == "":
            html_output += 'Ports: ' + ports + '<br>'
        else:
            html_output += '</a>'
            """
        if link != '':
            for port in ports.split(";"):
                fields = port.split("/")
                if len(fields) == 2:
                    fields[0] = fields[0].replace(" ", "")
                    if '5900' in fields[0]:
                        icon = '<img class="icon" src=/networkscan/icons/screen_sharing.png height=64>'
                        html_output += '<a href="vnc://' + ip + ":" + fields[0] + '">' + icon + '</a>'
                    elif '22' in fields[0]:
                        icon = '<img class="icon" src=/networkscan/icons/terminal.png height=64>'
                        html_output += '<a href="ssh://' + ip + ":" + fields[0] + '">' + icon + '</a>'
            if len(ports.split(";")) < 2:
                html_output += '<div class="icon_spacer_div"></div>'
                    #else:
                    #    html_output += '<a href="http://' + ip + ":" + fields[0] + '">' + fields[1] + '</a><br>'
                    """
        html_output += '<canvas id="' + mac.replace(":","") + '"></canvas>'

        times_string = "["
        response_times_string = "["
        for line in os.popen("tail -n 50 " + config.logs_path + host):
        #for line in f:
            tokens = line.replace("\n","").split(",")
            if len(tokens) < 2:
                continue
            try:
                time_stamp = float(tokens[0])
            except:
                print(host +  " [" + tokens[0] + "] invalid date. " + " tokens: " + str(tokens))
                continue
                
            utc_now = datetime.utcnow()
            utc_timestamp = datetime.utcfromtimestamp(time_stamp)
            local_timestamp = utc_timestamp - timedelta(hours=8, minutes=0)
            local_date_string = local_timestamp.strftime('%-I:%M')

            if (utc_now - utc_timestamp).seconds < (hours * 60 * 60):
                times_string += "'" + local_date_string + "', "
                response_times_string += tokens[1][1:] + ","
        times_string += "]"
        response_times_string += "]"
        times_string = times_string.replace(", ]", "]")
        response_times_string = response_times_string.replace(",]", "]")
        #print("times: " + times_string)
        #print("response_times: " + response_times_string)

        html_output += "<script>var ctx = document.getElementById('" + mac.replace(":","") + "').getContext('2d');"
        html_output += """
var chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'line',

    // The data for our dataset
    data: {"""
        #labels: ['1', '2', '3'],
        html_output += 'labels: ' + times_string + ','
        html_output += """
        datasets: [{
            label: 'response time',
            backgroundColor: 'rgb(0, 155, 0)',
            pointRadius:1,
            borderColor: 'rgb(99, 255, 132)',"""
            #data: [ 20, 30, 45]
        html_output += 'data: ' + response_times_string
        html_output += """
        }]
    },

    // Configuration options go here
    options: {
        legend: {
            display: false
        },
        animation: {
            duration: 0
        },
        scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: 250

                    }
                }]
            }
    }
});</script><br>"""
        html_output += '</div>'
        #if link != '':
        #    html_output +='</a>\n'
    return html_output
        
def host_detail_to_html(filename, hours):
    host_detail_filename = filename.replace(":", "").replace(".log", ".html")
    host_file = open(config.hosts_path + host_detail_filename, "w")
    header_html_output = '<html>\n<head>\n'
    header_html_output +=  '<meta http-equiv="refresh" content="300">'
    header_html_output += '<link rel="stylesheet" type="text/css" href="/networkscan/hostsstyle.css">\n'
    header_html_output += '<script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>\n'
    header_html_output += '</head>'
    host_file.write(header_html_output + host_to_html(filename, hours, ""))
    host_file.close()

def get_hosts():
    count = 0
    html_output = ""
    for root, dirs, files in os.walk(config.logs_path):
        for filename in files:
            if ".log" in filename:
                host_output = host_to_html(filename,1, "./hosts/" + filename.replace(":", "").replace(".log", ".html"))
                host_array.append(host_output)
                #html_output += host_output
                host_detail_to_html(filename, 48)
                count += 1
    host_array.sort(reverse=True)
    for host in host_array:
        html_output += host
    html_output += '<div>' + str(count) + ' devices</div>\n'
    return html_output

host_array = []
html_output = '<html>\n<head>\n'
html_output += '<meta http-equiv="refresh" content="300">'
html_output += '<meta name="viewport" content="width=320, initial-scale=1.0, maximum-scale=1.0">'
html_output += '<link rel="stylesheet" type="text/css" href="/networkscan/hostsstyle.css">\n'
html_output += '<link rel="stylesheet" type="text/css" href="style.css">\n'
html_output += '<script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>\n'
html_output += '<script src="javascript.js"></script>\n'
html_output += '</head><body>'
html_output += '<div id="top_div">'
html_output += '<b>Network Devices</b><br>'
html_output += 'Up Hosts: <a id="up_toggle" href="#" onclick="toggle(\'up\');">Shown</a><br>'
html_output += 'Down Hosts: <a id="down_toggle" href="#" onclick="toggle(\'down\');">Shown</a><br>'
html_output += 'Charts: <a id="chart_toggle" href="#" onclick="toggle(\'chart\');">Shown</a><br>'
html_output += '<b>' + datetime.now().strftime("%m/%d/%Y %-I:%M %p") + '</b>'
html_output += '</div>'
html_output += get_hosts()
html_output += """<script>
if(localStorage.down == "0"){
    hide_class("Down");
    document.getElementById("down_toggle").innerHTML = "Hidden";
}
if(localStorage.up == "0"){
    hide_class("Up");
    document.getElementById("up_toggle").innerHTML = "Hidden";
}
if(localStorage.chart == "0"){
    hide_class("chartjs-render-monitor");
    document.getElementById("chart_toggle").innerHTML = "Hidden";
    }
        </script>"""
html_output += '</body></html>'
#print(html_output)

out_file = open(config.index_path + "index.html", "w")
out_file.write(html_output)
out_file.close()
