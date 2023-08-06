
# Pirtul
[![MIT License](https://img.shields.io/github/last-commit/akimbo7/Pirtul?color=%237c2bff&style=flat-square)](https://github.com/akimbo7/Pirtul) 
![MIT License](https://img.shields.io/github/languages/code-size/akimbo7/Pirtul?color=%23602bff&style=flat-square)

![Logo](https://cdn.discordapp.com/attachments/935638977707376674/948301871469187182/unknown.png)
A simple API Wrapper for Norton Hill Portal.

For the most part, this lib doesn't hold much value. 
As the Portal is very restrictive in what it allows you to do, 
this lib is just a collection of different **GET** and **POST** requests which allows you to gather information of any given account.

*The Portal also has **shocking** security measures.*

Have fun :)

## Installation

```
pip install git+https://github.com/akimbo7/Pirtul.git#egg=pirtul
```
**Requirements**:

- requests
- bs4
- lxml
- colorama

## Example Usage

```python
import pirtul

client = pirtul.Portal()

username = '8SURNAME.FORNAME'
password = 'Password123'

#returns True or False
x = client.login(username, password)

numMerits = client.getMerits()
print(f'User has {numMerits} merits')
```


## Features
`Initializing your client`
```python
pirtul.Portal()
```

This initializes a client for Portal usage.

**Parameters**:
- Nothing yet
**Return**:
- A pirtul client

#
`Keep Alive`
```python
keepAlive()
```
![Logo](https://cdn.discordapp.com/attachments/935638977707376674/948310069144059924/Screenshot_2022-03-01_at_20.04.26.png)

This mimics the pop-up above. It's **not** needed but it's there if needed for whatever reason.

**Parameters**:
- None
**Returns**:
- Nothing lol

#
`Get Cookies`
```python
getCookies()
```

Gets all **available** cookies in the current session.

**Parameters**:
- None
**Returns**:
- The cookies of the current session

#
`Check Status`
```python
checkStatus()
```

Checks to see if the Portal is online.

**Parameters**:
- None

**Returns**:
- The current status code of the Portal

#
`Check Username Availability`
```python
checkUser(username)
```

Checks whether a username is registered in the Portal's database.

**Parameters**:
- Username
**Returns**:
- True - If the username **is** in the database
- False - If the username **is not** in the database

#
`Login`
```python
login(username, password)
```

Logs in with a given username and password.

**Parameters**:
- Username
- Password
**Returns**:
- True - If login was **successful**
- False - If login was **unsuccessful**

#
`Get full name`
```python
getName()
```

Get a users full name.

**Parameters**:
- None
**Returns**:
- The users full name

#
`Get users merits`
```python
getMerits()
```

Gets a users total amount of merits.

**Parameters**:
- None
**Returns**:
- The users amount of merits

#
`Get users minus points`
```python
getMinusPoint()
```

Gets a users total amount of minus points.

**Parameters**:
- None
**Returns**:
- The users amount of minus points

#
`Get users details`
```python
getPersonalDetails()
```

Gets a users complete list of personal details

**Parameters**:
- None
**Returns**:
- DOB
- Age
- Tutor
- Tutor group
- Address line 1
- Address line 2
- Address line 3
- Address line 4
- Address line 5
- Home phone number (Currently not working)
- Mobile phone number (Currently not working)
- Gender
- Full name

#
`Get users food balance` - Currently not working
```python
getFoodBalance()
```

Gets a users current food balance/ thumbprint balance.

**Parameters**:
- None
**Returns**:
- The users food balance

