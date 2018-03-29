sudo apt-get update
sudo apt-get install tomcat8
sudo service tomcat8 start
sudo apt-get install openjdk-8-jdk-headless
sudo apt-get install python2.7
wget https://res.cloudinary.com/negarr/raw/upload/v1522320270/py-fact.war
sudo mv py-fact.war /var/lib/tomcat8/webapps/
