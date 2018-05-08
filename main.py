# -*- coding: utf-8 -*-
import config # config file
from hello import MaskTerminal, TextColor  # Крутое приветствие 

import boto3
import socket
from datetime import timedelta, datetime
import time

"""
TODO:
   1 Determine the instance state using its DNS name (need at least 2 verifications: TCP and HTTP).
   2 Create an AMI of the stopped EC2 instance and add a descriptive tag based on the EC2 name along with the current date.
   3 Terminate stopped EC2 after AMI creation.
   4 Clean up AMIs older than 7 days.
   5 Print all instances in fine-grained output, INCLUDING terminated one, with highlighting their current state.  
"""

constract_template = ['','',[],'','','','']
#	'Hostname'				0
#	'ResolveIP'				1
#	['config.scan_ports']	2
#	'InstanceId'			3
#	'InstancePubIP'			4
#	'InstanceStatus'		5
#	'InstanceNameTag'		6

all_instance_info = []


client = boto3.client('ec2',region_name=config.region_name,aws_access_key_id=config.aws_access_key_id, 
					  aws_secret_access_key=config.aws_secret_access_key)		

aws = boto3.session.Session(aws_access_key_id=config.aws_access_key_id, 
					  aws_secret_access_key=config.aws_secret_access_key, 
					  region_name=config.region_name)	  
ec2 = aws.resource('ec2')


					  
def resolveIP(target):
    """
        Resolve Hostname
    """
    ip = repr(socket.gethostbyname_ex(target)[2][0])
    return ip


def getAllInstanceInfo(all_instance_info):
    """
	    Get all info about instance
    """
    print("Get instances info.")

    for host in config.hosts:
        constract =  list(constract_template)
        constract[0] = host
        constract[1] = str(resolveIP(host))[1:-1]
        all_instance_info.append(constract)
    for instance in ec2.instances.all():
        if config.name_tag in instance.tags[0].get('Value'):		# check if name/surname in tag
            for host in all_instance_info:     
                if host[0] in instance.tags[0].get('Value'):        # check hostname in tag
                    host[3] = instance.id
                    host[4] = instance.state.get('Name')
                    host[5] = instance.public_ip_address
                    host[6] = instance.tags[0].get('Value')
    return all_instance_info

					
def checkPorts(all_instance_info):
    """
	    Check host ports
    """
    print("Checking for open ports (please wait [{} sec timeout]):".format(config.socket_timeout))

    for host in all_instance_info:
        for port in config.scan_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(config.socket_timeout)	
            result = sock.connect_ex((host[1], int(port)))
            if(result == 0):
                text = TextColor.WHITE + "[" + TextColor.GREEN + "+" + TextColor.WHITE +"] Port open {}({}): {} ".format(host[0], host[1], port)
                print(text)
                host[2].append(str(port)) 
            else:
                text = TextColor.WHITE + "[" + TextColor.RED + "-" + TextColor.WHITE +"] Port open {}({}): {} ".format(host[0], host[1], port)
                print(text)
            sock.close()
    return all_instance_info
	
def createStopedInstanceAMI(all_instance_info):
    """
	    Create an AMI of the stopped EC2 instance and add a descriptive tag based on the EC2 name along with the current date.
    """
    print("Create AMI for stopped instances.")
	
    for host in all_instance_info:
        if host[4] == 'stopped':
            now = datetime.now()
            ami_name = host[6]
            ami_name = ami_name + now.strftime(" %H.%M %d.%m.%Y")
            ami_desc = 'Backup stopped instance: ' + ami_name

            ami_id = client.create_image(InstanceId=host[3], Name=ami_name, Description=ami_desc, NoReboot=True)
            ami_id = ami_id.get('ImageId')

            image = client.describe_images(ImageIds=[ami_id])
            text = TextColor.WHITE + "Creating AMI for " + str(host[0]) + " waiting..." 
            print(text)
            while image['Images'][0].get('State') == 'pending':
                time.sleep(5)
                image = client.describe_images(ImageIds=[ami_id])
            if image['Images'][0].get('State') == 'available':
                status = TextColor.GREEN + "success"
                client.terminate_instances(InstanceIds=[host[3]])
                text = TextColor.WARNING + "Instance " + str(host[0]) + " will be terminated." + TextColor.WHITE
                print(text)
            else:
                status = TextColor.RED + "fail"
            text = TextColor.WHITE + 'Status: ' + status + TextColor.WHITE 		
            print(text)    
    return all_instance_info
	
	
def deleteOldAMI(all_instance_info):
    """
	
    """
    text = TextColor.WARNING + "Warning! Deleting old AMI images..." + TextColor.WHITE
    image = client.describe_images(Owners=[config.owner_id])
    for im in image['Images']:
        if config.name_tag in im.get('Name'):
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            creation_date = datetime.strptime(im.get('CreationDate'), f)
            date_check = datetime.now() - creation_date
            if date_check.total_seconds() > 604800:
                text = TextColor.WARNING + "Will be deleted AMI id:" + str(im.get('ImageId')) + TextColor.WHITE
                client.deregister_image(ImageId=im.get('ImageId'))
                print(text)
            else:
                text = TextColor.WARNING + "No old images were found." + TextColor.WHITE
                print(text)
    return all_instance_info
	

	
def printAllInstancesStatus(all_instance_info):
    """
        Print instances status
    """
    print("Checking status of instances:")	
    for host in all_instance_info:
        if host[5] != None:
            if host[1] != host[5]:
                text = TextColor.WARNING + 'Warning! The ip_public(' + str(host[5]) + ') and ip_resolve(' + str(host[1]) + ') for host ' + str(host[0])+ ' is not same! Check A record in DNS.'		
                print(text)		
    for host in all_instance_info:  
        if host[4] == 'running':
            color = TextColor.GREEN
        else:
            color = TextColor.RED
        text = TextColor.WHITE + str(host[0]) + " [" + color + str(host[4]) + TextColor.WHITE + "]"	
        print(text)				
    return all_instance_info
	
def main():
    """
        Main function
    """
    getAllInstanceInfo(all_instance_info)
    printAllInstancesStatus(all_instance_info)
    checkPorts(all_instance_info) 
    createStopedInstanceAMI(all_instance_info)		
    deleteOldAMI(all_instance_info)
    printAllInstancesStatus(all_instance_info)	

if __name__ == '__main__':
    MaskTerminal().ShowMask()	# Крутое приветствие 
    main()