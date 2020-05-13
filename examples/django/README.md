# Django flagship demo

### Set-up

virtualenv -p python3 env  
source env/bin/activate  
pip install -r requirements.txt

### Init DB migrations

python3 manage.py makemigrations  
python3 manage.py migrate  

### Run server

python3 manage.py runserver

### Create super user

python3 manage.py createsuperuser


### Build docker image

docker build -t fs-demo .

### Start image with docker-compose

docker-compose up -d 

### If you want to access the container

docker-compose exec web bash  
python manage.py createsuperuser

### Usage of Flagship

In the ecommerce demo, we connected Flagship inside a middleware.
We use Flagship to change the order of the menu items, and to toggle the display of the wishlist icon.
You can have a look at ./flagship_ecommerce_demo/middlewares.py to see how it is implemented