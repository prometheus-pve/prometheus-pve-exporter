#!/bin/sh

SSL="${PVE_VERIFYSSL:-false}"

if [ ! -f /config/pve.yml ]; then
        if [ -z ${PVE_USER+x} ] && [ -z ${PVE_PASSWORD+x} ]; then
                echo "Provide PVE_USER and PVE_PASSWORD variables !"
                exit 1
        else
                cat <<- EOF > /config/pve.yml
                        default:
                          user: "${PVE_USER}"
                          password: "${PVE_PASSWORD}"
                          verify_ssl: "${SSL}"
                EOF
        fi
fi

exec "$@"
