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

- **get all communities**
  - Path: /api/v1/communities/
  - Method: GET
  - Returns: city-state dictionary as key-value pair.
  - Description: Returns all cities with their value as states from the database.
                 States are abbreviated.

- **get user's profile picture**
  - Path: /api/v1/user_accounts/{user_email}/picture
  - Method: GET
  - Returns: Picture file with *200 OK* Status Code
  - Description: Returns user's profile picture.

- **edit user's profile picture**
  - Path: /api/v1/user_accounts/{user_email}/picture
  - Method: PUT
  - Data: profile_picture
  - Returns: If successfully edited returns *200 OK* Status Code
  - Description: Updates user's profile picture.

- **delete user's profile picture**
  - Path: /api/v1/user_accounts/{user_email}/picture
  - Method: DELETE
  - Returns: *200 OK* Status Code.
  - Description: Deletes user's profile picture

- **add community to the user**
  - Path: /api/v1/user_accounts/{user_email}/communities/{community}
  - Method: PUT
  - Data: home, home_away
  - Returns: *200 OK* Status Code if successfully added.
  - Description: Adds communities to user if followed. Provide what
                 community(**home/home_away**) to add in the url.

- **remove user's community**
  - Path: /api/v1/user_accounts/{user_email}/communities/{community}
  - Method: DELETE
  - Returns: *200 OK* Status code if successfully deleted.
  - Description: Deletes the community if unfollowed by the user.

- **follow a user**
  - Path: /api/v1/users/{user_email}/following
  - Method: PUT
  - Returns: *200 OK* Status Code
  - Description: Following a user. It adds the user to the following list and 
                 adds this user to the following users followers list.

- **get all followers**
  - Path: /api/v1/users/{user_email}/following
  - Method: GET
  - Returns: Users all followings list.
  - Description: Get all list of users following user list.

- **unfollow a user**
  - Path: /api/v1/users/{user_email}/following
  - Method: DELETE
  - Returns: *200 OK* Status Code.
  - Description: Removes the unfollowed user from the followings list and removes 
                 this user from followers list from the unfollowed user.

- **get users followers**
  - Path: /api/v1/users/{user_email}/followers
  - Method: GET
  - Returns: List of all followers.
  - Description: Fetches all users followers and returns it.
