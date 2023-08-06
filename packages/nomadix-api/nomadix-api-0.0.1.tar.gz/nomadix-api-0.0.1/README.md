
### Notes

#### TODO
- test some auth flows
- room administration api
- pypi pipeline
- check mac format, docs sugest all caps with no separation (i.e. CAFECAFECAFE)

#### XXX
- update_cache -> giving AAA internal error
- user_authorize not finding mac


### Reference Tables

Nomadix Error Numbers Description Table

┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error No. ┃ Error Description String                                                             ┃
┣━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃   100     ┃   Parsing error                                                                      ┃
┃   101     ┃   Unrecognized command                                                               ┃
┃   102     ┃   Required attribute is missing                                                      ┃
┃   103     ┃   Required data is missing                                                           ┃
┃   200     ┃   Unknown room number                                                                ┃
┃   201     ┃   Unknown user name                                                                  ┃
┃   202     ┃   Unknown user MAC address                                                           ┃
┃   203     ┃   Incorrect password                                                                 ┃
┃   204     ┃   User name already present                                                          ┃
┃   205     ┃   Too many subscribers                                                               ┃
┃   206     ┃   Unable to provide all requested data                                               ┃
┃   207     ┃   AAA internal error (when AAA is not configured correctly for the command request)  ┃
┃   301     ┃   User Radius Authorization Denied                                                   ┃
┃   303     ┃   Unsupported payment method                                                         ┃
┗━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Radius User Status table:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Status Message                 ┃        Description                                                                                                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ RADIUS_LOGIN                   ┃  Default Login Response if no match for other RADIUS_LOGIN messages, i.e. Access-Challenges will reproduce this message.  ┃
┃ RADIUS_LOGIN_ACCEPT            ┃  Login by XML or IWS (Internal Web Server) Login or HTML GET (SSL or non-SSL)                                             ┃
┃ RADIUS_LOGIN_REJECT            ┃  Login Reject                                                                                                             ┃
┃ RADIUS_LOGIN_ERROR             ┃  An error occurred.                                                                                                       ┃
┃ RADIUS_LOGIN_TIMEOUT           ┃  Login Timeout                                                                                                            ┃
┃ RADIUS_LOGOUT                  ┃  Default Logout Response if no match for other RADIUS_LOGOUT messages                                                     ┃
┃ RADIUS_LOGOUT_PORTAL_RESET     ┃  XML Logout                                                                                                               ┃
┃ RADIUS_LOGOUT_IDLE_TIMEOUT     ┃  Idle Timeout                                                                                                             ┃
┃ RADIUS_LOGOUT_SESSION_TIMEOUT  ┃  Session Timeout                                                                                                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
