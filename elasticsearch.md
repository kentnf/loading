
## Install and start 

sudo apt install elasticsearch 		#(v6.4.1 for ubuntu 18.04)
sudo apt install kibana             #(v6.4.1 for ubuntu 18.04)
sudo service elasticsearch status
sudo service kibana start

curl 'http://localhost:9200/?pretty'
