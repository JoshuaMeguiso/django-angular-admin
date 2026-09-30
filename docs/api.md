# API

The backend will expose versionable REST resources under `/api/`.

Planned resources include:

```text
/api/auth/
/api/products/
/api/categories/
/api/inventory/
/api/stock-movements/
```

Authentication endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/me/
```

Registration accepts `username`, `email`, `first_name`, `last_name`, and
`password`. Login returns a token and public user data. Send the token on
protected requests with the `Authorization: Token <token>` header.

List endpoints should use pagination, and validation errors should use a consistent structured response.
