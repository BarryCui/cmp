# Description
This is a small python flask program used to gather property data from multiple cloud sources and present them on web pages.
The following sources have been inregrated:
Aliyun, Azure, Oracle Cloud, DnsPod
## USER DOCUMENTATION
#### There are two ways to get started:
1. Build image by yourself locally and run it as a container.
2. Pull image from your aliyun container service repository and run it as a container.
No mather which way you choose, you'll need two files: .env and oci\_api\_key.pem

### The first way(Build docker image by yourself) 
1. Build Dockerfile
- sudo docker build -t icicle/cmp:v1 . --no-cache
2. Put oracle cloud pem key file into $(pwd)/.oci folder
3. Put .env file into $(pwd)/cmp/env folder and set up environment variables in it
4. Run Docker container
- sudo docker network create cmp-network
- sudo docker run --name cmp-redis --network cmp-network -d redis:alpine
- sudo docker run --name cmp-mysql -e MYSQL_ROOT_PASSWORD=<password> -e MYSQL_DATABASE=sysop_cmp --network cmp-network -d mysql:8.0 
- sudo docker run -d -p 8848:8000 -v $(pwd)/.oci:/root/.oci -v $(pwd)/cmp/env:/cmp/env --network cmp-network --name cmp-app icicle/cmp:v1
5. Open browser
- http://127.0.0.1:8848

### The second way(Pull docker image from aliyun)

1. Login 
- sudo docker login --username=<username> registry.cn-shanghai.aliyuncs.com
2. Pull image
- sudo docker pull registry.cn-shanghai.aliyuncs.com/xxx/cmp:<image-version-number>
3. Prepare .env file and oracle cloud pem key file
4. Put .env file under ./env/ and key file under ./.oci/ respectively
5. Run docker container
- sudo docker run -d -p 8000:8000 -v $(pwd)/.oci:/root/.oci:ro -v $(pwd)/env:/cmp/env:ro --name cmp registry.cn-shanghai.aliyuncs.com/xxx/cmp:<image-version-number>
6. Execute command to generate data
- sudo docker exec -it cmp /bin/bash
- flask generate
7. Open browser
- http://127.0.0.1:8848

### Environment Variables in .env file Introduction
#### aliyun related
For aliyun, we use accesskey & secret to authenticate.
```shell
#user1
user1_AccessKeyId="<access-key-id>"
user1_AccessKeySecret="<access-key-secret>"
user1_RegionId="<region-id>"
user1_AccountName="<account-name>"
user1_RegionId2="<second-region-id-if-you-have>"
#user2
user2_AccessKeyId="<access-key-id>"
user2_AccessKeySecret="<access-key-secret>"
user2_RegionId="<region-id>"
user2_AccountName="<second-account-name-if-you-have>"
user2_RegionId2="<second-region-id-if-you-have>"
```
#### oracle cloud related
For oracle cloud, we use API keys, you can create them under user settings.
```shell
OC_USER_OCID="<user-ocid>"
OC_FINGERPRINT="<key-file-fingerprint>"
OC_TENANCY="<tenancy-id>"
OC_KEY_FILE="~/.oci/oci_api_key.pem"
OC_REGION_1="<region-id>"
OC_REGION_2="<second-region-id-if-you-have>"
OC_REGION_3="third-region-id-if-you-have"
```
#### Azure related
For azure, we use service principal to authenticate. So if you don't have it, go create one.
```shell
APP_ID="<service-principal-app-id>"
PASSWORD="<service-principal-password>"
TENANT_ID="<tenant-id>"
APP_URL="<service-principal-app-url>"
RESOURCE_GROUP="<resource-group-name>"
SQL_SERVER_NAME="<sql-server-name-if-you-have>"
```
#### Dnspod
For dnspod, please refer to https://www.dnspod.cn/
```shell
LOGIN_TOKEN="<dnspod-token>"
```

## DEVELOPMENT DOCUMENTATION ##
1. Python setup
Under project root folder, do the following:
- python3 -m venv env  
- source env/bin/activate  
- pip install -r requirements.txt 
2. Edit .env file to set up environment variables and put it under ~/cmp/cmp/env/
3. Put pem key file under ~/.oci/ folder for the use of accessing oracle cloud api
4. Azure setup
Before start, you need to make sure that you have created a service principal for your azure account first.
If you haven't done it, please refer to the following documentation to create one.
###### Official documentation reference
https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?toc=%2Fazure%2Fazure-resource-manager%2Ftoc.json&view=azure-cli-latest

5. Import repo key
- sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
6. Create repo file
echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo
7. Install azure cli
- sudo yum -y install azure-cli
8. Set region to China
- az cloud set -n AzureChinaCloud
9. Sign in(Replace the variables to your own ones)
- az login --service-principal -u APP\_URL --username APP\_ID --password PASSWORD --tenant TENANT\_ID
10. change the following path:
- cmp/icicleazure.py: change load\_dotenv('/cmp/env/.env') to load\_dotenv('/your-home-directory/cmp/cmp/env/.env')
- cmp/commands.py: change load\_dotenv('/cmp/env/.env') to load\_dotenv('/your-home-directory/cmp/cmp/env/.env') 
11. Under project root folder, run this command to generate cloud property data
- flask generate
12. Start web server
- flask run --host=0.0.0.0
#### Project Description 
###### Directory tree
```shell
cmp_package 
├── cmp // package folder
│   ├── commands.py // commands to generate data
│   ├── env // used to store .env file
│   ├── errors.py // customized error pages
│   ├── iciclealiyun.py // fetch data from aliyun python api
│   ├── icicleazure.py // fetch data from azure-cli
│   ├── iciclednspod.py // fetch data from dnspod api
│   ├── icicleoracle.py // fetch data from oracle cloud python api
│   ├── __init__.py // This is the starting point.
│   ├── models.py // Define sql schemas
│   ├── settings.py // used to store db settings
│   ├── static // used to store js, css and images
│   ├── templates // html files
│   └── views.py // view functions to control data interactions
├── Dockerfile // used to make this whole app into a docker image
├── README.md // descriptions
├── requirements.txt // python libraries
└── wsgi.py // used by gunicorn, in order to find where flask app is located at.
```

