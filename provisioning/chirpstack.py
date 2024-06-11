import json
import grpc
import requests
import secret
import sys
from chirpstack_api import api

class Device:
    def __init__(self, dev_eui, name, description, application_id, device_profile_id, is_disabled):
        self.dev_eui            = dev_eui
        self.name               = name
        self.description        = description
        self.application_id     = application_id
        self.device_profile_id  = device_profile_id
        self.is_disabled        = is_disabled

class DeviceKeys:
    def __init__(self, dev_eui, network_key, application_key):
        self.dev_eui            = dev_eui
        self.network_key        = network_key
        self.application_key    = application_key

class DeviceProfile:
    def __init__(self, name, region, mac_version, reg_params_revision, adr_algorithm_id, flush_queue_on_activate, uplink_interval, supports_otaa, supports_class_b, supports_class_c):
        self.name                       = name
        self.region                     = region
        self.mac_version                = mac_version
        self.reg_params_revision        = reg_params_revision
        self.adr_algorithm_id           = adr_algorithm_id
        self.flush_queue_on_activate    = flush_queue_on_activate
        self.uplink_interval            = uplink_interval
        self.supports_otaa              = supports_otaa
        self.supports_class_b           = supports_class_b
        self.supports_class_c           = supports_class_c

def get_application(channel, auth_token, tenant_id, device_type):
    client = api.ApplicationServiceStub(channel)
    req = api.ListApplicationsRequest()
    req.tenant_id   = tenant_id
    req.limit       = 1000
    req.search      = device_type
    resp = client.List(req, metadata=auth_token)
    return resp

def create_application(channel, auth_token, tenant_id, device_type):
    client = api.ApplicationServiceStub(channel)
    req = api.CreateApplicationRequest()
    req.application.tenant_id   = tenant_id
    req.application.name        = device_type
    req.application.description = f'Application for {device_type} devices'
    resp = client.Create(req, metadata=auth_token)
    return resp

def get_device_profile(channel, auth_token, tenant_id, device_type):
    client = api.DeviceProfileServiceStub(channel)
    req = api.ListDeviceProfilesRequest()
    req.tenant_id   = tenant_id
    req.limit       = 1000
    req.search      = device_type
    resp = client.List(req, metadata=auth_token)
    return resp

def create_device_profile(channel, auth_token, tenant_id, device_profile):
    client = api.DeviceProfileServiceStub(channel)
    req = api.CreateDeviceProfileRequest()
    req.device_profile.tenant_id                = tenant_id
    req.device_profile.name                     = device_profile.name
    req.device_profile.description              = f'Device profile for {device_profile.name} devices'
    req.device_profile.region                   = device_profile.region
    req.device_profile.mac_version              = device_profile.mac_version
    req.device_profile.reg_params_revision      = device_profile.reg_params_revision
    req.device_profile.adr_algorithm_id         = device_profile.adr_algorithm_id
    req.device_profile.flush_queue_on_activate  = device_profile.flush_queue_on_activate
    req.device_profile.uplink_interval          = device_profile.uplink_interval
    req.device_profile.supports_otaa            = device_profile.supports_otaa
    req.device_profile.supports_class_b         = device_profile.supports_class_b
    req.device_profile.supports_class_c         = device_profile.supports_class_c
    resp = client.Create(req, metadata=auth_token)
    return resp

def create_device(channel, auth_token, device):
    client = api.DeviceServiceStub(channel)
    req = api.CreateDeviceRequest()
    req.device.dev_eui              = str(device.dev_eui)
    req.device.name                 = str(device.name)
    req.device.description          = str(device.description)
    req.device.application_id       = str(device.application_id)
    req.device.device_profile_id    = str(device.device_profile_id)
    req.device.is_disabled          = device.is_disabled
    resp = client.Create(req, metadata=auth_token)
    return resp

def create_device_keys(channel, auth_token, device_keys):
    client = api.DeviceServiceStub(channel)
    req = api.CreateDeviceKeysRequest()
    req.device_keys.dev_eui = str(device_keys.dev_eui)
    req.device_keys.nwk_key = str(device_keys.network_key)
    req.device_keys.app_key = str(device_keys.application_key)
    resp = client.CreateKeys(req, metadata=auth_token)
    return resp

def update_device(channel, auth_token, device):
    client = api.DeviceServiceStub(channel)
    req = api.UpdateDeviceRequest()
    req.device.dev_eui              = str(device.dev_eui)
    req.device.name                 = str(device.name)
    req.device.description          = str(device.description)
    req.device.application_id       = str(device.application_id)
    req.device.device_profile_id    = str(device.device_profile_id)
    req.device.is_disabled          = device.is_disabled
    resp = client.Update(req, metadata=auth_token)
    return resp

def update_device_keys(channel, auth_token, device_keys):
    client = api.DeviceServiceStub(channel)
    req = api.UpdateDeviceKeysRequest()
    req.device_keys.dev_eui = str(device_keys.dev_eui)
    req.device_keys.nwk_key = str(device_keys.network_key)
    req.device_keys.app_key = str(device_keys.application_key)
    resp = client.UpdateKeys(req, metadata=auth_token)
    return resp

def delete_device(channel, auth_token, dev_eui):
    client = api.DeviceServiceStub(channel)
    req = api.DeleteDeviceRequest()
    req.dev_eui = str(dev_eui)
    resp = client.Delete(req, metadata=auth_token)
    return resp

def main():
    input = json.load(sys.stdin)
    mode = sys.argv[1]

    server = secret.chirpstack_server
    tenant_id = secret.chirpstack_tenant_id
    api_token = secret.chirpstack_api_token

    channel = grpc.insecure_channel(server)
    auth_token = [("authorization", "Bearer %s" % api_token)]

    if mode == 'create' or mode == 'update':
        manufacturer = input['manufacturer']
        model = input['model']
        device_type = f"{manufacturer} / {model}"
        resp = get_application(channel, auth_token, tenant_id, device_type)
        application_exists = False
        if hasattr(resp, 'result'):
            for item in resp.result:
                if item.name == device_type:
                    application_exists = True
                    application_id = item.id
        if not application_exists:
            resp = create_application(channel, auth_token, tenant_id, device_type)
            application_id = resp.id

        resp = get_device_profile(channel, auth_token, tenant_id, device_type)
        device_profile_exists = False
        if hasattr(resp, 'result'):
            for item in resp.result:
                if item.name == device_type:
                    device_profile_exists = True
                    device_profile_id = item.id
        if not device_profile_exists:
            r = requests.get(f'https://raw.githubusercontent.com/stellio-hub/device-catalog/main/manufacturers/{manufacturer}/models/{model}/config.json')
            if r.status_code not in [200, 201, 204]:
                raise Exception('Issue when calling device-catalog GitHub')
            else:
                config = r.json()['chirpstack']
                device_profile = DeviceProfile(device_type, config['region'], config['macVersion'], config['regParamsRevision'], config['adrAlgorithmId'], config['flushQueueOnActivate'], config['uplinkInterval'], config['supportsOTAA'], config['supportsClassB'], config['supportsClassC'])
                resp = create_device_profile(channel, auth_token, tenant_id, device_profile)
                device_profile_id = resp.id

    if mode == 'create':
        device = Device(input['devEUI'], input['name'], input['description'], application_id, device_profile_id, (not input['isEnabled']))
        device_keys = DeviceKeys(input['devEUI'], input['applicationKey'], input['applicationKey'])
        resp = create_device(channel, auth_token, device), create_device_keys(channel, auth_token, device_keys)
        print(resp)

    elif mode == 'update':
        device = Device(input['devEUI'], input['name'], input['description'], application_id, device_profile_id, (not input['isEnabled']))
        device_keys = DeviceKeys(input['devEUI'], input['applicationKey'], input['applicationKey'])
        resp = update_device(channel, auth_token, device), update_device_keys(channel, auth_token, device_keys)
        print(resp)

    elif mode == 'delete':
        resp = delete_device(channel, auth_token, input['devEUI'])
        print(resp)

    else:
        raise Exception('Unkonwn mode')

if __name__ == "__main__":
    main()