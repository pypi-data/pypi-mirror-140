Bandwidth Subscriptions CLI Tool

This tool presents a CLI interface allowing you to manage Bandwidth webhook subscriptions with the Bandwidth API.  
(See https://dev.bandwidth.com/docs/account/subscriptions)

Requires Python 3.7+

This tool depends upon the following environment variables to be set:
    - bandwidth_account_id=<your account_id>
    - bandwidth_password=<your password>
    - bandwidth_site_id=<your site id>
    - bandwidth_url=https://dashboard.bandwidth.com/api
    - bandwidth_username=<your username>

Usage:

    - pip install bandwidth_cli
    - set env vars above
    - bandwidth_cli --help
