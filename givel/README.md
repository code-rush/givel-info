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

- **get user's stars**
  - Path: /api/v1/profile/users/stars/{user_email}
  - Method: **GET**
  - Returns: *200 OK* Status Code with a message and result if the request is successful.
  - Description: Gets users stars.


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
- **follow a user/organization**
  - Path: /api/v1/users/{user_email}/following
  - Method: **PUT**
  - Content-Type: application/json
  - Required_Data: follow
  - Returns: *200 OK* Status Code with a success message.
  - Description: Following a user. It adds the user to the following list and 
                 adds this user to the following users followers list.

- **get users followings**
  - Path: /api/v1/users/following
  - Method: **POST**
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: Users all followings list as results with a message and *200 OK* Status Code.
  - Description: Gets all list of user's followings as results. Alongwith the results it 
                 also sends a *last_evaluated_key* parameter to get more results if all 
                 results are not fetched. If the response does not contain *last_evaluated_key*, 
                 it means all results have been fetched in the response.
                 The *user_id* is the *email* of the logged_in user.

- **unfollow a user/organization**
  - Path: /api/v1/users/{user_email}/following
  - Method: **DELETE**
  - Content-Type: application/json
  - Required_Data: unfollow
  - Returns: *200 OK* Status Code with a success message.
  - Description: Removes the unfollowed user from the followings list and removes 
                 this user from followers list from the unfollowed user. Returns a message 
                 if this operation fails or is successfully executed.

- **get users followers**
  - Path: /api/v1/users/followers
  - Method: **POST**
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: List of all followers if any with a success message and *200 OK* Status Code.
  - Description: Returns all users followers as results with a message. Alongwith the results it 
                 also sends a *last_evaluated_key* parameter to get more results if all 
                 results are not fetched. If the response does not contain *last_evaluated_key*, 
                 it means all results have been fetched in the response.
                 The *user_id* is the *email* of the logged_in user.



### USERS POSTS APIS
- **create post**
  - Path: /api/v1/users/posts/{user_email}
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: 
      - content= (some text)
      - file_count= 0 (default value should be 0. while sending file value is 
                       number of files. Max value is 1.)
  - Optional Data: 
      - location = (send location as 'city, state' only if location services 
                    services are on)
      - tags = (Array of dictionaries). Send *user_id*, *origin* and *length* 
                for each user who is being tagged on the post.
                - *user_id*: user's id
                - *origin*: origin of the person being tagged
                - *length*: length of their tag. (Could be either 
                            full or first name)
  - Returns:  - If *file_count* is not **0** then, the response will contain feed's *id* 
                 and *key*. Use this feed *id* and *key* to send the file in 
                 **add files to the post** api.
              - *201 OK* Status Code and message if post created successfully.
              - *400 BAD REQUEST* and message if failed to create post.
  - Description: Creates post. To create a post content is required. If the post does not
                 contain any data, it will raise a BadRequest Exception.
                 Provide *location* only when the user have their location services on
                 for the application. The location should be a string in the following 
                 syntax: "City, State".
  - IMPORTANT: Handle that the users should not be able to create empty post on the client side.

  - **NOTE:** - To remove file(s) and edit post contents, use **edit post** api.
              - To add file(s) to the feed, use **add files to the post** api.
                - Even when a user edits the post by just adding a file, only use the 
                  **add files to the post** to send the file to the server and add to the post.
                - While creating a post if the user sends in both *content* and *file*, 
                  create a post first with the **create post** api and in the response of 
                  that api, it has that feed's *id* and *key*, Use this to add file to that 
                  feed with **add files to the post** api. 

- **add files to the post**
  - Path: /api/v1/users/posts/files/{user_email}
  - Method: **PUT**
  - Content-Type: multipart/form-data
  - Required Data: id, key, file_count, file
                - file_count= 0 (default value should be 0. while sending file value is 
                       number of files. Max value is 1.)
                - file = (send file only if file_count is not 0)
  - Allowed files: 
      - IMAGE(.jpg, .png, .jpeg)
      - VIDEOS(.mp4, .mpeg)
  - Returns: *200 OK* Status Code with a successful message if the file added successfully.
  - Description: Adds files to the post. Use this api only to add file to the post.

- **edit post**
  - Path: /api/v1/users/posts/{user_email}
  - Method: **PUT**
  - Content-Type: application/json
  - Data: content, id, key, tags, file
         - content: (text)
         - id: feed_id (text)
         - key: feed_key (text)
         - tags: (Array of dictionaries). Send *user_id*, *origin* and *length* 
                for each user who is being tagged on the post.
                - *user_id*: user's id
                - *origin*: origin of the person being tagged
                - *length*: length of their tag. (Could be either 
                            full or first name)
         - file: (the only possible value is 'remove' to remove a file from post) (text)
  - Return: *200 OK* Status Code and message if post edited successfully.
  - Description: Edits post content. Once post is created, only the content is allowed 
                 to be edited. {user_email} is the email id for the one editing the post.
                 Only the creator of the post can edit the post. If someone else trys to
                 edit the post, it raises a BadRequest Exception.
  - **NOTE:** - There are two ways a user can edit tags:
                1) Add new tags.
                2) Remove exisisting tags.

              - Regardless of however they edit the tags, always send in the final tags 
                after the edit.
                **For example:** If *Bob* and *Cat* were two people tagged in a post 
                earlier and if the *Cat* was removed, even then send *Bob* in tags again.
                And if only *Bob* was tagged in a post and *Cat* was added while editing,
                send *Bob* again alongwith *Cat* in the tags with the tagging parameters
                (*user_id*, *origin* and *length*)
              - While editing the post, even if the tags are not edited, the location 
                of the tags will change and so the client needs to send tags everytime the 
                post is edited.


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
  - Path: /api/v1/users/challenges/{user_email}
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
  - Description: Accepts challenges for the user. Provide challenge_id and challenge_key 
                 as the *id* and *key* in the data for the challenge to be accepted by 
                 user.




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
  - Optional Data: tags
  - Content-Type: application/json
  - Returns: *200 OK* Status Code with a message
  - Description: - {user_email} in the url is the email id of the logged in user.
                 - *id* and *key* is the feed id and key which needs to be sent with the 
                   request else a BadRequest Exception is raised.
                 - If an empty *comment* is sent in the request, it raises BadRequest 
                   Exception.
                 - For tagging, send the data as array of dictionaries for each tag. 
                   Use "user_id" Key to send the tagged user's id, "origin" for the 
                   the place where the tag for that user started and "length" for 
                   the total length of that tag.

- **edit comment*
  - Path: /api/v1/feeds/comments/{user_email}
  - Method: **PUT**
  - Required Data: id, key, comment, tags
  - Content-Type: application/json
  - Returns: *200 OK* Status code with a message if comment succesfully edited
  - Description: Edits users comments if they are the creator of the comment.
                 {user_email} in the url is the email if of the logged in user.
                 *id* and *key* here is the comment id and key which needs to be with 
                 the request else a BadRequest Exception is raised.
                 If an empty *comment* is sent in the request, it raises BadRequest 
                 Exception.
  - **NOTE:** - There are two ways a user can edit tags:
                1) Add new tags.
                2) Remove exisisting tags.

              - Regardless of however they edit the tags, always send in the final tags 
                after the edit.
                **For example:** If *Bob* and *Cat* were two people tagged in a post 
                earlier and if the *Cat* was removed, even then send *Bob* in tags again.
                And if only *Bob* was tagged in a post and *Cat* was added while editing,
                send *Bob* again alongwith *Cat* in the tags with the tagging parameters
                (*user_id*, *origin* and *length*)
              - While editing the comment, even if the tags are not edited, the location 
                of the tags will change and so the client needs to send tags everytime the 
                comment is edited.


- **delete comment**
  - Path: /api/v1/feeds/comments/{user_email}
  - Method: **DELETE**
  - Required Data: id, key, feed_id
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
  - Path: /api/v1/feeds/likes/{user_email}
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: List of users who liked the post
  - Description: Gets all users who liked the post.
                 *id* and *key* here are the feed id and key which needs to be sent 
                 with the request.
                 In the *user_following*, if the *following* is not present in any entity,
                 that means the user is same who requested to get feed stars, else the 
                 *following* will have a boolean value.

- **get feed stars**
  - Path: /api/v1/feeds/stars/{user_email}
  - Method: **POST**
  - Required Data: id, key
  - Content-Type: application/json
  - Returns: List of users who gave stars to the post
  - Description: Gets all users who gave stars to the post.
                 *id* and *key* here are the feed id and key which needs to be sent 
                 with the request.
                 In the *user_following*, if the *following* is not present in any entity,
                 that means the user is same who requested to get feed stars, else the 
                 *following* will have a boolean value.

- **get community posts(feed)**
  - Path: /api/v1/communities/posts
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: Posts feeds in the community
  - Description: Gets the users feeds that are in the community of the logged in user.
                 Alongwith the results it also sends a *last_evaluated_key* parameter 
                 to get more results if all results are not fetched. If the response 
                 does not contain *last_evaluated_key*, it means all results have been 
                 fetched in the response.
                 The *user_id* is the *email* of the logged_in user.

- **get community challenges(feed)**
  - Path: /api/v1/communities/challenges
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: Challenges feeds in the community
  - Description: Gets the users post feeds that are in the community of the logged in user.
                 Alongwith the results it also sends a *last_evaluated_key* parameter 
                 to get more results if all results are not fetched. If the response 
                 does not contain *last_evaluated_key*, it means all results have been 
                 fetched in the response.
                 The *user_id* is the *email* of the logged_in user.

- **get following posts(feed)**
  - Path: /api/v1/users/following/posts
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: Posts feeds in the following.
  - Description: Returns all the posts of the followings. Alongwith the results it 
                 also sends a *last_evaluated_key* parameter to get more results if all 
                 results are not fetched. If the response does not contain *last_evaluated_key*, 
                 it means all results have been fetched in the response.
                 The *user_id* is the *email* of the logged_in user.

- **get following challenges(feed)**
  - Path: /api/v1/users/following/challenges
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: Challenges feeds in the following.
  - Description: Returns all the challenges of the followings. Alongwith the results it 
                 also sends a *last_evaluated_key* parameter to get more results if all 
                 results are not fetched. If the response does not contain *last_evaluated_key*, 
                 it means all results have been fetched in the response.
                 The *user_id* is the *email* of the logged_in user.

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

- **share feed with users**
  - Path: /api/v1/feeds/share/{feed}/{user_email}
  - Method: **PUT**
  - Required Data: id, key, shared_to
  - Data-types: - id: String
                - key: String
                - shared_to: Array of strings
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if the feed shared successfully
  - Description: Allows user to share with someone. {user_email} in the url 
                 is the email address for the user who is sharing the post.
                 Send the email address of the user in *shared_to* in data with whom 
                 the feed is being shared with.
                 {feed} in url is either *post* or *challenge*. Any other value would 
                 raise BadRequest Exception.



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
  - Path: /api/v1/reports/{feed}/{user_email}
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



### ORGANIZATION'S APIS
- **register organization**
  - Path: /api/v1/organizations/register
  - Method: **POST**
  - Required Data: - name: must be a unique name
                   - description: no more than 2 lines (client should handle this)
                   - type: either 'b-corp' or 'non-profit'
                   - global: *true* if global else *false*
                   - location: city, country
                   - admin_email
                   - password
  - Content-Type: multipart/form-data
  - Returns: *201 CREATED* Status Code if the organization succesfully created
  - Description: Registers organization on the application and adds it to the database.
                 The name of the organization should be unique.
                 There can be only two types of organizations: 'b-corp' or 'non-profit'.
                 'b-corp' is the social good type of organization.

- **organization login**
  - Path: /api/v1/organizations/login
  - Method: **POST**
  - Required Data: email, password
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if the login is successful
  - Description: Allows the admin to login into the organizations account.

- **uplift feed**
  - Path: /api/v1/organizations/uplift/
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id
  - Optional data: last_evaluated_key
  - Returns: List of all the organization in the category
  - Description: Gets organizations of type 'social_good' and/or 'non-profit'.
                 Alongwith the results it also sends a *last_evaluated_key* parameter 
                 to get more results if all results are not fetched. If the response 
                 does not contain *last_evaluated_key*, it means all results have been 
                 fetched in the response.
                 The *user_id* is the *email* of the logged_in user.

- **get organization details**
  - Path: /api/v1/organizations/uplift/feed
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id, organization_id
  - Returns: *200 OK* Status Code with a success message.
  - Description: Gets the details of the organizations.

- **give stars to organization on uplift**
  - Path: /api/v1/organizations/uplift/stars/share/{user_email}
  - Method: *POST*
  - Required Data: organization_name, stars
  - Content-Type: application/json
  - Returns: *200 OK* Status Code with a message and *400 Bad Request* if failed
  - Description: - Allows users to give stars to organizations on uplift.
                 - {user_email} is the the email for the user who is giving stars.

- **organizations's uplift billboard**
  - Path: /api/v1/organizations/billboard/uplift/{organization's_name}
  - Method: *GET*
  - Returns: Organization's details with a success message and *200 OK* Status Code
  - Description: Gets organization's details to create billboard.

- **organizations's feed billboard**
  - Path: /api/v1/organizations/billboard/feed/{organization's_name}
  - Method: *GET*
  - Returns: Organization's details with a success message and *200 OK* Status Code 
  - Description: Gets organization's details to create billboard.
                 - It also gets comments, likes and stars numbers.

- **organization's uplift stats**
  - Path: /api/v1/organizations/stats/uplift/{organization's_name}
  - Method: *GET*
  - Returns: All organization's stats based on stars in percentages
  - Description: Organization's stars is compared with the average 
                 of all the other organizations stars on uplift and the 
                 result is sent in percentages. Also, the stats of where the stars 
                 are coming from is shown in percentages for total 6 regions in US.

- **organization's feed stats**
  - Path: /api/v1/organizations/stats/feed/{organization's_name}
  - Method: *GET*
  - Returns: All organization's stats based on stars in percentages
  - Description: Organization's stars is compared with the average 
                 of all the other organizations stars on feed and the 
                 result is sent in percentages. Also, the stats of where the stars 
                 are coming from is shown in percentages for total 6 regions in US.

- **change organization's login password**
  - Path: /api/v1/organizations/setings/password/{organization}
  - Method: *POST*
  - Required Data: current_password, new_password
  - Returns: *200 OK* Status Code with a successful message if the password 
             changed successfuly.
  - Description: - Changes the organization's admin password. 
                 - {organization} in the url is the organization's name
                 - *current_password* and *new_password* are both required to 
                   change the admins login password.
                 - Results in failure if the *current_password* does not match.
  -IMPORTANT: Check if new_password and confirm_password matches on the front end 
              before sending the new password.



### Search Givel users API

- **search users**
  - Path: /api/v1/search/users/{user_email}
  - Method: **POST**
  - Required Data: search_for
  - Content-Type: application/json
  - Returns: *200 Ok* Status Code with a list of givel users if request is successful
  - Description: Searches for givel users. The {user_email} is the email for the user
                 who is searching for the user.


### API's not to be implemented by the client currently
- **edit organization's name**
  - Path: /api/v1/organizations/settings/name
  - Method: **PUT**  
  - Required Data: current_name, new_name
  - Content-Type: application/json
  - Returns: *200 OK* Status code and a message if the name changed successfully
  - Description: Changes the organization's name.

- **edit organization's details**
  - Path: /api/v1/organizations/settings/details
  - Method: **PUT**
  - Required Data: name
  - Data(to edit): - type: either 'b-corp' or 'non-profit'
                   - description:  no more than 2 lines (client should handle this)
                   - global: *true* if global else *false*
                   - location: city, country
  - Content-Type: application/json
  - Returns: *200 OK* Status Code if details successfully edited
  - Description: - Edits organization's details.
                 - *name* is organization's name which is required to start editing.

- **add/change organization's picture**
  - Path: /api/v1/organizations/settings/picture
  - Method: **PUT**
  - Required Data: name
  - File: picture
  - Content-Type: multipart/form-data
  - Returns: *200 OK* Status Code and a message if the picture changed successfully
  - Description: Changes organization's profile picture.



### Notifications API's

- **get user's all notifications**
  - Path: /api/v1/notifications/
  - Method: **POST**
  - Required Data: user_id
  - Optional Data: last_evaluated_key
  - Returns: List of user's notifications as results with a message and *200 OK* 
             if the request is successful.
  - Description: Gets all the users notifications. *user_id* is the email for 
                 the user who's is logged in. Alongwith the results it also sends a 
                 *last_evaluated_key* parameter to get more results if all results are 
                 not fetched. If the response does not contain *last_evaluated_key*, 
                 it means all results have been fetched in the response.
  - WHAT DOES EVERY NOTIFICATION CONTAIN:
    - checked: denotes that the notification is seen OR not seen by the user.
      - 2 possible boolean values: True OR False.
    - activity: says what is the notification about.
      - Possible values: 'like', 'share', 'shared' 'stars', 'comment', 
        'following', 'tagging'.
    - where: denotes where did the activity took place.
      - Possible values: 'post', 'challenge'.
    - tagged_where: the value denotes where the user was tagged.
                    The values could be either *post* OR *comment*
      - Possible values: 'post', 'comment'.
    - stars: represents how many stars where shared on the **activity**
    - comment: dictionary with keys *id* and *content*. *id* holds the comment_id as 
               its value and *content* holds the comment as its value.
    - notification: dictionary which holds the notification's *id* and *key*.
    - user: dictionary which holds user's *id*, *name* and *profile_picture*.
    - feed: dictionary which holds feed'd *id*, *type* and *content*.
    - creation_time: denotes when the notification was created.

  - **Note**: *checked*, *activity*, *creation_time*, *user* and *notification* occurs 
          always. All other keys occur according to the notification. Except the value 
          "following" for *activity*, for all the values there will be key *where*.
          Only the value *stars* for *activity* may or may not have key *where*. 
          When the *where* does not occur, the notification is always meant to be for the 
          user directly.
          There are two such notifications: 1) User started following you.
                                            2) User gave you stars for being awesome.

  ## HOW TO PUT THE NOTIFICATION:
    - If the value of the *activity* is "following", the notification would be 
      **"*user_name* started following you."**
    - If the value of the *activity* is "stars" and there does not exists key *where*, 
      the notification would be **"*user_name* gave you *stars* stars for being 
      awesome."**
    - If the value of the *activity* is "stars" and there does exists key *where*, 
      the notification would be **"*user_name* gave you *stars* stars for the *where* 
      *feed_content*"**.
    - If the value of the *activity* is "like", the notification would be **"*user_name* 
      liked your *where* *feed_content*"**.
    - If the value of the *activity* is "share", the notification would be **"*user_name* 
      shared your *where* *feed_content*"**.
    - If the value of the *activity* is "shared", the notification would be **"*user_name* 
      shared a *where* with you *feed_content*"**.
    - If the value of the *activity* is "comment", the notification would be **"*user_name* 
      commented on your *where* *feed_content*"**.
    - If the value of the *activity* is "tagging" and the value of *tagged_where* is "post", 
      the notification would be **"*user_name* tagged you in a *tagged_where* 
      *feed_content*"**.
    - If the value of the *activity* is "tagging" and the value of *tagged_where* is "comment", 
      the notification would be **"*user_name* tagged you in a *tagged_where* 
      *comment_content"**.

    - *Note:* If **feed_content** OR **comment_content** is an empty string, it means the 
            comment/post has been deleted.


- **change notification's status**
  - Path: /api/v1/notifications/{user_email}
  - Method: **PUT**
  - Content-Type: application/json
  - Required Data: - notifications: array of dictionaries of notification's id and key
                                    [{'id': 'notification_id', 'key': 'notification_key'}]
                   - checked: boolean
  - Returns: *200 OK* Status Code with a message if request is successful
  - Description: Changes the state of the notification to "seen" once the user taps and checks 
                 the notification. *id* and *key* are the notification's id and key which is 
                 required to for the request to be successful else it will raise a BadRequest 
                 exception. *checked* should be (true) bool value, if the notification is 
                 checked else do not call this api.

- **get notification's contents**
  - Path: /api/v1/notifications/{user_email}
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: feed_id, feed_type
  - Returns: *200 OK* Status Code with a success message if request is successful
  - Description: Gets the content of the notification.
  
- **get notification's screen dot to appear/disappear**
  - Path: /api/v1/notifications/activity/page/{user_email}
  - Method: **GET**
  - Returns: *200 OK* Status Code with a success message if request is successful
  - Description: Gets if the hamburger/Activity should have a dot. 
                 {user_email} is the email of the logged in user.
                 The response consists of *seen* parameter with a boolean value. If the 
                 value is *true*, the dot needs to disappear else the dot needs to appear.

- **remove notification dot*
  - Path: /api/v1/notifications/activity/page/{user_email}
  - Method: **PUT**
  - Content-Type: application/json
  - Required Data: seen
  - Returns: *200 OK* Status Code with a success message if request is successful
  - Description: Send the value as *true* (boolean) if the user checks the notifications 
                 screen. 
                 {user_email} is the email of the logged in user.


### Get User's Profile Page (Following, Followers, Badges, Activity)

- **get user's profile**
  - Path: /api/v1/profile/users/{user_email}
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: user_id
  - Returns: List of followings and followers and badges if the request is successful.
  - Description: Gets user's profile page with results consisting of the user's followers,
                 following and badges and activity(posts and challenges). {user_email} is 
                 the email of the user who is logged in to the application.
                 The *following* Key has a boolean value for the user_email following the 
                 user_id and the *following* Key in the following and followers list has a 
                 boolean value for the user_email following the user in the list.


### FAQ apis

- **ask a question**
  - Path: /api/v1/faqs/question/<user_email>
  - Method: **POST**
  - Content-Type: application/json
  - Required Data: question
  - Returns: *201 CREATED* Status Code with a message.
  - Description: Allows user to ask questions.

- **get FAQs**
  - Path: /api/v1/faqs/
  - Method: **GET**
  - Returns: All frequently asked questions and answers.
  - Description: Gets all questions that have been answered.


### Other

- **follow others**
  - Path: /api/v1/users/{user_email}/follow
  - Method: **GET**
  - Returns: *200 OK* Status Code and a success message with a list of users
  - Description: Returns a list of important Givel users to follow.