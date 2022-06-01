========================
What is Implemented
========================

Overview
========================
The idea here is to document the knowns and unknowns with `pySym`. Generally
speaking, the basics of Python execution have mostly been implemented. By this
I mean, while loops, for loops, integers, arithmetic, bit operations, etc. I'll
focus mainly here on big picture structures.

Known Limitations
========================
* importing isn't implemented
* function scoping isn't implemented (meaning, if you declare a function inside another function, scope will be messed up)
* In some cases, call nesting with chaining doesn't work. Not sure exactly when this is, but for instance (test(test2()).rstrip("x")) i believe would fail.
* Case mixing is always a bit of a gamble (real/int/bitvec)

pyState functions
========================
* pyState.BVV(i,size=ast.Num(Z3_DEFAULT_BITVEC_SIZE))
    * Declares a BitVec Value of value "i" with optional BitVec size size
* pyState.BVS(size=ast.Num(Z3_DEFAULT_BITVEC_SIZE))
    * Declares a symbolic BitVec of max bits "size"
* pyState.Int()
    * Declares a symbolic Integer
* pyState.Real()
    * Declares a symbolic Real value
* pyState.String(length=ast.Num(Z3_MAX_STRING_LENGTH))
    * Declares a symbolic String value of length "length"

Example:

* If we want to declare a variable to be a Symbolic String of length 10, this would go in the python source code script that we're executing
    * s = pyState.String(10)
    * Note that you assign it like you would if you were executing it. Also, you do not need to from pySym import pyState to call this.


Python Built-in
========================
* abs (Fully Implemented)
* all (Not Implemented)
* any (Not Implemented)
* ascii (Not Implemented)
* bin (Partially Implemented)
* bool (Not Implemented)
* bytearray (Not implemented)
* bytes (Not Implemented)
* callable (Not Implemented)
* chr (Fully Implemented)
* classmethod (Not Implemented)
* compile (Not Implemented)
* complex (Not Implemented)
* delattr (Not Implemented)
* dict (Not Implemented)
* dir (Not Implemented)
* divmod (Not Implemented)
* enumerate (Not Implemented)
* eval (Not Implemented)
* exec (Not Implemented)
* filter (Not Implemented)
* float (Not Implemented)
* format (Not Implemented)
* frozenset (Not Implemented)
* getattr (Not Implemented)
* globals (Not Implemented)
* hasattr (Not Implemented)
* hash (Not Implemented)
* help (Not Implemented)
* hex (Partially Implemented)
* id (Not Implemented)
* input (Not Implemented)
* int (Partially Implemented)
* isinstance (Not Implemented)
* iter (Not Implemented)
* len (Fully Implemented)
* list (Not Implemented)
* locals (Not Implemented)
* map (Not Implemented)
* max (Not Implemented)
* memoryview (Not Implemented)
* min (Not Implemented)
* next (Not Implemented)
* object (Not Implemented)
* oct (Not Implemented)
* open (Not Implemented)
* ord (Fully Implemented)
* pow (Not Implemented)
* print (Partially Implemented)
* property (Not Implemented)
* range (Partially Implemented)
* repr (Not Implemented)
* reversed (Not Implemented)
* round (Not Implemented)
* set (Not Implemented)
* setattr (Not Implemented)
* slice (Not Implemented)
* sorted (Not Implemented)
* staticmethod (Not Implemented)
* str (Partially Implemented)
* sum (Not Implemented)
* super (Not Implemented)
* tuple (Not Implemented)
* type (Not Implemented)
* vars (Not Implemented)
* zip (Partially Implemented)
    * zip(list1,list2) works. 3 or more lists doesn't work at the moment
* __import__ (Not Implemented)


Numbers
========================
* Real/Int and implicit BitVecs are implemented

* Integer Methods
    * bit_length (Not Implemented)
    * conjugate (Not Implemented)
    * denominator (Not Implemented)
    * from_bytes (Not Implemented)
    * imag (Not Implemented)
    * numerator (Not Implemented)
    * real (Not Implemented)
    * to_bytes (Not Implemented)

* Float Methods
    * as_integer_ratio (Not Implemented)
    * conjugate (Not Implemented)
    * fromhex (Not Implemented)
    * hex (Not Implemented)
    * imag (Not Implemented)
    * is_integer (Not Implemented)
    * real (Not Implemented)

Strings
========================
* methods
    * capitalize (Not Implemented)
    * casefold (Not Implemented)
    * center (Not Implemented)
    * count (Not Implemented)
    * encode (Not Implemented)
    * endswith (Not Implemented)
    * epandtabs (Not Implemented)
    * find (Not Implemented)
    * format (Not Implemented)
    * format_map (Not Implemented)
    * index (Partially Implemented)
    * isalnum (Not Implemented)
    * isalpha (Not Implemented)
    * isdecimal (Not Implemented)
    * isdigit (Not Implemented)
    * isidentifier (Not Implemented)
    * islower (Not Implemented)
    * isnumeric (Not Implemented)
    * isprintable (Not Implemented)
    * isspace (Not Implemented)
    * istitle (Not Implemented)
    * isupper (Not Implemented)
    * join (Partially Implemented)
    * ljust (Not Implemented)
    * lower (Not Implemented)
    * lstrip (Not Implemented)
    * maketrans (Not Implemented)
    * partition (Not Implemented)
    * replace (Not Implemented)
    * rfind (Not Implemented)
    * rindex (Not Implemented)
    * rjust (Not Implemented)
    * rpartition (Not Implemented)
    * rsplit (Not Implemented)
    * rstrip (Fully Implemented)
    * split (Not Implemented)
    * splitlines (Not Implemented)
    * startswith (Not Implemented)
    * strip (Not Implemented)
    * swapcase (Not Implemented)
    * title (Not Implemented)
    * translate (Not Implemented)
    * upper (Not Implemented)
    * zfill (Partially Implemented)

Lists
========================
* methods
    * append (Fully Implemented)
    * clear (Fully Implemented)
    * copy (Not Implemented)
    * count (Not Implemented)
    * extend (Not Implemented)
    * index (Not Implemented)
    * insert (Partially Implemented -- No symbolic index)
    * pop (Not Implemented)
    * remove (Not Implemented)
    * reverse (Not Implemented)
    * sort (Not Implemented)

Python Common Libraries
========================
* random
   * randint (Partially Implemented)


Dictionaries
========================
Not implemented

Tuples
========================
Not Implemented

Files
========================
Not Implemented

Sets
========================
Not Implemented

Booleans
========================
Not Implemented

Bytes
========================
Not Implemented

ByteArray
========================
Not Implemented

Class
========================
Not Implemented

Functions
========================
Mostly implemented. Arbitrary function declaration. Keyword arguments, positional arguments, default arugments are implemented.

Some nested call limitations at the moment. If unsure if it'll work, just try it and let me know.

Symbolic Hooking
================
There often times is a need to hook symbolic execution. This is most often used
to flatten a group of statements into a single expression or otherwise change
the execution flow. See `hooking <hooking.html>`_ for more information.
