import argparse
import sys
import opreport.helpers as helpers
from opreport.reports import network_utilization_report, utilization_comparison_report, patch_management_report, remote_control_usage_report
from opreport.opsramp.env import OpsRampEnv
import appdirs
import os
import traceback
import shutil

appauthor = "OpsRamp"
appname = "opreport"
default_conf_dir = appdirs.user_config_dir(appauthor, appname)
default_env_file = f'{default_conf_dir}{os.sep}environments.yml'
default_logo_file = f'{default_conf_dir}{os.sep}logo.jpeg'
default_output_dir = f'.{os.sep}output'
SAMPLE_ENVIRONMENTS = '''
#
# This file is used to provide named OpsRamp API credential sets
#


# Sample entries

- name: sample-environment-1
  url:  https://customername1.api.opsramp.com
  partner: msp_nnnnn                                    # If using a partner-level credential to do multi-client operations then use
  tenant: client_nnnnn                                  # the partner msp ID for both of these.
  client_id: oauth_client_id_from_integration
  client_secret: oauth_client_secret_from_integration
  vtoken: vtoken_from_integration                       # This line is only needed if sending alerts to an inbound webhook integration

- name: sample-environment-12
  url:  https://customername2.api.opsramp.com
  partner: msp_nnnnn
  tenant: client_nnnnn
  client_id: oauth_client_id_from_integration
  client_secret: oauth_client_secret_from_integration
  vtoken: vtoken_from_integration

#
# Add your entries below here
#
'''

def do_arg_parsing():
    parser = argparse.ArgumentParser(description='Multi-Client Reporting Utility for OpsRamp')
    subparsers = parser.add_subparsers(required=True, help='Available commands', dest='command')

    parser_uc = subparsers.add_parser('uc', help='Generate Server Utilization Comparison Reports')
    parser_uc.add_argument('--baseline_months_back', type=int, default=1, help='How many months back to use for the baseline data')
    subparsers.add_parser('nu', help='Generate Network Utilization  Reports')
    subparsers.add_parser('pm', help='Generate Patch Management Reports')
    subparsers.add_parser('rcu', help='Generate Remote Control Usage Reports')

    envfile_creds = parser.add_argument_group(title='Use yaml environment file credentials')
    cli_creds = parser.add_argument_group(title='Use command line credentials')

    envfile_creds.add_argument('--env', help='Name of environment to use, referencing a named set of API credentials in environments.yml')
    envfile_creds.add_argument('--envfile', default=default_env_file, help=f'Location of environments YAML file to be used (Default: {appdirs.user_config_dir(appauthor, appname)}{os.sep}environments.yml)')

    cli_creds.add_argument('--api_url', help='Customer-specific API URL such as https://mycompany.api.opsramp.com')
    cli_creds.add_argument('--key', help='Authentication key')
    cli_creds.add_argument('--secret', help='Authentication secret')
    cli_creds.add_argument('--tenant', help='Authentication secret')
    

    parser.add_argument('--start', help='Start date of reporting period in YYYY-MM-DD format (default=1st of prior month)')
    parser.add_argument('--end', help='End date of reporting period in YYYY-MM-DD format (default=Last day of prior month)')
    parser.add_argument('--outdir', default=default_output_dir, help=f'Directory where report output will be written (Default: {default_output_dir})')
    parser.add_argument('--logo', default=default_logo_file, help=f'Logo image file for report headers (Default: {default_logo_file})')
    parser.add_argument('--secure', default=True, help='Whether or not to verify SSL cert (Default: True)')
    parser.add_argument('--tenant_criteria', help='Search criteria for which tenants to include as per https://develop.opsramp.com/tenancy-access-controls/tenants-orgid-clients-search (Default: "activeStatus:true", which will include all active tenants)')

    args = parser.parse_args()
    return args



def main():

    try:
        if not (len(sys.argv) == 2 and sys.argv[1] == '-h'):
            try:
                f = open(default_env_file, 'r')
                f.close()
            except FileNotFoundError:
                print(f'\nCould not find default environments file {default_env_file}, so creating it with sample content.\nPlease update it with your OpsRamp partner-level API credentials.')
                print('Run again with -h option to see available options and commands.\n')
                os.makedirs(default_conf_dir)
                env_file = open(default_env_file, "w")
                env_file.write(SAMPLE_ENVIRONMENTS)
                env_file.close()
                shutil.copy(f'{os.path.dirname(__file__)}{os.sep}..{os.sep}conf{os.sep}sample-logo.jpeg', default_logo_file)
                sys.exit(0)

        args = do_arg_parsing()

        if args.env is None and (args.api_url is None or args.key is None or args.secret is None or args.tenant is None) :
            print('For authentication, either the --env option referencing to a named set of API credentials in environments.yml, or all of: --api_url, --key, --secret, --tenant must be provided.')
            sys.exit(1)

        if args.env is not None and (args.api_url is not None or args.key is not None or args.secret is not None or args.tenant is not None) :
            print('For authentication, use either the --env option referencing to a named set of API credentials in environments.yml, or --api_url, --key, --secret, and --tenant - not both.')
            sys.exit(1)
        
        if args.env is None:
            print('\nUsing API credentials provided in command line')

        else:
            print(f'\nGetting environment named {args.env} from {args.envfile}')

        print(f'Report output will be sent to {args.outdir}')

        openv = OpsRampEnv(args.env, args.api_url, args.key, args.secret, None, args.tenant, args.envfile, args.secure)
        tenants = openv.get_tenants(queryString=args.tenant_criteria)
        dateranges = helpers.compute_dates(args)

        if args.command == 'uc':
            utilization_comparison_report.report(openv, tenants, dateranges, args.outdir, args.logo)
        elif args.command == 'nu':
            network_utilization_report.report(openv, tenants, dateranges, args.outdir, args.logo)
        elif args.command == 'pm':
            patch_management_report.report(openv, tenants, dateranges, args.outdir, args.logo)
        elif args.command == 'rcu':
            remote_control_usage_report.report(openv, tenants, dateranges, args.outdir, args.logo)
        print("Done")
    except Exception as err:
        print('\nAn error has occurred:\n')
        print(f"{err.args=}\n")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        print(__file__)


if __name__ == "__main__":
    # execute only if run as a script
    main()
