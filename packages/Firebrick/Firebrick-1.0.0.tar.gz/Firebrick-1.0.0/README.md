# Firebrick
 
### What is Firebrick?
Firebrick is a package with some general utilitys for django.


### How do I install Firebrick?
Via pip:
On Windows: `pip install firebrick`
On linux: `pip3 install firebrick`
In pipenv `pipenv install firebrick`

In `settings.py` add the following:

```
INSTALLED_APPS = [
    ...
    'firebrick',
    ...
]
```


### What sort of utilitys does Firebrick have?
- Auto generated accounts app
- Username validation settings
- Custom asserts for TestCase's
- Basic tests for views