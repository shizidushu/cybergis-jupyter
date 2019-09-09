import os

from oauthenticator.github import GitHubOAuthenticator

users = {
	'padmanabhananand', 
	'ddcamiu',
	'swuiuc',
	'CarnivalBug',
	'beckvalle',
	'kang716',
	'ZeweiXu',
	'zhiyuli',
	'alexandermichels',
	'danames',
	'xhqiao89',
        'N-Jaro',
	'ZhesongW',
#test Accounts
	'test78910',
	'FZtheBug',
	'GISCheng',
	'test-becky',
	'Stephenaaa',
	'summerschool-tester1',
	'ddtest2019',
	'cigijupyter',
	'jykang1522',
#Summer School 2019 Accounts
	'fupenghzau',
	'jwang-19',
	'zawoon96',
	'mehak-sachdeva',
	'swarnali29',
	'mmamanat',
	'zyykyy',
	'blieber1985',
	'yukiejiang',
	'Yalin1995',
	'AndongMa',
	'w412l907',
	'bowlick',
	'zhaoyun1230',
	'jimmy-feng',
	'akwerner',
	'keyao22',
	'david0811',
	'kh-id',
	'violine17',
	'eshook',
	'dianamaps',
	'zyykyy',
	'bidhya',
	'ZeweiXu',
	'ykarale',
	'mishkavance',
	'xiaonant',
	'bakkerbakker',
	'jinleegis',
	'alextimmons',
	'liyiphd',
	'meshghi',
	'puhuang1989',
	'Xuan4dream',
	'xdeng7',
	'JimColl',
	'vavramusser',
	'metrokim217',
	'Yuanyuan2018',
	'zhejiangsdm',
	'Peter-Kedron',
# Hour of CI
	'kkkemp',
##ZJU Summer Session
	'fangzhou129', 
	'Yeeyyor',
	'zjuGISwjh',
	'wangyix1126',
	'GodDamnGitHub',
	'qyn0729',
	'myjmyj1',
	'xujyz',
	'jinyujingjessie',
	'ChangyuzhuZJU',
	'XUHAN9954',
	'JiaPengYue',
	'1228762976',
	'wuwenqi0706',
	'jinyujingjessie',
	'Groot54203',
	'Cath-zj',
	'1228762976',
	'Zehimoo',
	'1CorgeXxxi',
	'lily-ky',
	'kantshe',
	'wuwenqi0706',
	'fiu-pi',
	'Chklast',
	'shiyuwang0921',
	'Wyichen430',
	'Shanmwy',
	'jinyujingjessie',
	'qinlugu',
	'zfy465914233',
	'junruz',
	'PorHoward',
	'pashaBiceps233',
	'ProHoward',
	'S-u-ing'
	}


c.JupyterHub.authenticator_class = GitHubOAuthenticator
c.GitHubOAuthenticator.oauth_callback_url = 'https://cybergis-jupyter.cigi.illinois.edu/hub/oauth_callback'
c.GitHubOAuthenticator.client_id = '209e85df92468e772473'
c.GitHubOAuthenticator.client_secret = '819b663e06a49b338923cc5a639a9aab32a077f3'
c.Authenticator.whitelist = users
#c.Authenticator.whitelist = {'padmanabhananand', 'ddcamiu','swuiuc','CarnivalBug','beckvalle','kang716','ZeweiXu','zhiyuli','alexandermichels','danames','xhqiao89','N-Jaro','test78910','ZhesongW','FZtheBug','GISCheng','test-becky','Stephenaaa','summerschool-tester1','ddtest2019','cigijupyter','jykang1522'}
c.Authenticator.admin_users = {'padmanabhananand','ddcamiu','CarnivalBug'}

## The public facing port of the proxy
c.JupyterHub.port = 8000
## The public facing ip of the whole application (the proxy)
c.JupyterHub.ip = '0.0.0.0'
## The ip for this process
c.JupyterHub.hub_ip = '0.0.0.0'

c.JupyterHub.extra_log_file = '/var/log/jupyterhub.log'

c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'


c.SwarmSpawner.jupyterhub_service_name = "jupyterhubserver"

c.SwarmSpawner.networks = ["jupyterhub"]

notebook_dir = os.environ.get('NOTEBOOK_DIR') or '/home/jovyan/work'
c.SwarmSpawner.notebook_dir = notebook_dir

mountlocal = {'type': 'bind',
              'source': '/data/cigi/cybergis-jupyter/notebook_home_data/{username}',
               'target': notebook_dir
}
mountlocalshared = {'type': 'bind',
              'source': '/data/cigi/cybergis-jupyter/notebook_shared_data',
               'target': '/share'
}
c.SwarmSpawner.container_spec = {
    # The command to run inside the service
    'args': ['/usr/local/bin/start-singleuser.sh'],  # (string or list)
    'Image': 'padmanab/cybergis-notebook:latest',
    'mounts': [mountlocal, mountlocalshared]
}

c.SwarmSpawner.resource_spec = {
    # (int)  CPU limit in units of 10^9 CPU shares.
    'cpu_limit': int(1 * 1e9),
    # (int)  Memory limit in Bytes.
    'mem_limit': int(4096 * 1e6),
    # (int)  CPU reservation in units of 10^9 CPU shares.
    'cpu_reservation': int(1 * 1e9),
    # (int)  Memory reservation in bytes
    'mem_reservation': int(4096 * 1e6),
}


# Remove containers once they are stopped
c.SwarmSpawner.remove_containers = True

# override templates to customize login page
# full path inside container
c.JupyterHub.template_paths = ['/srv/jupyterhub']

