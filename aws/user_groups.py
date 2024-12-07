import boto3
import json

# Create client for IAM
iam_client = boto3.client('iam')

# Step 1: Create user groups with all the needed access
def create_iam_group(group_name, policies_arns):
    try:
        # Create group
        iam_client.create_group(GroupName=group_name)
        print(f"Group {group_name} created successfully")
        
        # Add the policies to the group
        for policy_arn in policies_arns:
            iam_client.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
            print(f"Policy {policy_arn} attached to group {group_name}.")
    except Exception as e:
        print(f"Error creating group: {e}")
        
# Step 2: Create a user and add it to the group
def create_iam_user(user_name, group_name):
    try:
        # Create the user
        iam_client.create_user(UserName=user_name)
        print(f"User {user_name} created successfully.")
        
        # Add user to the group
        iam_client.add_user_to_group(GroupName=group_name, UserName=user_name)
        print(f"User {user_name} added to group {group_name}.")
        
        # Generate access credentials
        credentials = iam_client.create_access_key(UserName=user_name)
        
        # Serialize credentials, ensuring datetime is handled correctly
        credentials['AccessKey']['CreateDate'] = credentials['AccessKey']['CreateDate'].isoformat()
        print("Credentials created:")
        print(json.dumps(credentials['AccessKey'], indent=2))
    except Exception as e:
        print(f"Error creating user: {e}")
        
# Setup
group_name = "admin_db_group"
user_name = "angel_db_admin"
policies_arns = [
    "arn:aws:iam::aws:policy/AdministratorAccess",
    "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
]

create_iam_group(group_name, policies_arns)
create_iam_user(user_name, group_name)