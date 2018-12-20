#Microsoft Graph service
[![Build Status](https://travis-ci.org/sesam-community/microsoft-graph.svg?branch=master)](https://travis-ci.org/sesam-community/microsoft-graph)

A small microservice to get microsoft graph api

##### GET example pipe config
```
[
    "_id": "sharepoint-list",
    "type": "pipe",
    "source": {
        "type": "json",
        "system": "microsoft-graph",
        "url": "/sites/[root]/lists/[listId]/items"
    }
]
```


##### Example result from GET method
```
  {
    "eTag": "\"15d01d76-5d8b-4469-b145-932a9aa4e6ff,3\"",
    "id": "91",
    "fields": {
      "@odata.etag": "\"15d01d76-5d8b-4469-b145-932a9aa4e6ff,3\"",
      "Title": "Foo",
      "LinkTitleNoMenu": "Foo",
      "LinkTitle": "foobar",
      "Modified": "2018-11-30T09:09:39Z",
      "Created": "2018-11-20T16:17:43Z",
      "ContentType": "Item",
      "LongName": "Foo Bar",
      "ScorecardType": "Delivery Center",
      "OwnerLookupId": "75"
    }
  }
```


##### Example configuration:

```
{
  "_id": "cvpartner",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "base_url": "https://graph.microsoft.com/v1.0/",
      "token_payload": "$SECRET(your_token_payload_secret)"
      "token_url": "https://[your_microsoft_login_site]/oauth2/token"  
    },
    "image": "sesamcommunity/microsoft-graph:latest",
    "port": 5000
  }
}
```

You can have multiple methods of authentication payloads.
```
{'grant_type':'client_credentials', 'resource':'https://graph.microsoft.com', 'scope': 'read.account', 'client_secret': 'foo', 'client_id': 'bar'}
or with username and password
{'grant_type':'password', 'resource': 'https://graph.microsoft.com', 'username' : 'username', 'password': 'password', 'client_secret': 'foo', , 'client_id': 'bar'}
```

