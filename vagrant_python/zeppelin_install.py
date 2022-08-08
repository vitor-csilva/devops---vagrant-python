from bdb import set_trace
import os
import subprocess

# Arquivo de Configuração do Zeppelin
def config_zeppelpin() -> str:
    return """[Unit]
              Description=Zeppelin service
              After=syslog.target network.target

              [Service]
              Type=forking
              ExecStart=/opt/zeppelin/bin/zeppelin-daemon.sh start
              ExecStop=/opt/zeppelin/bin/zeppelin-daemon.sh stop
              ExecReload=/opt/zeppelin/bin/zeppelin-daemon.sh reload
              User=zeppelin
              Group=zeppelin
              Restart=always

              [Install]
              WantedBy=multi-user.target"""

# Arquivo de configuração do Nginx
def config_nginx() -> str:
    """upstream zeppelin {
        server 127.0.0.1:8888;
        }
        server {
            listen 80;
            server_name zeppelin.example.com;
            return 301 https://$host$request_uri;
        }

        server {
            listen 443;
            server_name zeppelin.example.com;

            ssl_certificate           /etc/letsencrypt/live/zeppelin.example.com/fullchain.pem;
            ssl_certificate_key       /etc/letsencrypt/live/zeppelin.example.com/privkey.pem;

            ssl on;
            ssl_session_cache  builtin:1000  shared:SSL:10m;
            ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
            ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
            ssl_prefer_server_ciphers on;

            access_log  /var/log/nginx/zeppelin.access.log;

        location / {
                proxy_pass http://zeppelin;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $http_host;
                proxy_set_header X-NginX-Proxy true;
                proxy_redirect off;
            }
        location /ws {
            proxy_pass http://zeppelin/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade websocket;
            proxy_set_header Connection upgrade;
            proxy_read_timeout 86400;
            }
        }"""

##def config_anonymous() -> str:
    

def install_wget() -> None:
    os.system("sudo yum install wget -y")

def install_java() -> None:
    """_This function install java at CentOS """
    install_pkgs = ["java-11-openjdk-devel","java-11-openjdk",
                    "java-1.8.0-openjdk-devel", "java-1.8.0-openjdk"]
    cmd = "sudo yum install " + " ".join(install_pkgs) + " -y"
    #import pdb; pdb.set_trace()
    os.system(cmd)
    
    ## get path
    pwd_java = "readlink -f $(which java)"
    path = subprocess.check_output(pwd_java, shell=True)
    path = str(path.strip()).split("jre")
    
    ##
    java_home = path[0][:-1]
    
    os.system(f'echo "export JAVA_HOME={java_home}" >> ~/.bash_profile')
    os.system(f'echo "export JRE_HOME={java_home}/jre" >> ~/.bash_profile')
    os.system("source ~/.bash_profile")

#Script para instalação do Apache Zepplin
def install_zeppelin() -> None:
    
    os.system("wget https://dlcdn.apache.org/zeppelin/zeppelin-0.10.1/zeppelin-0.10.1-bin-all.tgz --no-check-certificate")
    os.system("sudo tar xvzf zeppelin-0.10.1-bin-all.tgz -C /opt")
    os.system("sudo mv /opt/zeppelin-*-bin-all /opt/zeppelin")
    
    os.system("sudo adduser -d /opt/zeppelin -s /sbin/nologin zeppelin")
    os.system("sudo chown -R zeppelin:zeppelin /opt/zeppelin")
    os.system("sudo touch /etc/systemd/system/zeppelin.service")
    os.system(f'echo "{config_zeppelpin()}" | sudo tee /etc/systemd/system/zeppelin.service')
    os.system("sudo systemctl start zeppelin")
    os.system("sudo systemctl enable zeppelin")
    
# Script de todos os pacotes necessários para realização da instalação do nginx
# (utilizado como reverse Prox para acesso via http)
def install_nginx():
    os.system("sudo yum install epel-release -y")
    os.system("sudo yum install nginx -y")
    
    #import pdb;pdb.set_trace()
    os.system("sudo systemctl start nginx")
    os.system("sudo systemctl enable nginx")
    os.system("sudo yum -y install certbot ")
    os.system(f'sudo firewall-cmd --zone=public --add-service=http --permanent \
             && sudo firewall-cmd --zone=public --add-service=https --permanent \
             && sudo firewall-cmd --reload \
             && sudo certbot certonly --webroot -w /usr/share/nginx/html -d zeppelin.example.com \
             && sudo crontab -e \
             && 30 5 * * * /usr/bin/certbot renew --quiet \
             && sudo touch /etc/nginx/conf.d/zeppelin.example.com.conf \
             && sudo echo "{config_nginx()}" | sudo tee /etc/nginx/conf.d/zeppelin.example.com.conf')
    os.system("sudo systemctl restart nginx zeppelin")
    
#def desable_anonymous_access() : 
#    os.system(f"sudo co /opt/zeppelin/conf/zeppelin-site.xml.template conf/zeppelin-site.xml" \
#             && 
#              )
    
    
    
install_wget()
install_java()
install_zeppelin()
install_nginx()