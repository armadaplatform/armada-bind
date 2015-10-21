import os

import require_service
import haproxy


def main():
    service_name = os.environ.get('SERVICE_NAME')
    service_env = os.environ.get("SERVICE_ENV", os.environ.get("MICROSERVICE_ENV"))
    service_app_id = os.environ.get("SERVICE_APP_ID", os.environ.get("MICROSERVICE_APP_ID"))
    service_address = os.environ.get("SERVICE_ADDRESS")

    # If both name and address is supplied, name takes priority.
    if service_name:
        require_service.create_magellan_config(80, service_name, service_env, service_app_id)
    elif service_address:
        service_addresses = service_address.split(",")
        port_to_addresses = {
            80: service_addresses
        }
        haproxy.update_from_mapping(port_to_addresses)


if __name__ == '__main__':
    main()
