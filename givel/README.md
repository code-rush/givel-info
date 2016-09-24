# API Documentation

## Endpoints:
- **create a user account**
  - Path: /api/v1/user_accounts/
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: first_name, last_name, email, password
  - Returns: If successfully created returns *201 CREATED* Status Code with a success message, 
             elseif user already exists, returns *400 BAD REQUEST* Status Code with a 
             message "User already exists!"
  - Description: Creates a new user. Email must be unique. Will raise a 
                 BadRequest exception if a User with that email already exists.

- **user sign_in**
  - Path: /api/v1/user_accounts/login
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: email, password
  - Returns: *200 OK* Status Code with a success message and result containing
             User information.
  - Description: If user exists and successfully logs in returns Users Information, else if 
                 user doesn't exist returns NotFound Exception with a message.

- **delete user**
  - Path: /api/v1/user_accounts/
  - Method: **DELETE**
  - Content-Type: application/json
  - Required Data: email, password
  - Returns: *200 OK* Status Code with a message if User successfully deleted.
  - Description: User needs to enter correct password inorder to delete the account.
                 If the user does not exist, BadRequest exception is raised with a 
                 message "User does not exist!"

- **get all communities**
  - Path: /api/v1/communities/
  - Method: **GET**
  - Returns: A success message with result as city-state dictionary key-value pair.
  - Description: Returns all cities with their value as states from the database.
                 States are abbreviated.

- **get user's profile picture**
  - Path: /api/v1/user_accounts/{user_email}/picture
  - Method: **GET**
  - Returns: User's profile picture link address with *200 OK* Status Code and a message.
  - Description: Returns user's profile picture with a success message else raises 
                 NotFound Exception if the picture does not exist.

- **add user's profile picture**
  - Path: /api/v1/user_accounts/{user_email}/picture
  - Method: **POST**
  - Content-Type: multipart/form-data
  - File: picture
  - Extensions Allowed: .jpg, .png, .jpeg.
  - Returns: If successfully added returns *200 OK* Status Code with a message.
  - Description: Uploads user's profile picture if file is in allowed extensions, else
                 returns a message "File not allowed".

- **delete user's profile picture**
  - Path: /api/v1/user_accounts/{user_email}/picture
  - Method: **DELETE**
  - Returns: *200 OK* Status Code with a message if picture successfully deleted.
  - Description: Deletes user's profile picture if exists else raises BadRequest Exception 
                 if picture does not exists.

- **add community to the user**
  - Path: /api/v1/user_accounts/{user_email}/communities/{community}
  - Method: **PUT**
  - Content-Type: application/json
  - Data: community
  - Returns: *200 OK* Status Code with a message if a community successfully added.
  - Description: Adds communities to user if followed. Provide what
                 community(**home/home_away**) to add in the url. In order to follow
                 a **home_away** community, a user must first follow a **home** community 
                 else it will raise a BadRequest Exception.

- **remove user's community**
  - Path: /api/v1/user_accounts/{user_email}/communities/{community}
  - Method: **DELETE**
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message if community successfully deleted.
  - Description: Deletes the community if unfollowed by the user. If a *home* community is 
                 deleted and there exists *home_away* then *home_away* community is changed 
                 to *home* community. If a request is sent to delete a community that does 
                 not exists then a BadRequest Exception is raised.

- **follow a user**
  - Path: /api/v1/users/{user_email}/following
  - Method: **PUT**
  - Content-Type: application/json
  - Data: follow_user
  - Returns: *200 OK* Status Code with a success message.
  - Description: Following a user. It adds the user to the following list and 
                 adds this user to the following users followers list.

- **get all users followings**
  - Path: /api/v1/users/{user_email}/following
  - Method: **GET**
  - Returns: Users all followings list as results with a message and *200 OK* Status Code.
  - Description: Get all list of user's following user list as results and also 
                 returns a message.

- **unfollow a user**
  - Path: /api/v1/users/{user_email}/following
  - Method: **DELETE**
  - Content-Type: application/json
  - Data: unfollow_user
  - Returns: *200 OK* Status Code with a success message.
  - Description: Removes the unfollowed user from the followings list and removes 
                 this user from followers list from the unfollowed user. Returns a message 
                 if this operation fails or is successfully executed.

- **get users followers**
  - Path: /api/v1/users/{user_email}/followers
  - Method: **GET**
  - Returns: List of all followers if any with a success message and *200 OK* Status Code.
  - Description: Returns all users followers as results with a message.

- **create post**
  - Path: /api/v1/users/{user_email}/post
  - Method: **POST**
  - Content-Type: multipart/form-data
  - Required Data: 
      - content= (some text)
      - file_count= 0 (default value should be 0. while sending file value is 
                       number of files. Max value is 1.)
  - Optional Data: 
      - file = (send file only if file_count is not 0)
      - location = (send location as 'city, state' only if location services 
                    services are on)
  - Allowed files: 
      - IMAGE(.jpg, .png, .jpeg)
      - VIDEOS(.mp4, .mpeg)
  - Returns:  *201 OK* Status Code and message if post created successfully.
              *400 BAD REQUEST* and message if failed to create post.
  - Description: Creates post. To create a post content is required. If the post does not
                 contain any data, it will raise a BadRequest Exception.
                 Provide location only when the user have their location services on
                 for the application. The location should be a string in the following 
                 syntax: "City, State".
  - IMPORTANT: Handle that the users should not be able to create empty post on the client side.

- **edit post**
  - Path: /api/v1/users/post/edit
  - Method: **PUT**
  - Content-Type: application/json
  - Data: content, post_id, post_key
  - Return: *200 OK* Status Code and message if post edited successfully.
  - Description: Edits post content. Once post is created, only the content is allowed 
                 to be edited.

- **get user's posts**
  - Path: /api/v1/users/{user_email}/post
  - Method: **GET**
  - Return: *200 OK* Status Code and message if fetched post successfully.
  - Description: Gets all users posts. 
                - Use *posted_time* to display time on post.

- **create challenge**
  - Path: /api/v1/users/{user_email}/challenge
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: description
  - Optional Data: location
  - Returns: *201 OK* Status Code and message if challenge created succesfully.
  - Description: Creates challenge. To create a challenge, description is required.
                 If it does not contain any description, it will raise a BadRequest
                 Exception with a message.
                 Provide location only when the user have their location services on
                 for the application. The location should be a string in the following 
                 syntax: "City, State".

- **edit challenge**
  - Path: /api/v1/users/challenge/edit
  - Method: **PUT**
  - Content-Type: application/json
  - Data: content, challenge_id, challenge_key
  - Return: *200 OK* Status Code and message if challenge edited successfully.
  - Description: Edits challenge description.

- **get user's posts**
  - Path: /api/v1/users/{user_email}/challenge
  - Method: **GET**
  - Return: *200 OK* Status Code and message if fetched challenges successfully.
  - Description: Gets all users challenges. 
                - Use *posted_time* to display time on challenge.

