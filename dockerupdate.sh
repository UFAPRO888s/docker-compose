sudo docker stop app
sudo docker rm app
sudo docker build -t app .
sudo docker run -p 5000:5000 -p 8080:8080 --name app app