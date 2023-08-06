<h1>JSON DB</h1>
<h3>Simple python local database</h3>

***Quick start:***

```python
from jsondb import Manager

manager = Manager("database.test")
data = manager.get()
if "nick" not in data: 
    data["nick"] = input("Enter your nickname: ")
    manager.save()
nick = data["nick"]
print("Hello, %s" % nick)
```

```
>>> Enter your nickname: ZoomDeveloper
Hello, ZoomDeveloper
```
```
Hello, ZoomDeveloper
```
