if ! command -v docker &> /dev/null; then
    sudo span install -y docker
fi

if ! command -v nginx &> /dev/null; then
    sudo apt install -y nginx
fi

if [ ! -f /etc/nginx/sites-available/fastapi ]; then

    sudo rm -f /etc/nginx/sites-enabled/default
    sudo bash -c 'cat > /etc/nginx/sites-available/fastapi <<EOF
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF'
    sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled
    sudo systemctl restart nginx
fi

cd service
sudo docker rm -f app-container
sudo docker build -f Dockerfile.prod -t app-image .
sudo docker run --env-file env -d --name app-container -p 8000:8000 app-image