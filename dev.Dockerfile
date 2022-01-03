## Stage 1: Angular ##
##
##

# FROM node:10-stretch-slim as ng_stage_image

# # Copy project

# WORKDIR /usr/src

# # for dev purpose, copy all including credentials
# # for prod, you want to exclude credentials. Consider using a `.dockerignore` file. See https://stackoverflow.com/questions/43747776/copy-with-docker-but-with-exclusion
# COPY . .

# # Install dependencies

# WORKDIR /usr/src/frontend

# RUN npm i && npm rebuild node-sass

# # only build dev; for production please add --prod
# RUN $(npm bin)/ng build

## Stage 2: Django ##
##
##

FROM python:3.10-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PROJECT_DIR /usr/src

# Set work directory
# sets the working directory for docker commands e.g. RUN, CMD, ENTRYPOINT, COPY and ADD.
# also WORKDIR will auto-create directory if not exist.
WORKDIR ${PROJECT_DIR}/backend

# Copy project

COPY backend/requirements.txt requirements.txt

# Install dependencies

RUN pip install --upgrade pip && pip install -r requirements.txt

# COPY --from=ng_stage_image ${PROJECT_DIR}/backend/frontend-bundle-dist ${PROJECT_DIR}/backend/frontend-bundle-dist
# RUN chmod +x ./recollect_static.sh && ./recollect_static.sh

# Entry point

# vscode remote does not support EXPOSE, we use `appPort` in `.devcontainer.json` instead
# for production build, you might want to include EXPOSE

CMD ["python", "manage.py", "runserver", "0.0.0.0", "8000"]
