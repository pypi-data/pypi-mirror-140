# Streambird | Python API Client


## Installation

Install with PyPI (pip)

```bash
$ pip install --upgrade streambird
```

or install with Anaconda (conda)

```bash
$ conda install -c conda-forge streambird
```

## Usage

```python
import streambird

sb_client = streambird.Client("YOUR_API_KEY_HERE")
```

### Example


Start a email magic link flow:

```python
sb_client.magic_links.email.login_or_create(
    email='dev@streambird.io',
    login_redirect_url='https://example.com/login',
    registration_redirect_url='https://example.com/register',
)
```

Verify the magic llink token:

```python
sb_client.magic_links.verify(
    token='bbqg5fxQrCkgIZr3HyWlxNdZ5l_lDNPrRlxnQ0KHTBk',
)
```

## Error handling


If something went wrong while making API calls, then exceptions will be raised automatically
as a `StreambirdException` parent type and child exceptions:

- ``StreambirdInvalidRequest``: 400 - Bad Request -- The request was unacceptable, often due to missing a required parameter.
- ``StreambirdUnauthorized``: 401 - Unauthorized -- No valid API key provided.
- ``StreambirdNotEnabled``: 402 - Not enabled -- Please contact support@streambird.io before creating this type of task.
- ``StreambirdResourceNotFound``: 404 - Not Found -- The requested resource doesn't exist.
- ``StreambirdDuplicateResource``: 409 - Conflict -- Object already exists with same name, idempotency key or unique_id.
- ``StreambirdTooManyRequests``: 429 - Too Many Requests -- Too many requests hit the API too quickly.
- ``StreambirdInternalError``: 500 - Internal Server Error -- We had a problem with our server. Try again later.
- ``StreambirdServiceUnavailable``: 503 - Server Timeout From Request Queueing -- Try again later.
- ``StreambirdTimeoutError``: 504 - Server Timeout Error -- Try again later.

Check out [Streambird's API documentation]( <https://docs.streambird.io/reference#errors>) for more details.

## Troubleshooting

If you notice any problems, please email us at support@streambird.io.
