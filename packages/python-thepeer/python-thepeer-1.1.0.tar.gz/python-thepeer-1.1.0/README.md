# ThePeer Python Sdk
python SDK for ThePeer payment infrastructure


# Reference Official Documentation
https://docs.thepeer.co/

# Instantiate ThePeer api object
```python
from ThePeer.client import Client

client = Client(api_key="YOUR PRIVATE KEY")

"""
returns all indexed users for your business
"""
client.get_users()


"""
Index/create users
data = {"name" : "", "identifier" : "", "email" : ""} 
"""
client.create_user(data=data)


"""
Update indexed user
the method requires two arguments, the user's ReferenceId and the user's new identifier
referenceId = ""
data = {"identifier" : ""}
"""
client.update_user(referenceId, data=data)


"""
Delete indexed user
this methods allows you to delete an indexed user on your business profile
referenceId = ""
"""
client.delete_user(referenceId)

# Transactions

"""
returns all the details of a particuar transaction
transactionId = ""
"""
client.get_transaction(transactionId)


"""
This method refunds a specific transaction back to its origin (business & user of that business)
it requires two arguments by default transactionId and refund details, alternatively, you can
pass in only the transactionId and we'd use the default refund data i.e data = {"reason": "possible fraud"}
"""
client.refund_transaction(transactionId)


"""
This returns all linked accounts associated with a user, It returns the user's account details along with he business the account resides on.
pass in the linkId to identify and get user's links
"""
client.get_user_links(linkId)


"""
Similarly the method returns a linked account details by passing its ID.
"""
client.get_user_link(linkId)


"""
This method enables you to charge your user's linked account
where data = {
    "amount": ,
    "remark": ""
}
"""
client.charge(linkId, data)


"""
This method allows you simulate receiving money

data = {
  "amount": ,
  "currency": "",
  "user_reference": ""
}

"""

```
