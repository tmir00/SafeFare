This is our backend API documentation that incorporates digital wallet integration for payments, more private NFC tap-to-pay, and free transfer tracking within a 2-hour window from the first payment built using privacy by design principles.

# **Backend API Documentation**

## **Base URL**
```
https://<to_be_decided>.com/
```

## **Endpoints Overview**


### User Registration Endpoint
**POST** `/register/`
Creates a new user account with the provided username, password, and recovery seed hash.

**Request:**
```json
{
  "username": "newUser",
  "password": "userPassword",
  "recovery_seed_hash": "hashedRecoverySeedFromClient"
}
```

**Response:**
```json
{
  "username": "newUser",
  "token": "generatedTokenForAuthentication"
}
```
- `username`: The chosen username for the new account.
- `password`: The password for the account (sent as plain text but stored securely hashed).
- `recovery_seed_hash`: A client-provided hashed recovery seed.

---

### User Detail Endpoint
**GET** `/me/`
Retrieves the details of the authenticated user.

**Request:**
```plaintext
Authorization: Token userToken
```

**Response:**
```json
{
  "username": "existingUser",
  "number_of_tickets": 5
}
```
- Requires token authentication.
- `username`: The username of the authenticated user.
- `number_of_tickets`: The number of tickets associated with the user's account.

---

### Password Recovery Endpoint
**POST** `/recover/`
Allows a user to reset their password using their recovery seed.

**Request:**
```json
{
  "username": "existingUser",
  "recovery_seed": "userRecoverySeed",
  "new_password": "newUserPassword"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully."
}
```
- `username`: The username of the account being recovered.
- `recovery_seed`: The recovery seed provided by the user to reset the password.
- `new_password`: The new password the user wishes to set.

---

### Login Endpoint
**POST** `/login/`
Authenticates a user and returns a token for authorization in subsequent requests.

**Request:**
```json
{
  "username": "existingUser",
  "password": "userPassword"
}
```

**Response:**
```json
{
  "token": "generatedTokenForAuthentication"
}
```
- `username`: The username of the user trying to log in.
- `password`: The password of the user trying to log in.

---

### Stripe Customer Creation Endpoint
**POST /payments/setup/**
Sets up a Stripe customer with the provided token, preparing the user for future payments.
- **Request**:
  ```json
  {
    "token": "tok_visa"
  }
  ```
- **Response**:
  ```json
  {
    "stripe_customer_id": "cus_HKJsdh238"
  }
  ```
- **Attributes**:
  - `token`: A unique token representing the user's payment information, obtained through Stripe.js on the frontend.
  
---

### Payment Endpoint
**POST** `/payments/pay/`
Initiates a payment process for the authenticated user using their stored Stripe customer ID and returns a confirmation.

**Permissions:** Requires user authentication.

**Request Body:**
```
None
```
**Successful Response:**
```json
{
  "success": True,
  "tickets": "updatedNumberOfTickets",
  "payment_intent": "pi_123456789",
  "client_secret": "secret_123456789"
}
```
- `success`: A boolean indicating whether the payment was successfully initiated.
- `tickets`: The updated number of tickets for the user after the payment.
- `payment_intent`: The ID of the created Stripe PaymentIntent.
- `client_secret`: The client secret of the PaymentIntent, needed for client-side confirmation (if applicable).

**Error Response:**
```json
{
  "error": "Error message"
}
```
- For issues such as "Stripe customer ID not found for user" or any Stripe-related error.



## Additional Considerations
- OMNY removed trip history and charge history due to privacy concerns, can we implement one or both in a privacy preserving way?

