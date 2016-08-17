# API Documentation

## Endpoints:
- **create a user account**
  - Path: /api/v1/user_accounts/
  - Method: POST
  - Required Data: first_name, last_name, email, password
  - Returns: If successfully created returns *201 CREATED* Status Code, else
             if user already exists, returns *400 BAD REQUEST* with a response
             message "User already exists!"
  - Description: Creates a new user. Email must be unique. Will raise a 
                 BadRequest exception if a User with that email already exists.

- **user sign_in**
  - Path: /api/v1/user_accounts/{user_email}/{password}
  - Method: GET
  - Returns: User item with *200 OK* Status Code.
  - Description: Returns all user information their communities.

- **delete user**
  - Path: /api/v1/user_accounts/{user_email}/{password}
  - Method: DELETE
  - Returns: If successfully deletes returns *200 OK* Status Code.
  - Description: Deletes the user. If the user does not exist, BadRequest 
                 exception is raised with a message "User does not exist!"

- **getting all communities**
  - Path: /api/v1/communities/
  - Method: GET
  - Returns: city-state dictionary as key-value pair.
  - Description: Returns all cities with their value as states from the database.

- **edit user profile**
  - Path: /api/v1/user_accounts/{user_email}
  - Method: PUT
  - Parameters: profile_picture, primary_community, secondary_community
  - Returns: If successfully edited returns *200 OK* Status Code
  - Description: Updates user profile.