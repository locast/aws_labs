from __future__ import print_function
import json
import boto3
import logging
##################
debug=True

#tag to identify the instance of the project
target_tag_key = 'project'
target_tag_value = 'docker-mlm'

#Ansible_ssh_user
instance_user= 'ubuntu'

#aws S3 bucket name
bucket_name = 'docker-mlm'
#Inventory S3 path
bucket_key = 'Ansible/'
#Inventory name
inventory_name = 'inventory.inv'

##################
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if debug:
        logger.info('event: ' + str(event))

    try:
        instance_id = event['detail']['instance-id']
    except Exception as error:    
        logger.error(error)  

    ec2 = boto3.resource('ec2')

    try:
        instance = ec2.Instance(instance_id)
        base_tags = instance.tags
        instance_ip = instance.private_ip_address
        instance_sshkey = instance.key_name
    except Exception as error:
        logger.error(error)
        #default value to try the rest waiting authorisations
        base_tags = {{'Key' : 'debug','Value':'true'}, {'Key':'project','Value':'docker-mlm'},{'Key':'role','Value':'manager'}}
        instance_ip = '192.168.4.6-debug'
        instance_sshkey='~/ssh/devops-key-debug'

    #format tag as a python dictionary
    instance_tags = {}
    for tags in base_tags:
        instance_tags[tags['Key']] = tags['Value']

    if debug:
        logger.info('tags: ' + str(instance_tags))
        logger.info('PIp: ' + str(instance_ip))
        logger.info('key: ' + str(instance_sshkey))

    # check if the created instance is part of project
    if target_tag_key in instance_tags:
        if target_tag_value == instance_tags[target_tag_key]:

            roles = instance_tags['role']
            name = instance_tags['Name']
            #instances might haves many roles separated by: ","
            roles = roles.split(',')
            ansible_grps = [ '['+role+']\n' for role in roles ]

            #copy the inventory from S3 to /tmp
            try:
                # Create an S3 client
                s3 = boto3.client('s3')
                #copy inventory file in S3 to temp folder
                s3.download_file(bucket_name, bucket_key+inventory_name, '/tmp/'+inventory_name)
                with open('/tmp/'+inventory_name,'r') as inventory_file:
                    inventory = inventory_file.readlines()

                if debug:
                    logger.info('read_inventory: ' + str(inventory))
            except Exception as error:
                logger.error(error)
                inventory = []

           
            if debug:
                logger.info('current_inventory: ' + str(inventory))
                logger.info('ansible_grp: ' + str(ansible_grps))
                logger.info('inventory_line: ' + str(inventory_add_line)
            
            for ansible_grp in ansible_grps:
                # check if the group already is in inventory
                #Ansible inventory template line
                inventory_add_line = '{0} ansible_host={1} ansible_user={2} ansible_ssh_private_key_file={3}\n'.format(name, instance_ip, instance_user, instance_sshkey)

                if ansible_grp in inventory:

                    if debug:
                        logger.info('Ansible group found in inventory')

                    # Get the position of the group
                    index = inventory.index(ansible_grp)
                    index = insert = index + 1
                    present = False
                    file_line = inventory[index]

                    if debug:
                        logger.info('ansible grp found in position: ' + str(index))

                    # check all ip in the group
                    while file_line[0] != '[' and index < len(inventory):
                        file_line = inventory[index]

                        if debug:
                            logger.info('line in check for doublon: ' + str(file_line))

                        # check if the ip adress already is in the inventory
                        if file_line.split(' ')[0] == instance_ip:
                            present = True
                            index += 1

                            if debug:
                                logger.info('present: ' + str(present))
                                logger.info('instance_ip: ' + str(instance_ip))
                                logger.info('file_line: ' + file_line.split(' '))
                    # add line to inventory if ip not found
                    if not present:
                        inventory.insert(insert, inventory_add_line)

                # Add the new group and device t the ansible inventory
                else:
                    if debug:
                        logger.info('Ansible group not found in inventory')

                    # add both group and line if not found
                    inventory.append(ansible_grp)
                    inventory.append(inventory_add_line)

                    # Write the new inventory in /tmp
                    with open('/tmp/'+inventory_name,'w') as inventory_file:
                        inventory_file.writelines(inventory)

                    #Upload inventory to S3
                    try:
                        s3.upload_file('/tmp/'+inventory_name, bucket_name, bucket_key+inventory_name)
                    except Exception as error:
                        logger.error(error)
                    else:
                        logger.info('invotory writen in S3')
