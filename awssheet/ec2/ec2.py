import boto3
from botocore.exceptions import ClientError
from django.conf import settings





def create_ec2_instance(name,AWS_ACCESS_KEY,AWS_SECRET_KEY,AWS_REGION):
    """
    Creates a new EC2 instance
    """

    # Set the AMI ID of the Amazon Machine Image you want to use
    ami_id = 'ami-04f1014c8adcfa670'

    # Set the instance type (e.g. t2.micro)
    instance_type = 't2.micro'

    # Set the key pair name for SSH access
    key_name = 'my_key_pair'

    # Set the security group IDs for the instance
    security_group_ids = ['default']

    # Create a new EC2 client
    ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

    try:
        # Delete the existing key pair
        ec2.delete_key_pair(KeyName=key_name)
    except ClientError as e:
        # Key pair does not exist
        pass

    # Create a new key pair
    response = ec2.create_key_pair(KeyName=key_name)

    # Write the private key to a file
    with open('my_key_pair.pem', 'w') as file:
        file.write(response['KeyMaterial'])

    # Launch a new EC2 instance
    response = ec2.run_instances(ImageId=ami_id, InstanceType=instance_type, KeyName=key_name, SecurityGroupIds=security_group_ids, MinCount=1, MaxCount=1)
    print(response)
    # Get the instance ID of the new instance
    instance = response[0]
    print(instance)
    instance_id=response['Instances'][0]['InstanceId']
    # instance.wait_until_running()
    # instance.reload()

    # Tag the instance with the specified name
    instance.create_tags(Tags=[{'Key': 'Name', 'Value': name}])


    print(f"New EC2 instance created with ID: {instance_id}")


def list_ec2_instances(AWS_ACCESS_KEY,AWS_SECRET_KEY,AWS_REGION):
    ec2_list=[]

   
    """
    Lists all EC2 instances across all regions
    """
    # Create a new EC2 client
 
    ec2_region = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

        # Get a list of all instances in the region
    
    instances = ec2_region.describe_instances()
   



        # Loop through each instance and print its ID and region
    for reservation in instances['Reservations']:

        for instance in reservation['Instances']:
            ec2_info = {}
                
            print(type(instance))
            instance_id = instance['InstanceId']
            ec2_info['Instance ID'] = instance_id
            ec2_info['InstanceType'] =instance['InstanceType']
            ec2_info['Placement'] =instance['Placement']['AvailabilityZone']
            ec2_info['PrivateDnsName'] =instance['PrivateDnsName']
            ec2_info['PrivateIpAddress'] =instance['PrivateIpAddress']
            ec2_info['PublicDnsName'] =instance['PublicDnsName']
            ec2_info['PublicIpAddress'] =instance['PublicIpAddress']
            ec2_info['State'] =instance['State']['Name']
            ec2_info['SubnetId'] =instance['SubnetId']
            ec2_info['VpcId'] =instance['VpcId']
            ec2_info['Architecture'] =instance['Architecture']
            ec2_info['CpuOptions'] =instance['CpuOptions']['CoreCount']
            ec2_info['PlatformDetails'] =instance['PlatformDetails']
            ec2_info['LaunchTime'] =str(instance['LaunchTime'])
            ec2_info['MaintenanceOptions'] =instance['MaintenanceOptions']['AutoRecovery']
            ec2_info['CurrentInstanceBootMode'] =instance['CurrentInstanceBootMode']
            # # ec2_info['Name'] = instance['Name']

# This loop will add all attributes of the EC2 instance to ec2_info
            for key, value in instance.items():
                print(f"Key: {key}, Value: {value}")
                # ec2_info[key] = value
            print(f"Instance ID: {instance_id}, Region: {AWS_REGION}")
            # Create empty row
           
            ec2_list.append(ec2_info)

    print(ec2_list)
    ec2_info={}
    ec2_info['Instance ID'] = ""
    ec2_info['InstanceType'] =""
    ec2_info['Placement'] =""
    ec2_info['PrivateDnsName'] =""
    ec2_info['PrivateIpAddress'] =""
    ec2_info['PublicDnsName'] =""
    ec2_info['PublicIpAddress'] =""
    ec2_info['State'] =""
    ec2_info['SubnetId'] =""
    ec2_info['VpcId'] =""
    ec2_info['Architecture'] =" "
    ec2_info['CpuOptions'] =""
    ec2_info['PlatformDetails'] =""
    ec2_info['LaunchTime'] =""
    ec2_info['MaintenanceOptions'] =""
    ec2_info['CurrentInstanceBootMode'] =""
    ec2_list.append(ec2_info)
    return ec2_list
