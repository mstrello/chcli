import os
import click
import requests
import json

class Config:
    def __init__(self):
        api_key = os.getenv('CH_API_KEY')
        if not api_key:
            raise RuntimeError(
                'chcli expects an environment variable called CH_API_KEY '
                'whith a valid CloudHealt API key.'
            )
        self.headers = {
            'Content-type': 'application/json',
            'Authorization': f'Bearer {api_key}'}
        self.base_url = 'https://chapi.cloudhealthtech.com/'
        self.log_level = 'NONE'

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.version_option("0.1")
@click.pass_context
def cli(ctx):
    """
    chcli is a command line tool for extracting data from ClodHealth without 
    to get into the console.  
    """
    # Create a config object and remember it as the context object.
    # This way other commands can use it with the @pass_config decorator.
    ctx.obj = Config()

@cli.command()
@pass_config
def list_customers(config):
    """
    List all the customers
    """
    url = config.base_url + 'v1/customers?'
    page_size = 100
    total_customers = 0

    # The API of CloudHealth uses pagination, in the customers
    # array we will agreggate all the data from all pages.
    customers = []
    page = 1
    while True:
        params = {'page': str(page), 'per_page': str(page_size)}
        res = requests.get(url, headers=config.headers, params=params)
        
        message = extract_json(res, url)
        customers.extend(message['customers'])
        customers_count = len(message['customers'])
        
        log(config.log_level, f'Page: {page} # Customers: {customers_count}')
        total_customers += customers_count
        if customers_count  == page_size:
            page += 1
        else:
            break
    
    # Print the list of customers
    sep = '-' * 85
    click.echo('{:30.30} {:12.12} {:25.25} {:15.15}'.format('Customer Name', 'Customer Id', 'Classification' ,'Partner Billing'))
    click.echo(sep)
    for customer in sorted(customers, key=lambda a: a['name'].lower()):
        click.echo('{:30.30} {:12.12} {:25.25} {:^15}'.format(
            customer['name'],
            str(customer['id']),
            customer['classification'],
            ('Yes' if customer['partner_billing_configuration']['enabled'] else 'No')
        ))
    click.echo(sep)
    click.echo(f'Total of customers: {total_customers}')

@cli.command()
@click.option('--customer-id', '-i', required=True)
@pass_config
def list_customer_accounts(config,customer_id):
    """
    List all the accounts for customer
    """
    url = config.base_url + (
        f'api/search.json?api_version=2&client_api_id={customer_id}'
        '&name=AwsAccount&fields=name,amazon_name,account_type,cluster_name'
    )
    res = requests.get(url, headers=config.headers)
    
    accounts = extract_json(res, url)
    total_accounts = len(accounts)
    # Print the list of accounts
    sep = '-' * 120
    click.echo('{:35.35} {:25.25} {:15.15} {:35.35}'.format('Name', 'Amazon Name', 'Account Type' ,'Payer Account'))
    click.echo(sep)
    for account in sorted(accounts, key=lambda a: (a['cluster_name']+a['account_type']).lower()):
        click.echo('{:35.35} {:25.25} {:^15} {:35.35}'.format(
            account['name'],
            account['amazon_name'],
            account['account_type'],
            account['cluster_name']
        ))
    click.echo(sep)
    click.echo(f'Total of accounts: {total_accounts}')

@cli.command()
@click.option('--customer-id', required=True)
@click.option('--show-subtotal', is_flag=True)
@pass_config
def list_customer_ec2_instances(config,customer_id, show_subtotal):
    """
    List all the EC2 instances for customer
    """
    url = config.base_url + (
        f'/api/search.json?api_version=2&client_api_id={customer_id}&name='
        'AwsInstance&query=is_active=1&fields=instance_id,name,instance_type.'
        'api_name,state,account.name'
    )
    res = requests.get(url, headers=config.headers)
    
    ec2_instances = extract_json(res, url)
    total_ec2_instances = len(ec2_instances)
    if show_subtotal:
        account_total = 0
        current_account = ''
    # Print the list of EC2 instances
    sep = '-' * 108
    click.echo('{:25.25} {:41.41} {:19.19} {:10.10} {:8.8}'.format('Account Name', 'Name', 'Instance Id' ,'Model', 'State'))
    click.echo(sep)
    for ec2_instance in sorted(ec2_instances, key=lambda a: (a['account']['name']+a['name']).lower()):
        if show_subtotal:
            account_total += 1
            if current_account != ec2_instance['account']['name']:
                if current_account == '':
                    current_account = ec2_instance['account']['name']
                else:
                    # Print subtotal
                    click.echo(sep)
                    click.echo(f'Total EC2 instances in {current_account}: {account_total}')
                    click.echo(sep)
                    current_account = ec2_instance['account']['name']
                    account_total = 0
        click.echo('{:25.25} {:41.41} {:19.19} {:10.10} {:8.8}'.format(
            ec2_instance['account']['name'],
            ec2_instance['name'],
            ec2_instance['instance_id'],
            ec2_instance['instance_type']['api_name'],
            ec2_instance['state']
        ))
    click.echo(sep)
    click.echo(f'Total of EC2 instances: {total_ec2_instances}')

@cli.command()
@click.option('--customer-id', '-i', required=True)
@pass_config
def list_customer_rds_instances(config,customer_id):
    """
    List all the RDS instances for customer
    """
    url = config.base_url + (
        f'/api/search.json?api_version=2&client_api_id={customer_id}&name='
        'AwsRdsInstance&query=is_active=1&fields=instance_id,flavor,engine,'
        'status,account.name'
    )
    res = requests.get(url, headers=config.headers)
    
    rds_instances = extract_json(res, url)
    total_rds_instances = len(rds_instances)
    # Print the list of EC2 instances
    sep = '-' * 94
    click.echo('{:25.25} {:30.30} {:12.12} {:12.12} {:10.10}'.format('Account Name', 'Instance Id', 'Model', 'Engine' ,'State'))
    click.echo(sep)
    for rds_instance in sorted(rds_instances, key=lambda a: (a['account']['name']+a['instance_id']).lower()):
        click.echo('{:25.25} {:30.30} {:12.12} {:12.12} {:10.10}'.format(
            rds_instance['account']['name'],
            rds_instance['instance_id'],
            rds_instance['flavor'],
            rds_instance['engine'],
            rds_instance['status']
        ))
    click.echo(sep)
    click.echo(f'Total of RDS instances: {total_rds_instances}')

def extract_json(response, url):
    # Sometimes in error conditions valid json is not returned
    try:
        response_message = response.json()
    except json.decoder.JSONDecodeError:
        response_message = response.text

    if response.status_code < 200 or response.status_code > 299:
        raise RuntimeError(
            f'Request to {url} failed! HTTP Error Code: {response.status_code} '
            f'Response: {response_message}'
        )

    return response_message

def log(level, message):
    if level != 'NONE':
        click.echo(f'[{level}] {message}')