docker login
docker build . -t shaungc/iriversland2-django:w-cred02 -f prod.Dockerfile
docker push shaungc/iriversland2-django:w-cred02