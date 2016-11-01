# API Documentation

## Endpoints:

### USER APIS
- **create a user account**
  - Path: /api/v1/users/accounts/
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: first_name, last_name, email, password
  - Returns: If successfully created returns *201 CREATED* Status Code with a success message, 
             elseif user already exists, returns *400 BAD REQUEST* Status Code with a 
             message "User already exists!"
  - Description: Creates a new user. Email must be unique. Will raise a 
                 BadRequest exception if a User with that email already exists.

- **user sign_in**
  - Path: /api/v1/users/accounts/login
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: email, password
  - Returns: *200 OK* Status Code with a success message and result containing
             User information.
  - Description: If user exists and successfully logs in returns Users Information, else if 
                 user doesn't exist returns NotFound Exception with a message.

- **delete user**
  - Path: /api/v1/users/accounts/
  - Method: **DELETE**
  - Content-Type: application/json
  - Required Data: email, password
  - Returns: *200 OK* Status Code with a message if User successfully deleted.
  - Description: User needs to enter correct password inorder to delete the account.
                 If the user does not exist, BadRequest exception is raised with a 
                 message "User does not exist!"


- **get user's profile picture**
  - Path: /api/v1/users/accounts/{user_email}/picture
  - Method: **GET**
  - Returns: User's profile picture link address with *200 OK* Status Code and a message.
  - Description: Returns user's profile picture with a success message else raises 
                 NotFound Exception if the picture does not exist.

- **add user's profile picture**
  - Path: /api/v1/users/accounts/{user_email}/picture
  - Method: **POST**
  - Content-Type: multipart/form-data
  - File: picture
  - Extensions Allowed: .jpg, .png, .jpeg.
  - Returns: If successfully added returns *200 OK* Status Code with a message.
  - Description: Uploads user's profile picture if file is in allowed extensions, else
                 returns a message "File not allowed".

- **delete user's profile picture**
  - Path: /api/v1/users/accounts/{user_email}/picture
  - Method: **DELETE**
  - Returns: *200 OK* Status Code with a message if picture successfully deleted.
  - Description: Deletes user's profile picture if exists else raises BadRequest Exception 
                 if picture does not exists.

- **add community to the user**
  - Path: /api/v1/users/accounts/{user_email}/communities/{community}
  - Method: **PUT**
  - Content-Type: application/json
  - Data: community
  - Returns: *200 OK* Status Code with a message if a community successfully added.
  - Description: Adds communities to user if followed. Provide what
                 community(**home/home_away**) to add in the url. In order to follow
                 a **home_away** community, a user must first follow a **home** community 
                 else it will raise a BadRequest Exception.

- **remove user's community**
  - Path: /api/v1/users/accounts/{user_email}/communities/{community}
  - Method: **DELETE**
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message if community successfully deleted.
  - Description: Deletes the community if unfollowed by the user. If a *home* community is 
                 deleted and there exists *home_away* then *home_away* community is changed 
                 to *home* community. If a request is sent to delete a community that does 
                 not exists then a BadRequest Exception is raised.

- **change user's password**
  - Path: /api/v1/user_accounts/{user_email}/password
  - Method: **PUT**
  - Required Data: current_password, new_password
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if the password changed successfully.
  - Description: Changes user's password. Current password is required to authenticate 
                 user and then the password is changed to the new password. 
                 Raises exception if any data is not provided.
                 Results in failure if the current password does not match user's current 
                 password.
  -IMPORTANT: Check if new_password and confirm_password matches on the front end 
              before sending the new password.


### COMMUNITY APIS
- **get all communities**
  - Path: /api/v1/communities/
  - Method: **GET**
  - Returns: results as an array of communities with city, state 
             member counts.
  - Description: Returns all communities in a dictionary with key city, state and members.
                 States are abbreviated. The client needs to sort them in the alphabetical 
                 order.


### USERS ACTIVITY APIS
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



### USERS POSTS APIS
- **create post**
  - Path: /api/v1/users/posts/{user_email}
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
  - Path: /api/v1/users/posts/{user_email}
  - Method: **PUT**
  - Content-Type: application/json
  - Data: content, id, key
  - Return: *200 OK* Status Code and message if post edited successfully.
  - Description: Edits post content. Once post is created, only the content is allowed 
                 to be edited. {user_email} is the email id for the one editing the post.
                 Only the creator of the post can edit the post. If someone else trys to
                 edit the post, it raises a BadRequest Exception.

- **get user's posts**
  - Path: /api/v1/users/posts/{user_email}
  - Method: **GET**
  - Return: *200 OK* Status Code and message if fetched post successfully.
  - Description: Gets all users posts. 
                - Use *posted_time* to display time on post.

- **delete user's post**
  - Path: /api/v1/users/posts/{user_email}
  - Method: **DELETE**
  - Required Data: id, key
  - Content-Type: application/json
  - Return: *200 OK* Status code if the post is deleted successfully.
  - Description: Deletes the user's post.  {user_email} is the email id for 
                 the one deleting the post.
                 Only the creator of the post can delete the post. If someone else trys to
                 delete the post, it raises a BadRequest Exception.                        

- **repost feed post**
  - Path: /api/v1/users/posts/repost/{user_email}
  - Method: **POST**
  - Data: id, key, location(optional)
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if repost is successful
  - Description: Reposts users feed post. The client should send key and id for the post 
                 and location if the location services are on.



### USERS CHALLENGES APIS

**Note** : - There are *FOUR STATES* in challenges.
             - ACTIVE, INACTIVE, COMPLETE, INCOMPLETE
           - When a user creates a new challenge, the challenge becomes 'ACTIVE' for 
             for the user who created/accepted the challenge and clock starts ticking from 
             that point. The user now has 48 hrs to complete the challenge. 
           - If the user does not respond in 48 hrs, the challenge becomes 'INACTIVE'. 
           - At any point of time during the challenge is 'ACTIVE' or 'INACTIVE, the user 
             can click the button where the clock is ticking and a question is popped up 
             asking if the user has completed the challenge. If the user selects *YES*,
             then the state of the challenge changes to 'COMPLETE' and they are praised with a 
             *Good Job* message. If the user selects *NO*, then the state changes to 
             'INCOMPLETE' and they are shown *Good Try* message.
           - Until they answer the question that if they have completed the challenge or not,
             the challenge stays in the 'INACTIVE' state even if the clock ticks down to 
             *'0h 0m'*, it should show *'0h 0m'* and not show any message. This means the 
             user still has to respond to the challenge.

- **create challenge**
  - Path: /api/v1/users/challenges/{user_email}
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: description
  - Optional Data: location
  - Returns: *201 OK* Status Code and message if challenge created succesfully.
  - Description: - Creates a new challenge. To create a challenge, description is required.
                 - If it does not contain any description, it will raise a BadRequest
                   Exception with a message.
                 - Provide location only when the user have their location services on
                   for the application. The location should be a string in the following 
                   syntax: "City, State".


- **edit challenge**
  - Path: /api/v1/users/challenges/{user_email}
  - Method: **PUT**
  - Content-Type: application/json
  - Data: description, state, id, key
  - Returns: *200 OK* Status Code and message if challenge edited successfully.
  - Description: - Edits challenge description. {user_email} is the email id for 
                   the one editing the challenge.
                 - Only the creator of the challenge can edit the challenge. If someone 
                   else trys to edit the challenge, it raises a BadRequest Exception.
                 - Either only description or state is sent in the request.
                 - state can either be 'incomplete', 'complete' or 'inactive'
                 - if the challenge has been created 48 hrs ago, the client should send 
                   a request to change the state of the challenge to 'inactive'.
                 - 'complete' and 'incomplete' states are the events occured only when 
                   the user interacts with it.

- **get user's challenges**
  - Path: /api/v1/users/challenges/{user_email}
  - Method: **GET**
  - Returns: *200 OK* Status Code and message if fetched challenges successfully.
  - Description: Gets all users challenges. 
                - Use *creation_time* to calculate time to display on challenge.

- **delete user's challenge**
  - Path: /api/v1/users/challenge/{user_email}
  - Method: **DELETE**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status code if the post is deleted successfully.
  - Description: - Deletes the user's challenge. {user_email} is the email id for 
                   the one deleting the challenge.
                 - Only the creator of the challenge can delete the challenge. If someone 
                   else trys to delete the challenge, it raises a BadRequest Exception.

- **repost challenge**
  - Path: /api/v1/users/challenges/repost/{user_email}
  - Method: **POST**
  - Required Data: id, key 
  - Optional Data: location
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if repost is successful
  - Description: Reposts users challenge. The client should send key and id for the post 
                 and location if the location services are on.

- **post challenge as own**
  - Path: /api/v1/users/challenges/post/{user_email}
  - Method: **POST**
  - Required Data: id, key 
  - Optional Data: location
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if repost is successful
  - Description: Makes other user challenges as their own. The client should send 
                 key and id for the challenge in the request and location if the location 
                 services are on.

- **accept challenge**
  - Path: /api/v1/users/challenges/accept/{user_email}
  - Method: **PUT**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if repost is successful
  - Description: Accepts challenges for the user.



### USERS FEED ACTIVITIES APIS
- **feed like/unlike**
  - Path: /api/v1/feeds/likes/{user_email}/{feed}
  - Method: **PUT**
  - Required Data: id, key, emotion
  - Content-Type: application/json
  - Returns: *200 OK* Status Code with a message if request is successful
  - Description: - Adds user's likes to a feed(post/challenge). 
                 - Provide id and key of the feed to be liked. 
                 - *emotion* can be either 'like' or 'unlike'. A user 
                   cannot 'unlike' a feed unless the user has 'liked' it first.
                 - If any other value than 'like' or 'unlike' is sent, it raises a 
                   BadRequest Exception.
                 - {user_email} is the email of the user who likes/unlikes the feed.
                 - {feed} is either *posts* or *challenges*. Any other value raises 
                   an exception.

- **post only to followers**
  - Path: /api/v1/users/accounts/settings/post_only_to_followers/{user_email}
  - Method: **PUT**
  - Required Data: value
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message.
  - Description: If *Post Only to Followers* is turned on, the feeds created from 
                 now on will only show to the followers, else they will show up 
                 on both communities and followers.
                 By default the post shows up to both communities and followers.
                 The value here is either 'true' or 'false'.

- **share stars**
  - Path: /api/v1/feeds/stars/share{user_email}/{feed}
  - Method: **PUT**
  - Required Data: id, key, stars
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message if the request is successful
  - Description: - Adds stars count to the post.
                 - If the stars to be donated are more than what the user have,
                   it raises a BadRequest Exception. (Though this should be handled 
                   on the client side to not go beyond the number of what the user has)
                 - {user_email} is the email of the user who donates the stars.
                 - {feed} is either *posts* or *challenges*. Any other value raises 
                   an exception.

- **share stars with followings**
  - Path: /api/v1/users/accounts/stars/share/{user_email}
  - Method: **PUT**
  - Required data: user_id, stars
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message
  - Description: {user_email} in the url is the email id of the logged in user 
                 who wants to share stars with others(followings).
                 The *user_id* is the of the user to whom the user is sharing stars
                 with and *stars* are the number of stars to be shared. *stars* can 
                 neither be greater than what the user is capable of sharing nor equal 
                 zero.

- **comment on feeds**
  - Path: /api/v1/feeds/comments/{user_email}
  - Method: **POST**
  - Required Data: id, key, comment
  - Content-Type: application/json
  - Returns: *200 OK* Status Code with a message
  - Description: {user_email} in the url is the email id of the logged in user.
                 *id* and *key* is the feed id and key which needs to be sent with the 
                 request else a BadRequest Exception is raised.
                 If an empty *comment* is sent in the request, it raises BadRequest 
                 Exception.

- **edit comment*
  - Path: /api/v1/feeds/comments/{user_email}
  - Method: **PUT**
  - Required Data: id, key, comment
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message if comment succesfully edited
  - Description: Edits users comments if they are the creator of the comment.
                 {user_email} in the url is the email if of the logged in user.
                 *id* and *key* here is the comment id and key which needs to be with 
                 the request else a BadRequest Exception is raised.
                 If an empty *comment* is sent in the request, it raises BadRequest 
                 Exception.

- **delete comment**
  - Path: /api/v1/feeds/comments/{user_email}
  - Method: **DELETE**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message if comment succesfully deleted
  - Description: Deletes users comments if they are the creator of the comment.
                 {user_email} in the url is the email if of the logged in user.
                 *id* and *key* here is the comment id and key which needs to be with 
                 the request else a BadRequest Exception is raised.

- **get comments**
  - Path: /api/v1/feeds/comments
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: List of comments that were made on the feed
  - Description: Gets all the comments made on the feed. 
                 *id* and *key* here are the feed id and key which needs to be sent 
                 with the request to fetch all comments made on that feed.

- **get feed likes**
  - Path: /api/v1/feeds/likes
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: List of users who liked the post
  - Description: Gets all users who liked the post.
                 *id* and *key* here are the feed id and key which needs to be sent 
                 with the request.

- **get feed stars**
  - Path: /api/v1/feeds/stars
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: List of users who gave stars to the post
  - Description: Gets all users who gave stars to the post.
                 *id* and *key* here are the feed id and key which needs to be sent 
                 with the request.

- **get community posts(feed)**
  - Path: /api/v1/communities/posts/{user_email}
  - Method: **GET**
  - Returns: Posts feeds in the community
  - Description: Gets the users feeds that are in the community of the logged in user.

- **get community challenges(feed)**
  - Path: /api/v1/communities/challenges/{user_email}
  - Method: **GET**
  - Returns: Challenges feeds in the community
  - Description: Gets the users post feeds that are in the community of the logged in user.

- **get following posts(feed)**
  - Path: /api/v1/users/following/posts/{user_email}
  - Method: **GET**
  - Returns: Posts feeds in the following.
  - Description: Returns all the posts of the followings.

- **get following challenges(feed)**
  - Path: /api/v1/users/following/challenges/{user_email}
  - Method: **GET**
  - Returns: Challenges feeds in the following.
  - Description: Returns all the challenges of the followings.

- **report post**
  - Path: /api/v1/reports/{feed}/{user_email}
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status Code and a message if the post reported successfully
  - Description:  - Reports a feed. If the user on givel felt that this post is 
                    not appropriate and choose to report it, this api reports the post to 
                    the company. 
                  - The client needs to send 'id' and 'key' of the post with the request.
                  - value for {feed} is either 'posts' or 'challenges'.



### USERS FAVORITES POSTS APIS
- **add post to favorites**
  - Path: /api/v1/users/posts/favorites/{user_email}
  - Method: **PUT**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if the post successfully added to the favorites
  - Description: Adds posts to users favorites.

- **delete post from favorites**
  - Path: /api/v1/users/posts/favorites/{user_email}
  - Method: **DELETE**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if the post successfully deleted from the favorites
  - Description: Deletes posts from the users favorites

- **get all favorite posts**
  - Path: /api/v1/users/posts/favorites/{user_email}
  - Method: **GET**
  - Returns: List of all user's favorites posts if any.
  - Description: Gets user's all favorites posts. If there aren't any favorite posts 
                 then the response will consist of just a message and no results.


### REPORT API
- **report post**
  - Path: api/v1/reports/{feed}/{user_email}
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: *200 OK* Status Code and a message if the post reported successfully.
  - Description: Reports users post. 
                 - The {feed} in the url is either 'posts' or 'challenges'.
                 - The {user_email} in the url is the email for the user who is reporting
                   the post.
                 - The client needs to send the *id* and *key* to report a post else a 
                   BadRequest Exception is raised.




