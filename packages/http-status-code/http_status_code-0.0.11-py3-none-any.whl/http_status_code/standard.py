from . import StatusCode

from . import StatusCode

# General
successful_request = StatusCode(200, 'Successful Request')
bad_request = StatusCode(400, f'Something went wrong. '
                              f'Our technical team is doing their best to take care of it.')
unauthorized_request = StatusCode(401, 'Unauthorized Request')
forbidden_request = StatusCode(403, 'Forbidden Request')
resource_not_found = StatusCode(404, 'The required resource is not found')
request_args_validation_error = StatusCode(422, 'Request arguments (query string or body) validation error')

# JWT
expired_token = StatusCode(432, 'The token is expired')
logged_out = StatusCode(433, 'You have logged out. Please log in again (Expired Session)')
wrong_token = StatusCode(434, 'Wrong token error (related to refresh and access tokens)')

# Authentication (Codes start from 430)
invalid_credentials = StatusCode(430, 'Invalid credentials')
inactive_account = StatusCode(431, 'Your account is inactive')
missing_token = StatusCode(438, 'Missing token')
invalid_token = StatusCode(437, 'The token is invalid')