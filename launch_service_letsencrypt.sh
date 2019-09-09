docker service create \
  --name nginx \
  -p 443:443 \
  -p 80:80 \
  --detach \
  -e EMAIL=apadmana@illinois.edu \
  -e URL=cybergis-jupyter.cigi.illinois.edu \
  --constraint 'node.role == manager' \
  --network jupyterhub \
  --mount type=bind,src=/etc/jupyterhub/letsencrypt_container_nginx.conf,dst=/config/nginx/site-confs/default \
  --mount type=volume,src=nginx_volume,dst=/config \
  linuxserver/letsencrypt
