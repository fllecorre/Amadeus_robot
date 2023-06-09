"""
Test suite data for REST injections
"""
import os
import cyberarklib.aim

#Phase
environment = os.environ.get("ENVIRONMENT", "")

#Cyberark info to retrieve AMAIISDOM_PWD
AMAIISDOM_USER = "flecorre"
AMAIISDOM_PWD = cyberarklib.aim.get_password_and_conceal(
    cyb_object="WIN_account", appID="APS-B2B-OS-D", safe="APS-B2B-D"
)

# Dictionary for REST authentication
rest_context_dict = {
    "server_url": "https://qaproxy.forge.amadeus.net/api/tool/",
    "auth_token": {
        "token_type": "AMAIISDOM",
        "user_id": AMAIISDOM_USER,
        "password": AMAIISDOM_PWD
    }
}
    
#Directory paths
TEMP_DIRECTORY_PATH = "tmp/tmp.0751ZhHHNS/Inbox"
PROVIDER_DIRECTORY_PATH = f"ama/obe/{environment}/aps/vcp/data/vcp/Providers/"