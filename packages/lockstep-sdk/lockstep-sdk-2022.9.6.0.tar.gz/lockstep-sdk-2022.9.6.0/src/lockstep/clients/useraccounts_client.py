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
from lockstep.models.invitesubmitmodel import InviteSubmitModel
from lockstep.models.transferownersubmitmodel import TransferOwnerSubmitModel

class UserAccountsClient:

    def __init__(self, client):
        self.client = client

    def retrieve_user(self, id: str, include: str) -> LockstepResponse:
        """
        Retrieves the User with this identifier.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        id : str
            The unique ID number of the User to retrieve
        include : str
            To fetch additional data on this object, specify the list of
            elements to retrieve. Available collections: Notes,
            Attachments, CustomFields, AccountingRole
        """
        path = f"/api/v1/UserAccounts/{id}"
        return self.client.send_request("GET", path, None, {"id": id, "include": include})

    def update_user(self, id: str, body: object) -> LockstepResponse:
        """
        Updates a User that matches the specified id with the requested
        information.

        The PATCH method allows you to change specific values on the
        object while leaving other values alone. As input you should
        supply a list of field names and new values. If you do not
        provide the name of a field, that field will remain unchanged.
        This allows you to ensure that you are only updating the
        specific fields desired.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        id : str
            The unique ID number of the User to retrieve
        body : object
            A list of changes to apply to this User
        """
        path = f"/api/v1/UserAccounts/{id}"
        return self.client.send_request("PATCH", path, body, {"id": id, "body": body})

    def disable_user(self, id: str) -> LockstepResponse:
        """
        Disable the user referred to by this unique identifier.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        id : str
            The unique Lockstep Platform ID number of this User
        """
        path = f"/api/v1/UserAccounts/{id}"
        return self.client.send_request("DELETE", path, None, {"id": id})

    def reenable_user(self, id: str) -> LockstepResponse:
        """
        Reenable the user referred to by this unique identifier.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        id : str
            The unique Lockstep Platform ID number of this User
        """
        path = f"/api/v1/UserAccounts/reenable"
        return self.client.send_request("POST", path, None, {"id": id})

    def invite_user(self, body: list[InviteSubmitModel]) -> LockstepResponse:
        """
        Invite a user with the specified email to join your accounting
        group. The user will receive an email to set up their account.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        body : list[InviteSubmitModel]
            The user to invite
        """
        path = f"/api/v1/UserAccounts/invite"
        return self.client.send_request("POST", path, body, {"body": body})

    def retrieve_invite_data(self, code: str) -> LockstepResponse:
        """
        Retrieves invite information for the specified invite token.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        code : str
            The code of the invite
        """
        path = f"/api/v1/UserAccounts/invite"
        return self.client.send_request("GET", path, None, {"code": code})

    def transfer_owner(self, body: TransferOwnerSubmitModel) -> LockstepResponse:
        """
        Transfer the ownership of a group to another user. This API must
        be called by the current owner of the group.

        A User represents a person who has the ability to authenticate
        against the Lockstep Platform and use services such as Lockstep
        Inbox. A User is uniquely identified by an Azure identity, and
        each user must have an email address defined within their
        account. All Users must validate their email to make use of
        Lockstep platform services. Users may have different privileges
        and access control rights within the Lockstep Platform.

        Parameters
        ----------
        body : TransferOwnerSubmitModel

        """
        path = f"/api/v1/UserAccounts/transfer-owner"
        return self.client.send_request("POST", path, body, {"body": body})

    def query_users(self, filter: str, include: str, order: str, pageSize: int, pageNumber: int) -> LockstepResponse:
        """
        Queries Users for this account using the specified filtering,
        sorting, nested fetch, and pagination rules requested. A User
        represents a person who has the ability to authenticate against
        the Lockstep Platform and use services such as Lockstep Inbox. A
        User is uniquely identified by an Azure identity, and each user
        must have an email address defined within their account. All
        Users must validate their email to make use of Lockstep platform
        services. Users may have different privileges and access control
        rights within the Lockstep Platform.

        Parameters
        ----------
        filter : str
            The filter for this query. See [Searchlight Query
            Language](https://developer.lockstep.io/docs/querying-with-searchlight)
        include : str
            To fetch additional data on this object, specify the list of
            elements to retrieve. Available collections: Notes,
            Attachments, CustomFields, AccountingRole
        order : str
            The sort order for this query. See See [Searchlight Query
            Language](https://developer.lockstep.io/docs/querying-with-searchlight)
        pageSize : int
            The page size for results (default 200). See [Searchlight
            Query Language](https://developer.lockstep.io/docs/querying-with-searchlight)
        pageNumber : int
            The page number for results (default 0). See [Searchlight
            Query Language](https://developer.lockstep.io/docs/querying-with-searchlight)
        """
        path = f"/api/v1/UserAccounts/query"
        return self.client.send_request("GET", path, None, {"filter": filter, "include": include, "order": order, "pageSize": pageSize, "pageNumber": pageNumber})
