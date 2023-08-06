def  datareader_doc():
    """ function to return the string 'My first Python package that anyone call install it! How cool!!!' """
    return("My first Python package that anyone can install it! How cool!!!")
def say_hello(name=None):
  if name is None:
    return "Hello, World!"
  else:
    return f"Hello, {name}!"
