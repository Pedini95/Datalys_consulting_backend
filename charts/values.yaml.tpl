ingress:
  enabled: true
  hosts:
    - host: ${PROJECT_NAME}.${SUFFIX_DOMAIN}
      paths: 
        - path: /
    - host: ${PROJECT_NAME}.k8s.vpc.hq.olr.lan
      paths: 
        - path: /

persistence:
  enabled: true
  storageClass: longhorn
  mountPVC: true
  mountPath: /app/static
  storageSize: 5Gi


deployment:
  securityContext:
    fsGroup: 1000