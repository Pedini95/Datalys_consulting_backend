ingress:

  enabled: true
  hosts:
    - host: ${PROJECT_NAME}-${APP_NAME}.${SUFFIX_DOMAIN}
      paths: 
        - path: /
        