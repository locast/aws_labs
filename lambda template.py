from __future__ import print_function
import json
import boto3
import logging
import time
import datetime
##################
debug=True

target_tag_key = 'project'
target_tag_value = 'docker-mlm'

target_tag = 'docker_aws_mlm'
inventory_groups = ['manager', 'worker', 'DTR', 'Jenkins', 'gitlab']

inventory_s3_url = ""
instance_user= 'ubuntu'
inventory_link='inventory2.txt'

bucket_name = 'docker-mlm'

##################
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ids = []

    if debug:
        logger.info('event: ' + str(event))

    try:
        region = event['region']
        instance_id = event['detail']['instance-id']
    except Exception as error:    
        logger.error('principalId: ' + str(error))
    
    ec2 = boto3.resource('ec2')

    try:
        instance = ec2.Instance('instance_id')
        instance_tags = instance.tags
        instance_ip = instance.private_ip_address

        #instance_sshkey_name = 

    except Exception as error:
        logger.error('error: ' + str(error))

        if debug:
            instance_tags = {'debug':'true', project':'docker-mlm','role':'manager'}
            instance_ip = '192.168.4.6-debug'
            instance_sshkey='~/ssh/devops-key-debug'

    if debug:
        logger.info('tags: ' + str(instance_tags))
        logger.info('PIp: ' + str(instance_private_ip))

    # check if the created instance is part of project
    if target_tag_key in instance_tags:
        if target_tag_value == instance_tags[target_tag_key]:
            update_inventory()




def update_inventory(instance_tag_key, ):
    role = instance_tags['role']
    ansible_grp = '['+role+']\n'

    ### TODO ####
    READ INVENTORY IN S3
    ##############

    inventory_add_line = '{0} ansible_ssh_user={1} ansible_ssh_key={2}\n'.format(instance_ip, instance_user, instance_sshkey)

    if debug:
        logger.info('current_inventory: ' + str(inventory))
        logger.info('ansible_grp: ' + str(ansible_grp))
        logger.info('inventory_line: ' + str(inventory_add_line))

    if ansible_grp in inventory:
        if debug:
            logger.info('Ansible group found in inventory')

        index = inventory.index(ansible_grp)
        index = insert = index + 1
        present = False
        file_line = inventory[index]

        if debug:
            logger.info('ansible grp found in position: ' + str(index))

        while file_line[0] != '[' and index < len(inventory):
            file_line = inventory[index]

            if debug:
                logger.info('line in check for doublon: ' + str(file_line))

                    if file_line.split(' ')[0] == instance_ip:
                        print(instance_ip, file_line.split(' '))
                        present = True
                    index += 1
                print(present)
                if not present:
                    inventory.insert(insert, line)
            else:
                logger.info('Ansible group not found in inventory')
                inventory.append(ansible_grp)
                inventory.append(line)

            with open('/tmp/inventory.inv','w') as inventory_file:
                inventory = inventory_file.writelines(inventory)

            # Create an S3 client
            s3 = boto3.client('s3')

            # Uploads the given file using a managed uploader, which will split up large
            # files automatically and upload parts in parallel.
            s3.upload_file('/tmp/inventory.inv', bucket_name, 'inventory.inv')




def update_inventory(instance_ip, instance_tags, instance_sshkey, instance_user, inventory_link):
    #if target tag present
        fn = instance_tags['fn']
        ansible_grp = '['+fn+']\n'
###############
import boto3

client = boto3.client('s3') #low-level functional API

resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket('my-bucket') #subsitute this for your s3 bucket name.
        import pandas as pd

obj = client.get_object(Bucket='my-bucket', Key='path/to/my/table.csv')
grid_sizes = pd.read_csv(obj['Body'])
##########
        with open(inventory_link,'r') as inventory_file:
            inventory = inventory_file.readlines()
            print(inventory)
        print(inventory)

        line = '{0} ansible_ssh_user={1} ansible_ssh_key={2}\n'.format(instance_ip, instance_user, instance_sshkey)

        if ansible_grp in inventory:
            index = inventory.index(ansible_grp)

            index = insert = index + 1
            present = False
            file_line = inventory[index]
            print(index)
            while file_line[0] != '[' and index < len(inventory):
                file_line = inventory[index]
                print(file_line)
                if file_line.split(' ')[0] == instance_ip:
                    print(instance_ip, file_line.split(' '))
                    present = True
                index += 1
            print(present)
            if not present:
                inventory.insert(insert, line)
        else:
            inventory.append(ansible_grp)
            inventory.append(line)


        print(inventory)
        with open('inventory.inv','w') as inventory_file:
            inventory = inventory_file.writelines(inventory)

        # Create an S3 client
        s3 = boto3.client('s3')



###############"




# Uploads the given file using a managed uploader, which will split up large
# files automatically and upload parts in parallel.
s3.upload_file(filename, bucket_name, filename)
 
