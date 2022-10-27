from typeguard import check_type
# global list of header names, used to check for collisions
global_header_names = []
def header(target, name):
    """
    The decorator wrapper function that sets the target and name for the
    decorator environment.
    """
    # make sure there are no name collisions
    if target+name in global_header_names:
        raise ValueError(f"header name collision: {target+name}")
    global_header_names.append(target+name)
    def make_header(func):
        """
        The inside decorator function that will get called on the decorated
        function.
        Returns a HeaderPrimitive object with the appropriate target, name, and
        typing_function.
        """
        # this is magic
        # purposefully confusing pylance so it will give up and
        # show the header with the signature of the original function
        # it is synonymous with `return HeaderPrimitive(target, name, func)`
        return [HeaderPrimitive(target, name, func),0][0]
    return make_header
class HeaderPrimitive():
    """
    The header class, which is used to type check and return formatted header
    tuples.
    This class is callable, and will type check the passed in keyword arguments
    and return a tuple of the target, the name, and the kwargs. This class
    should be created by decorating a type anotated function with the @header
    decorator. Any untyped variables will not be type checked.
    This class is also comparable to other header classes or to strings, and will
    be equal if the name field is equal, or if the name is equal to the string.
    This class is also hashable, so it may be used as a key in a dictionary.
    This class is immutable as well.
    This docstring will be replaced by the typing_function's docstring.
    """
    def __init__(self, target, name, typing_function):
        """
        The initializer for the HeaderPrimitive class. Copies the doc string from
        the typing function and sets the target, name, and typing function.
        """
        self.__doc__ = typing_function.__doc__
        self.target = target
        self.name = name
        self.typing_function = typing_function
    def __call__(self, *args, **kwargs):
        """
        The function that is called when an instance of HeaderPrimitive is called.
        Ensures that no positional args are passed in.
        Ensures that all the keyword args that are passed in are typed the same
        as the annotations.
        Calls the typing function on the keyword arguments to ensure that the
        function signature is satisfied and that the rules defined in the
        typing_function are followed.
        Returns a tuple of the target, the name, and the kwargs.
        """
        # check for positional args and raise an exception
        if len(args) > 0:
            raise TypeError(f"{self.typing_function.__name__}"
                + " requires keyword arguments, but positional arguments were given")
        # check the typing for each arg in kwargs against the annotation.
        annots = self.typing_function.__annotations__
        for arg, value in kwargs.items():
            # skips unannotated arguments, typechecks annotated arguments.
            # skips nonetype args, those will get handled later if they are an issue.
            if arg in annots and value is not None:
                check_type(f"{self.typing_function.__name__}({arg})", value, annots[arg])
        # call the typing_function and ignore any return value.
        # the typing_function must raise an error to have an effect.
        self.typing_function(**kwargs)
        # return a tuple of the target, the name, and the kwargs.
        return (self.target, self.name, kwargs)
    def __eq__(self, other):
        """
        Do not allow ==.
        """
        raise NotImplementedError
    def __hash__(self) -> int:
        """
        Do not allow hashing.
        """
        raise NotImplementedError
    def __str__(self):
        """
        Return the name for str().
        """
        return self.name
    def __setarr__(self, *_):
        """
        Do not allow assignment to members of this class in order to make it immutable
        """
        raise NotImplementedError
    def __delattr__(self, *_):
        """
        Do not allow deletion of members of this class in order to make it immutable
        """
        raise NotImplementedError
