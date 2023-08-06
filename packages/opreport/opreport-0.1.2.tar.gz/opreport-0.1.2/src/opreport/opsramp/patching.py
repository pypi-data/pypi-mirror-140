def get_compliance_checks(openv, tenant=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/compliance'
    return openv.do_get(url)

def get_baselines(openv, tenant=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/baselines'
    return openv.do_get(url)

def get_baseline(openv, tenant=None, baseline_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/baselines/{baseline_id}'
    return openv.do_get(url)

def get_compliance_baselines(openv, tenant=None, compliance_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/compliance/{compliance_id}/baselines'
    return openv.do_get(url)

def get_compliance_devices(openv, tenant=None, compliance_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/compliance/{compliance_id}/devices'
    return openv.do_get(url)

def get_compliance_device_groups(openv, tenant=None, compliance_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/compliance/{compliance_id}/deviceGroups'
    return openv.do_get(url)

def get_configurations(openv, tenant=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/configurations/search'
    return openv.do_get(url)

def get_configuration(openv, tenant=None, configuration_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/configurations/{configuration_id}'
    return openv.do_get(url)

def get_patch(openv, tenant=None, integration_id=None, patch_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/rating/{integration_id}/feed/{patch_id}'
    return openv.do_get(url)

def get_patches(openv, tenant=None, queryString=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches'
    return openv.do_get(url, queryString=queryString)

def get_missing_scan_job_status(openv, tenant=None, job_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/{job_id}/scan/status'
    return openv.do_get(url)

def get_missing_scan_device_status(openv, tenant=None, resource_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/resources/{resource_id}/patches/scan/status'
    return openv.do_get(url)

def get_device_compliance_against_baseline(openv, tenant=None, resource_id=None, baseline_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/resources/{resource_id}/baselines/{baseline_id}/patches'
    return openv.do_get(url)

def get_patches_on_resources(openv, tenant=None, query_string=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/resources/patches'
    return openv.do_get(url,queryString=query_string)

def get_resources_against_compliance_baseline(openv, tenant=None, compliance_id=None, baseline_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/patchcompliance/{compliance_id}/baselines/{baseline_id}/resources'
    return openv.do_get(url)

def get_resources_in_group_against_compliance_baseline(openv, tenant=None, group_id=None, compliance_id=None, baseline_id=None):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/tenants/{tenant}/patches/patchcompliance/{compliance_id}/baselines/{baseline_id}/group/{group_id}'
    return openv.do_get(url)