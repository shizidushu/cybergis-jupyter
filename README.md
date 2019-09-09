# CyberGIS Jupyterhub Deployment on Docker Swarm mode

In order to support scaling of CyberGIS-Jupyter we are exploring the use of Docker Swarm. Docker Swarm is the simpler approach to doing scalable deployment. An alternative approach is Kubernetes which provides high availability and a robust failure recovery but the learning curve for this is quite steep. I heavily depended on [1] and [2] for my deployment.

## Setting up virtual machines on JetStream

Using the atmosphere interface of Jetstream [3], I set up two virtual machines on JetStream that has Ubuntu Server 18.04 with Docker installed. The docker version I used was 18.06.1-ce After setting up necessary access key for ssh, added user id to docker group so that I could run docker as non-root user (i.e. without sudo). In our approach we will be installing JupyterHub Server within the docker container without having to set it up on the host virtual machine. Additionally we will also configure nginx server to help with load balancing. Post 80 and 443 on the master node needs to be accessible from the outside.

Created a folder ```etc/jupyterhub``` as my own user and downloaded config files for jupyterhub from a github repository [4].
Setting up Swarm Master Node
On the virtual machine chosen to serve as master I configured the master using 
```
%docker swarm init --advertise-addr INTERNAL_IP_ADDRESS
```

The internal IP address of the master node is different from the external address seen from the atmosphere interface (find it using ```/sbin/ifconfig```). On successful setup the master will return a token along with a command that can be used by the worker node to join the swarm. This command along with the secret and join a new master or worker node to an existing swarm can be retrieved by running the following command on a master node

```
%docker swarm join-token manager
%docker swarm join-token worker
Useful Docker commands
%docker pull repository
%docker build PATH -t TAG
%docker ps -a
%docker service create REPOSITORY/IMAGE
%docker service ls
%docker service ps --no-trunc ServiceName
%docker service rm ServiceName
%docker events
%journalctl -u docker.service
%docker push repository/image
%docker node ls
%docker images ls
%docker exec -it 5ae5a20b657a bash
```
Cleanup of docker to free space on nodes
```
%docker rm -vf $(docker ps -aq)
%docker rmi -f $(docker images -aq)
%docker volume prune -f
```

## Install and Test NGINX Server
We are using Nginx from dockerhub and it sets in front of JupyterHub and serves as a proxy for JupyterHub
```
%docker pull nginx:latest
```
Create and launch nginx service with default configurations
```
%docker service create -name nginx   --publish 80:80  nginx
```
You can check if the nginx is configured correctly by going to the public url of the VM.

Finally remove the service using ```%docker service rm nginx```  

## Create a network
```
docker network create --driver overlay --attachable jupyterhub
```
## Install and Test JupyterHub 
Since we are using DockerSwarm and JupyterHub instance may be launched on any of the master or worker nodes, hence we will need to have any images we are using available on a public place like DockerHub. For this reason we will need to create a DockerHub account on  http://hub.docker.com and then creating a new repository

Under ```/etc/jupyterhub/hub``` there is a dockerfile which can be customized and built using ```%docker build . -t yourusername/jupyterhub-docker```. The created image can be committed and tagged using ```%docker commit ID jupyterhubserver``` and 
```%docker tag jupyterhubserver yourusername/jupyterhub-docker```. Then you login to dockerhub using docker ```%docker login``` and push the image created to remote repository using ```%docker push yourusername/jupyterhub-docker```.   

Next we create a common network that can be used by containers in the DockerSwarm to communicate easily and in an isolated fashion, using the command
```
%docker network create --driver overlay --attachable jupyterhub
```

Next we edit the configuration file jupyterhub_config.py specifically the following 
**The public facing ip of the whole application (the proxy)**
```
c.JupyterHub.ip = 'IP'
```
**The ip for this process**
```
c.JupyterHub.hub_ip = 'IP'
mounts = [{'type': 'volume',
           'source': 'jupyterhub-user-{username}',
           'target': notebook_dir,
        'no_copy' : True,
        'driver_config' : {
          'name' : 'local',
          'options' : {
             'type' : 'nfs4',
             'o' : 'addr=IP,rw',
             'device' : ':/var/nfs/{username}/'
           }
        },
```
For configuring the github authenticator we add the following lines
```
from oauthenticator.github import GitHubOAuthenticator
c.JupyterHub.authenticator_class = GitHubOAuthenticator
c.GitHubOAuthenticator.oauth_callback_url = 'http://129.114.16.224/hub/oauth_callback'
c.GitHubOAuthenticator.client_id = 'client_id'
c.GitHubOAuthenticator.client_secret = 'Client_Secret'
```
The client ID and secret can be found by registering a new application on github at [5]

In order to get jupyterhub log file added following entry
```
JupyterHub.extra_log_file = '/var/log/jupyterhub.log'
```
## Setting up NFS for shared permanent storage
### Setting up NFS Server
Note: You do not need to do most of this step if you already have an NFS. Instead use the NFS directory you already have 

On the master node, or a separate node if there is lot of IO operations, first install NFS server using instruction in [6]. Specifically this consists of
```
%apt-get install nfs-kernel-server
%sudo mkdir -p /var/nfs
%sudo chmod +777 /var/nfs
```
Then on JetSteam atmosphere web interface, create a volume. This by default gets mounted on ```/vol_b```
Add ```‘/dev/sdb /var/nfs ext4 defaults,nofail 0 2’``` to  ```/etc/fstab``` (this is essentially equivalent to running  ```%mount --bind /vol_b /var/nfs)```
Then add ```‘/var/nfs        *(rw,sync,no_subtree_check)’``` to ```/etc/exports```
Create ```/mnt %mkdir /mnt```

Run ```‘sudo exportfs -a’ ```to have NFS export the ```/mnt``` directory 

Finally add following to /etc/fstab
```‘INTERNAL_SERVER_IP:/var/nfs /mnt     nfs     auto    0       0’``` and ```run %sudo mount -a```
### Setting up NFS client
On each of the machine that is part of the swarm (i.e. runs worker or master) do the following
```
%sudo apt-get install nfs-common
%mkdir /mnt 
```
Finally add following to ```/etc/fstab```
```
‘INTERNAL_SERVER_IP:/var/nfs /mnt     nfs     auto    0       0’ 
```
and run ```%sudo mount -a``` (This is equivalent to running ```%sudo mount 172.19.119.13:/var/nfs /mnt``` but you have to do it just once rather than with every reboot)
## Create an NFS mount for container
To mount the NFS volume on the container run
```
%docker volume create --driver local --opt type=nfs4 --opt o=addr=INTERNEL_IP,rw   --opt device=:/var/nfs nfsvolume
```
## Starting JupyterHub and Nginx
Edit ```nginx.conf``` to add Public IP address to ```server_name``` parameter
Then run
```
%docker service create --name nginx --constraint 'node.role == manager' --publish 80:80 --detach=true --network jupyterhub --mount type=bind,src=/etc/jupyterhub/nginx.conf,dst=/etc/nginx/conf.d/default.conf  nginx
```
FInally run the following to launch jupyterHub
```
%docker service create --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock --mount type=bind,src=/etc/jupyterhub,dst=/srv/jupyterhub --mount src=nfsvolume,dst=/var/nfs --name jupyterhubserver --network jupyterhub --constraint 'node.role == manager' --detach=true  YOUR_USER_NAME/jupyterhub-docker:latest
```
## Handling IP Changes

You will need to edit the following files

1. launch_letsencrypt_container.sh or launch_service_letsencrypt.sh (change url)
2. Jupyterhub_config.py (change nfs portion of mount and callback url)
3. Add or edit /etc/exports and /etc/fstab
4. Delete and recreate the nfsvolume (change IP in   create_volume_nfs.sh)
5. Need to recreate juputerhub network


# Other Documetnations
1. https://docs.google.com/document/d/1o1m8sue0iU3Xud6eM3k37QrsKU99g5M2Q2WATV0prp8/edit?usp=sharing


## Reference
1. https://zonca.github.io/2017/10/scalable-jupyterhub-docker-swarm-mode.html
2. https://zero-to-jupyterhub.readthedocs.io/en/latest/ 
3. https://use.jetstream-cloud.org/application 
4. https://github.com/zonca/deploy-jupyterhub-dockerswarm 
5. https://github.com/settings/applications/new 
6. https://help.ubuntu.com/community/SettingUpNFSHowTo
7. Installing Docker - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04


