docker service create \
  --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
  --mount type=bind,src=/etc/jupyterhub,dst=/srv/jupyterhub \
  --mount type=bind,src=/data/cigi/cybergis-jupyter/notebook_home_data,dst=/var/nfs \
  --name jupyterhubserver \
  --network jupyterhub \
  --constraint 'node.role == manager' \
  --detach=true \
  padmanab/cybergis-jupyter:latest
#  --mount src=nfsvolume,dst=/var/nfs \
