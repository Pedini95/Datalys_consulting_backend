ingress:
  enabled: true
  hosts:
    - host: ${PROJECT_NAME}.${SUFFIX_DOMAIN}
      paths: 
        - path: /