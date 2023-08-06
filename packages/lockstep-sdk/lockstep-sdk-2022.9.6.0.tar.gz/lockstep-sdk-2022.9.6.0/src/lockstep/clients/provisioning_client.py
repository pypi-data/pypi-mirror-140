#
# Lockstep Software Development Kit for Python
#
# (c) 2021-2022 Lockstep, Inc.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
# @author     Ted Spence <tspence@lockstep.io>
# @copyright  2021-2022 Lockstep, Inc.
# @link       https://github.com/Lockstep-Network/lockstep-sdk-python
#

from lockstep.lockstep_response import LockstepResponse
from lockstep.models.provisioningmodel import ProvisioningModel
from lockstep.models.provisioningfinalizerequestmodel import ProvisioningFinalizeRequestModel
from lockstep.models.developeraccountsubmitmodel import DeveloperAccountSubmitModel

class ProvisioningClient:

    def __init__(self, client):
        self.client = client

    def provision_user_account(self, body: ProvisioningModel) -> LockstepResponse:
        """
        Creates a new User or updates an Invited user based on metadata
        provided by the User during the onboarding process

        Parameters
        ----------
        body : ProvisioningModel
            Represents a User and their related metadata
        """
        path = f"/api/v1/Provisioning"
        return self.client.send_request("POST", path, body, {"body": body})

    def finalize_user_account_provisioning(self, body: ProvisioningFinalizeRequestModel) -> LockstepResponse:
        """
        Updates user, company and group metadata for a User of status
        'Onboarding' and finalizes a user's onboarding process by
        changing the user status to 'Active'

        Parameters
        ----------
        body : ProvisioningFinalizeRequestModel
            Represents a User and their related metadata
        """
        path = f"/api/v1/Provisioning/finalize"
        return self.client.send_request("POST", path, body, {"body": body})

    def provision_free_developer_account(self, body: DeveloperAccountSubmitModel) -> LockstepResponse:
        """
        Creates a new account for a developer, sending an email with
        information on how to access the API.

        Parameters
        ----------
        body : DeveloperAccountSubmitModel

        """
        path = f"/api/v1/Provisioning/free-account"
        return self.client.send_request("POST", path, body, {"body": body})
