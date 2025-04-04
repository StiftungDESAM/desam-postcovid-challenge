## API

The API is implemented using the [Django Ninja REST Framework](https://django-ninja.dev/).
A detailed overview of all implemented endpoints can be found in the dedicated [API documentation](/api/docs).

### Authentication

The API uses a simple token system. Username and password are used to authenticate at at the `/user/login` endpoint.  This returns a token which must be provided in the request header in the following format:
```
Authorization: Bearer <token>
```

Tokens expire automatically after **24 hours**. Calling the `/user/logout` endpoint automatically deletes the token and thereby logs out the user. A system for automatically refreshing tokens is currently not implemented.

### Error handling

In the event of an error, an API endpoint should return the error message in the following schema:
```json
{
    "detail": "the error message to be sent to the frontend"
}
```

This can be achieved in Django-Ninja by raising an HttpError:
```python
raise HttpError(403, "Permission denied")
```

Unexpected errors that aren't handled by the endpoint automatically get converted into a server error with the HTTP status code 500 and are automatically logged in the backend.
