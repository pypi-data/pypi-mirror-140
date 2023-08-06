import requests

from .transaction import Transaction

"""FireflyIII API Driver.

API documentation: https://api-docs.firefly-iii.org
"""


class FireflyAPI:
    """Firefly API driver Class."""

    def __init__(self, hostname, auth_token):
        self.headers = {
            "Authorization": "Bearer " + auth_token if auth_token is not None else ""
        }
        self.hostname = (
            hostname
            if hostname is None or not hostname.endswith("/")
            else hostname[:-1]
        )  # Remove trailing backslash
        self.hostname = (
            self.hostname + "/api/v1/" if hostname is not None else self.hostname
        )
        self.api_test = self._test_api()

    def _test_api(self):
        """Tests API connection."""
        try:
            _ = self.get_about_user()
            return True
        except:
            return False

    def _post(self, endpoint, payload):
        """Handles general POST requests."""

        response = requests.post(
            "{}{}".format(self.hostname, endpoint),
            json=payload,
            # Pass extra headers, or it redirects to login
            headers={
                **self.headers,
                **{"Content-Type": "application/json", "accept": "application/json"},
            },
        )

        return response

    def _get(self, endpoint, params=None):
        """Handles general GET requests."""

        response = requests.get(
            "{}{}".format(self.hostname, endpoint), params=params, headers=self.headers
        )

        return response.json()

    def get_budgets(self):
        """Returns budgets of the user."""

        return self._get("budgets")

    def get_accounts(self, account_type="asset"):
        """Returns all user accounts."""

        return self._get("accounts", params={"type": account_type})

    def get_about_user(self):
        """Returns user information."""

        return self._get("about/user")

    def create_transaction(self, transaction: Transaction):
        """Creates a new transaction.
        data:
            pd.DataFrame

        `Amount, Description, Source account, Destination account, Category, Budget`
        Example:
            - A simple one:
                -> `5, Large Mocha, Cash`
            - One with all the fields being used:
                -> `5, Large Mocha, Cash, Starbucks, Coffee Category, Food Budget`
            - You can skip specfic fields by leaving them empty (except the first two):
                -> `5, Large Mocha, Cash, , , UCO Bank`
        """

        trans_data = transaction.to_dict(remove_none=True, api_safe=True)

        header = {k: v for k, v in trans_data.items() if k.startswith("header__")}
        body = {
            "transactions": [
                {k: v for k, v in trans_data.items() if not k.startswith("header__")}
            ]
        }

        payload = {**header, **body}

        return self._post(endpoint="transactions", payload=payload)
