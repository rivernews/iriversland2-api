variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}

variable "app_container_image_tag" {
  default = "latest"
}

data "aws_ssm_parameter" "kubernetes_cluster_name" {
  name  = "terraform-managed.garage.cluster-name"
}

module "iriversland2_api" {
  source  = "rivernews/kubernetes-microservice/digitalocean"
  version = "v0.1.33"

  aws_region     = var.aws_region
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  cluster_name   = data.aws_ssm_parameter.kubernetes_cluster_name.value

  # app-specific config (microservice)
  app_label               = "iriversland2-api"
  app_exposed_port        = 8000
  app_deployed_domain     = "api.shaungc.com"
  cors_domain_whitelist   = ["shaungc.com"]
  app_container_image     = "shaungc/iriversland2-django"
  app_container_image_tag = var.app_container_image_tag
  app_secret_name_list = [
    "/provider/aws/account/iriversland2-15pro/AWS_REGION",
    "/provider/aws/account/iriversland2-15pro/AWS_ACCESS_KEY_ID",
    "/provider/aws/account/iriversland2-15pro/AWS_SECRET_ACCESS_KEY",

    "/app/iriversland2/DJANGO_SECRET_KEY",
    "/app/iriversland2/IPINFO_API_TOKEN",
    "/app/iriversland2/IPSTACK_API_TOKEN",
    "/app/iriversland2/RECAPTCHA_SECRET",

    "/app/iriversland2/SQL_DATABASE",
    "/database/postgres_cluster_kubernetes/SQL_USER",
    "/database/postgres_cluster_kubernetes/SQL_PASSWORD",
    "/database/postgres_cluster_kubernetes/SQL_HOST",
    "/database/postgres_cluster_kubernetes/SQL_PORT",

    "/database/redis_cluster_kubernetes/REDIS_HOST",
    "/database/redis_cluster_kubernetes/REDIS_PORT",
    "/app/iriversland2/CACHEOPS_REDIS_DB",

    "/service/gmail/EMAIL_HOST",
    "/service/gmail/EMAIL_HOST_USER",
    "/service/gmail/EMAIL_HOST_PASSWORD",
    "/service/gmail/EMAIL_PORT",
    "/service/slack/SEND_MESSAGE_URL"
  ]
  kubernetes_cron_jobs = [
    {
      name          = "db-backup-cronjob",
      #   cron_schedule = "0 * * * *",
      # every day 11:00pm PST, to avoid the maintenance windown of digitalocean in 12-4am
      cron_schedule = "0 6 * * *",
      command = ["/bin/sh", "-c", "echo Starting cron job... && sleep 5 && cd /usr/src/backend && echo Finish CD && python manage.py backup_db && echo Finish dj command"]
    },
  ]

  use_recreate_deployment_strategy = true

  depend_on = []
}
