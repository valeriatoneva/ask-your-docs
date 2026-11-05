# REST API error handling

A REST API communicates the result of a request with HTTP status codes. A 200 means success, 201 means a resource was created, and 204 means success with no body, which is typical for a delete. The 400 code means the request was invalid, 401 means the caller is not authenticated, 403 means the caller is authenticated but not allowed, and 404 means the resource does not exist. Server problems use 500 codes.

On the client, handle errors in one central place instead of in every call. In Angular an HTTP interceptor can catch failed responses, show a friendly message, and redirect to the login page on a 401. Retry only requests that are safe to repeat, such as GET, and use a short delay between attempts.

Response bodies can differ between endpoints: one may return an array, another an object with a nested items property. Normalise the response into one internal shape as soon as it arrives, so the rest of the application does not depend on each endpoint format. Always validate the data before using it.

Never show raw server errors to users. Log the technical details and show a short message that tells the user what to do next.
