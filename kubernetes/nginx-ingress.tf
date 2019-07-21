# code based: https://medium.com/@stepanvrany/terraforming-dok8s-helm-and-traefik-included-7ac42b5543dc
# Terraform official: helm_release - an instance of a chart running in a Kubernetes cluster. A Chart is a Helm package
# https://www.terraform.io/docs/providers/helm/release.html
# `helm_release` is similar to `helm install ...`
resource "helm_release" "project-nginx-ingress" {
  name = "nginx-ingress"

  # or chart = "stable/nginx-ingress"
  # see https://github.com/digitalocean/digitalocean-cloud-controller-manager/issues/162

  repository = "${data.helm_repository.stable.metadata.0.name}"
  chart      = "nginx-ingress"

  # helm chart values (equivalent to yaml)
  # https://github.com/terraform-providers/terraform-provider-helm/issues/145

  # `set` below refer to SO answer
  # https://stackoverflow.com/a/55968709/9814131

  # nginx-ingress-controller spec: https://github.com/bitnami/charts/tree/master/bitnami/nginx-ingress-controller

  set {
    name  = "controller.kind"
    value = "DaemonSet"
  }

  set {
    name  = "controller.hostNetwork"
    value = true
  }

  set {
    name  = "controller.dnsPolicy"
    value = "ClusterFirstWithHostNet"
  }

  set {
    name  = "controller.daemonset.useHostPort"
    value = true
  }

  set {
    name  = "controller.service.type"
    value = "ClusterIP"
  }

  set {
    name  = "rbac.create"
    value = true
  }

  set {
      name = "controller.publishService.enabled"
      value = true
  }

  depends_on = [
    "kubernetes_cluster_role_binding.tiller",
    "kubernetes_service_account.tiller"
  ]
}

# based on SO answer: https://stackoverflow.com/a/55968709/9814131
# format for `set` refer to official repo README: https://github.com/helm/charts/tree/master/stable/external-dns
provider "aws" {
  region     = "${var.aws_region}"
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
}
data "aws_route53_zone" "selected" {
  name         = "${var.managed_route53_zone_name}"
  private_zone = false
}
resource "helm_release" "project-external-dns" {
  name      = "external-dns"
  chart     = "stable/external-dns"
  namespace = "${kubernetes_service_account.tiller.metadata.0.namespace}"

  set {
    name  = "provider"
    value = "aws"
  }

  set {
    name  = "aws.credentials.accessKey"
    value = "${var.aws_access_key}"
  }

  set {
    name  = "aws.credentials.secretKey"
    value = "${var.aws_secret_key}"
  }

  set {
    name  = "aws.region"
    value = "${var.aws_region}"
  }

  # domains you want external-dns to be able to edit
  # see terraform official blog: https://www.hashicorp.com/blog/using-the-kubernetes-and-helm-providers-with-terraform-0-12
  set {
    name  = "domainFilters[0]"
    value = "${data.aws_route53_zone.selected.name}"
  }
  set {
    name  = "registry"
    value = "txt"
  }
  set {
    name  = "txt-owner-id"
    value = "${data.aws_route53_zone.selected.zone_id}"
  }

  set {
    name  = "policy"
    value = "sync" # "sync" | "upsert-only" (default): will disable deletion
  }

  set {
    name  = "rbac.create"
    value = true
  }

  depends_on = [
    "kubernetes_cluster_role_binding.tiller",
    "kubernetes_service_account.tiller"
  ]
}

# template copied from terraform official doc: https://www.terraform.io/docs/providers/kubernetes/r/ingress.html
# modified based on SO answer: https://stackoverflow.com/a/55968709/9814131
resource "kubernetes_ingress" "project-ingress-resource" {
  metadata {
    name = "project-ingress-resource"
    # namespace = "${kubernetes_service.app.metadata.0.namespace}"

    annotations = {
      "kubernetes.io/ingress.class" = "nginx"
      # "ingress.kubernetes.io/ssl-redirect": "true"
    }
  }

  spec {
    rule {
      host = "${var.app_deployed_domain}"
      http {
        path {
          backend {
            service_name = "${kubernetes_service.app.metadata.0.name}"
            service_port = "${var.app_exposed_port}"
          }

          path = "/"
        }

        # path {
        #   backend {
        #     service_name = "MyApp2"
        #     service_port = 8080
        #   }

        #   path = "/app2/*"
        # }
      }
    }

    # tls {
    #   secret_name = "tls-secret"
    # }
  }
}