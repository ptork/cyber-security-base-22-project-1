# cyber-security-base-22 project-1

Source: <https://github.com/ptork/cyber-security-base-22-project-1>

## Installation

Initialize db

```sh
python manage.py migrate
python manage.py createsuperuser
```

Run development server

```sh
python manage.py runserver
```

## FLAW 1: OWASP vulnerability: A01:2021 – Broken Access Control

Source: <https://github.com/ptork/cyber-security-base-22-project-1/blob/master/profiles/views.py#L6>

### Before running

Use the admin view to create a new user and add a profile with address details for it.

<http://127.0.0.1:8000/admin/>

### Description

In the app we have a `/profile` route. It shows the profile of a user, including sensitive information such as their address.

The route takes 1 route parameter, which is the user id. So to see the profile of user 1, the url would be `/profile/1` and for user 2 `/profile/2` etc. It uses the `@login_required` decorator. Which means you have to be logged in to access this page.

The code however does not check whether the user requesting the page has the same user id as in the path parameter. Meaning users are able to change the parameter and see potentially private information of other users.

Furthermore it exposes the database id of the user. Even if the route was properly secured to allow logged in users to view their own profile. It leaks information about the database scheme used. An attacker would know based on this value how many users are in the database at least. And which numbers might be valid.

### How to fix

The first thing to address is to check whether the user requested has the same id as the logged in user. And to return a `404` if it's not the same. This ensures users are only able to request their own profile.

```python
if request.user.id == profile_id:
  profile = Profile.objects.get(pk=profile_id)
  return render(request, 'index.html', {'profile': profile })

return HttpResponseNotFound("hello")
```

However it still leaks information about the database; it tells the user what their database id is. We can avoid this by removing the path parameter altogether and to use the logged in users id directly. The route becomes `/profile` instead of `/profile/{id}`.

```python
profile = Profile.objects.get(pk=request.user.id)
return render(request, 'index.html', {'profile': profile })
```

## Flaw 2: A02:2021 – Cryptographic Failures

### Description

Source: <https://github.com/ptork/cyber-security-base-22-project-1/blob/master/project1/settings.py#L46>

In Django you can set the password hashing algorithm to be used when storing passwords in the database.

Here I've set it to use a salted MD5 hasher. MD5 is unsuitable for passwords because it's easy to crack on consumer, and even with a salted version it's fairly easy to retrieve the plain text.

For instance, using this hashing algorithm and using the password "admin" for the superuser, I got the following value in the database:

```
md5$Vwz3PvV4c9rJ8S9p1bWN4R$610dc97c7bc1ad92ee073d1ac61d80a1
```

The format is `{type}${salt}$password`.

I was able to crack the password using a list of 10 million common passwords in a few hours at 25 hashes per second. Using a GPU would increase this speed immensely:

```sh
hashcat -a 3 -m 20 610dc97c7bc1ad92ee073d1ac61d80a1:Vwz3PvV4c9rJ8S9p1bWN4R ~/downloads/10-million-password-list-top-1000000.txt
```

### How to fix

Always use secure hashing algorithms. The most recommended hashing algorithm changes every so often. So it's good to look this up regularily.

The last hashing algorithm to win the competition is `argon2`. However the default Django hasher (`pbkdf2`) is good too.

```sh
python -m pip install django[argon2]
```

```python
PASSWORD_HASHERS = [
  'django.contrib.auth.hashers.Argon2PasswordHasher',
]
```

#### Problem 2 - Get secret key from environment

## Before running

Use the admin view to create a new user and add an order belonging to that user.

<http://127.0.0.1:8000/admin/>

## Flaw 3: A03:2021 – Injection

Source: <https://github.com/ptork/cyber-security-base-22-project-1/blob/master/orders/views.py#L6>

### Description

This function is vulnerable to SQL injection. It builds a raw SQL string, inserting user input directly into the string.

A well crafted SQL statement can exploit this weakness. In this case we're able to get all the orders in the database by visiting the following page:

```sh
http://127.0.0.1:8000/orders/?status=open' OR '1'='1

# uri encoded

http://127.0.0.1:8000/orders/?status=open%27%20OR%20%271%27=%271
```

### How to fix

Always use parameterized queries when you're building raw SQL. In this case it would look like this:

```python
sql = "SELECT * FROM orders_order WHERE user_id = %s"

orders = []

if request.GET.get('status'):
  sql += " AND status = '%s'"
  orders = Order.objects.raw(sql, [request.user.id, request.GET.get('status')])
else:
  orders = Order.objects.raw(sql, [request.user.id, request.GET.get('status')])

orders = Order.objects.raw(sql)
```

Or better yet, don't use raw SQL at all:

```python
orders = Order.objects.filter(user=user)

if request.GET.get('status')
  orders = orders.filter(status=request.GET.get('status'))
```

## Flaw 4: A05:2021 – Security Misconfiguration

Source: <https://github.com/ptork/cyber-security-base-22-project-1/blob/master/project1/settings.py#L19>

### Description

Django uses a secret key to when performing cryptographic functions. For instance when signing a cookie.

A new Django installation will generate one. However it's unsafe to rely on the Django generation method. And it should not be included in source control.

Right above the key there is a big warning, including a link to the Django documentation describing how to mitigate this threat.

There is also a `DEBUG` variable set to true. This will show stacktraces. Deploying a standard Django project to production will reveal these stacktraces to anyone.

### How to fix

As described in the docs, the best way is to receive the secret key as environment variable.

```python
import os

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ['DEBUG']
```

## Flaw 5: A09:2021 – Security Logging and Monitoring Failures

Source: <https://github.com/ptork/cyber-security-base-22-project-1/blob/master/project1/logger.py#L7>

### Description

A common flaw is to log too much information. For instance often you want to log every request that comes in. In these cases it can be very useful to capcure headers so you can see what's going wrong during a request.

However logging too much can lead to vulnerbilities. In my example I'm logging the session cookie. If someone has access to where the logs are stashed, they can look up session ids and hijack a users session.

### How to fix

To fix this, only log things that not sensitive. Or provide multiple profiles for developers so they can still see all the headers during development. But are ommitted in production.

A way to fix this vulnerability is to not log cookies at all:

```python
def without(d, key):
    new_d = d.copy()
    new_d.pop(key)
    return new_d

def __call__(self, request):
  print(self.without(request.headers, 'cookies'))
  return self.get_response(request)
```
