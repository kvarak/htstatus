OAuth Guide
Most data that your CHPP product will download from Hattrick is data that belongs to a specific user. The security and privacy of our users is very important to us, and we therefore want to let our users control which products can download their data. Furthermore, we want to avoid forcing our users to share their authentication credentials (such as their login name and password, or the security code previously used by CHPP) with the CHPP product.
For these reasons we have chosen to implement OAuth to authenticate requests from CHPP products.
What is OAuth?
OAuth is "an open protocol to allow secure API authorization in a simple and standard method from desktop and web applications" (http://oauth.net/). With this authentication scheme the users do not give a CHPP product their authentication credentials to let it log on for them, instead they authorize the CHPP product to access their data. OAuth is developed as an open web standard and is used by many large web sites, including Google, Yahoo, Twitter, flickr, Facebook and others. This means there is a large community, supported by all of these commercial interests, that have already implemented client libraries that an application can use to consume resources using OAuth. These libraries are available for most platforms and programming languages, and it of course continues to grow rapidly.
Description of the OAuth flow
A Hattrick user (called the Resource Owner in OAuth terminology) wants to use a CHPP product (called a Consumer in OAuth terminology). Since this is the first time the user uses this product he has not yet authorized it to access his data on Hattrick (the Service Provider in OAuth terminology).
The CHPP product starts the authorization flow by making a request to Hattrick to obtain a Request Token. Next, it directs the user to Hattrick to authorize the request token. The user logs in at Hattrick (the CHPP product never receives the login name or password) and is presented with the request for authorization of the CHPP product to access his data. After the user allows this Hattrick then directs the user back to the CHPP product. To complete the authorization flow the CHPP product makes another request to Hattrick to exchange the now authorized request token for an Access Token.
The CHPP product can now make requests to Hattrick using the access token to authenticate the user. The access token continues to work until the user revokes it, which he can do on Hattrick at any time or in the CHPP product itself. A desktop or mobile application (or other single user app) can connect automatically, and a multi user web site only need to match the current user to an access token.
Using OAuth at Hattrick
Hattrick implements OAuth Core 1.0a as specified in the standard, so if you use a client library that supports this it should work out of the box. You will need the following details to specify or configure the library to be able to use OAuth at Hattrick.
- ConsumerKey and ConsumerSecret: Can be found on the OAuth page for your product (in the menu on the right)
- Request Token path: https://chpp.hattrick.org/oauth/request_token.ashx
- Authorize path: https://chpp.hattrick.org/oauth/authorize.aspx
- Authenticate path: https://chpp.hattrick.org/oauth/authenticate.aspx
- Access Token path: https://chpp.hattrick.org/oauth/access_token.ashx
- Check Token path: https://chpp.hattrick.org/oauth/check_token.ashx
- Invalidate Token path: https://chpp.hattrick.org/oauth/invalidate_token.ashx
- Path to protected resources: All CHPP XML files are downloaded from https://chpp.hattrick.org/chppxml.ashx, specifying which file is requested using the parameter file=teamdetails (for example). See API Documentation for more info.
- Use GET method for all requests
- Use HMAC-SHA1 to sign all requests
- Always provide oauth_callback in the request to request_token.ashx. If your product cannot receive a callback, use oauth_callback=oob
Depending on the library you are using this overview might be enough information for you to use OAuth at Hattrick. We also have a visual description of the authorization flow, for those that are implementing OAuth themselves or just want to understand what is going on beneath the surface.
Asking for extended permissions
CHPP 2.0 allows CHPP products to not just read a user's data, there are also specific APIs for 'write commands'. These APIs are contained in specific named permission sets. Users must specifically allow a product to use each permission set with his account. To request access to a specific permission set the CHPP product should add a parameter called scope to the query parameters for the authorize URL that users are directed to. This parameter should contain a comma-separated list of the extended permissions that you are requesting the user to allow for your product.
Available scopes:
Manage challenges:	manage_challenges
Set matchorder:	set_matchorder
Manage youth players:	manage_youthplayers
Set training:	set_training
Place bid:	place_bid
For example, to ask for permission to manage challenges:
https://chpp.hattrick.org/oauth/authorize.aspx?oauth_token=XYZ&scope=manage_challenges
For example, to ask for permission to both manage challenges and set matchorder:
https://chpp.hattrick.org/oauth/authorize.aspx?oauth_token=XYZ&scope=manage_challenges,set_matchorder
Description of all available scopes
Resources to help with OAuth implementation
One of the hardest parts to get right with OAuth is signing requests. To help with this we have created an OAuth Signature Test page where you can enter all the details of the request you are making and see what the correct signature base string and signature should be.
We have also created a simple test client for making OAuth authenticated requests to the CHPP files.
OAuth Client Libraries
While you could sit down and implement the OAuth specification yourself, we strongly recommend using an existing client library. Depending on which library you choose, accessing Hattrick can be as simple as providing a url and some parameters to get an xml response. Lower level functionality such as web requests are abstracted away, although some libraries of course give you access to this as well. Note that Hattrick's provider implements OAuth Core 1.0a, whereas some older libraries are built for earlier versions.
On the community site for OAuth there is an extensive list of client libraries for most platforms and languages.
Finally, if you are developing your CHPP product using PHP as your programming language you can use the library PHT, by Hattrick user and CHPP developer CHPP-teles. With PHT you can make OAuth authenticated requests by simply specifying your consumer key and secret. It doesn't get much simpler than that!
