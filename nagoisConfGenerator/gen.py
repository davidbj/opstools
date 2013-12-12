#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json
import urllib, urllib2
import os

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
HOST_CONF_DIR = os.path.join(CURR_DIR, 'hosts')
CACHE_FILE = '/var/tmp/api-cache.json'

HOST_TMP="""define host{
                host_name    %(hostname)s
                alias        %(hostname)s
                address      %(ipaddr)s
                check_command check-host-alive
                check_interval     5
                retry_interval     1
                max_check_attempts 5
                check_period       24x7
                process_perf_data  0
                retain_nonstatus_information     0
                contact_groups     admins
                notification_interval     30
                notification_period     24x7
                notification_options    d,u,r
}    
"""

SERVICE_TMP="""define service{
                host_name              %(hostname)s
                service_description    Check Http
                check_period           24x7
                max_check_attempts     4
                normal_check_interval  3
                retry_check_interval   2
                contact_groups         admins
                notification_interval  10
                notification_period    24x7
                notification_options   w,u,c,r
                check_command          check_http!-H www.956122.com!5!10
}
"""

SERVICE_USER_TMP="""define service{
                        host_name    %(hostname)s
                        service_description     check-%(hostname)s-user
                        check_period            24x7
                        max_check_attempts      4
                        normal_check_interval   3
                        retry_check_interval    2
                        contact_groups          admins
                        notification_interval   10
                        notification_period     24x7
                        notification_options    w,u,c,r
                        check_command           check_nrpe!check_users
}
"""

SERVICE_LOAD_TMP="""define service{
                        host_name    %(hostname)s
                        service_description     check-%(hostname)s-load
                        check_period            24x7
                        max_check_attempts      4
                        normal_check_interval   3
                        retry_check_interval    2
                        contact_groups          admins
                        notification_interval   10
                        notification_period     24x7
                        notification_options    w,u,c,r
                        check_command           check_nrpe!check_load
}
"""

SERVICE_SWAP_TMP="""define service{
                        host_name               %(hostname)s
                        service_description     check-%(hostname)s-swap
                        check_period            24x7
                        max_check_attempts      4
                        normal_check_interval   3
                        retry_check_interval    2
                        contact_groups          admins
                        notification_interval   10
                        notification_period     24x7
                        notification_options    w,u,c,r
                        check_command           check_nrpe!check_swap
}
"""

SERVICE_DISK_TMP="""define service{
                        host_name               %(hostname)s
                        service_description     check-%(hostname)s-disk
                        check_period            24x7
                        max_check_attempts      4
                        normal_check_interval   3
                        retry_check_interval    2
                        contact_groups          admins
                        notification_interval   10
                        notification_period     24x7
                        notification_options    w,u,c,r
                        check_command           check_nrpe!check_disk
}
"""

SERVICE_CPU_LOAD_TMP="""define service{
                        host_name               %(hostname)s
                        service_description     check-%(hostname)s-cpu-load
                        check_period            24x7
                        max_check_attempts      4
                        normal_check_interval   3
                        retry_check_interval    2
                        contact_groups          admins
                        notification_interval   10
                        notification_period     24x7
                        notification_options    w,u,c,r
                        check_command           check_nrpe!check_cpu_load
}
"""

HOSTGROUP_TMP="""define hostgroup{
                     hostgroup_name    %(hostgroup)s
                     alias             %(hostgroup)s
                     members           %(members)s
}  
"""

def getHosts():
    """Obtain host information from cmdb system."""

    url = "http://133.96.7.121/api/gethosts.json"
    try:
        data = urllib2.urlopen(url).read()
        writeFile(CACHE_FILE, data)
    except:
        with open(CACHE_FILE, 'r') as fd:
            data = fd.read()
    return json.loads(data)

def initDir():
    """If the configuration directory does not exist,create it."""

    if not os.path.exists(HOST_CONF_DIR):
        os.mkdir(HOST_CONF_DIR)

def writeFile(f, s):
    """When you can not get information from the CMDB host systems.To obtain information from the
       cache file.If you can get the information,the information will be updated with the latest
       mainframe systems to cmdb."""

    with open(f, 'w') as fd:
        fd.write(s)

def genNagiosHost(hostdata):
    """Processing information,and claimed that the configuration file."""

    initDir()
    fp_hostconf = os.path.join(HOST_CONF_DIR, 'hosts.cfg')
    fp_hostgroupconf = os.path.join(HOST_CONF_DIR, 'hostgroups.cfg')
    fp_serviceconf = os.path.join(HOST_CONF_DIR, 'service.cfg')
    hostconf = ""
    serviceconf = ""
    hostgroupconf = ""
    for hg in hostdata:
        members = []
        for h in hg['members']:
            if HOST_TMP % h not in hostconf:
                hostconf += HOST_TMP % h
                serviceconf += SERVICE_USER_TMP % h 
                serviceconf += SERVICE_LOAD_TMP % h
                serviceconf += SERVICE_SWAP_TMP % h
                serviceconf += SERVICE_DISK_TMP % h
                serviceconf += SERVICE_CPU_LOAD_TMP % h
            if hg['hostgroup'] == 'HTTP_check_status':
                hostconf += SERVICE_TMP % h 
            members.append(h['hostname'])
        hostgroupconf += HOSTGROUP_TMP % {'hostgroup':hg['hostgroup'], 'members':','.join(members)}

    try:
        writeFile(fp_hostconf, hostconf)
        writeFile(fp_serviceconf, serviceconf)
        writeFile(fp_hostgroupconf, hostgroupconf)
        return 'Nagios Template write success.'
    except:
        return 'Error:Nagios Template write failure.'
 
def main():
    """Global functions"""

    result = getHosts()
    if result['status'] == 0:
        print genNagiosHost(result['data'])
    else:
        print 'Err: %s' % result['message']

if __name__ == "__main__":
    main()    
