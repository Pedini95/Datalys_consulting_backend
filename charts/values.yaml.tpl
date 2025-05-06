ingress:
  enabled: true
  hosts:
    - host: ${PROJECT_NAME}.${SUFFIX_DOMAIN}
      paths: 
        - path: /
    - host: ${PROJECT_NAME}.k8s.vpc.hq.olr.lan
      paths: 
        - path: /