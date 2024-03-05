
You will be given computer code. Your task is to analyze it and look for code smells and signs of bad design. You will receive one or more files at once, and these files will likely be related (importing each other). The format of the input is as follows:

path/to/file/one.c:
    #include "two.h"

    void main(void) {
        hello("world");
    }

path/to/file/two.h:
    #include "stdio.h"

    void hello(const char* s) {
        printf("hello, %s\n", s);
    }

The first line of the file is always directly below the file path, without any blank lines inbetween. Every line of code is idented by additional 4 spaces (which are not in the original source file) to distinguish it from the rest of the input.

Your responses can should follow the format described here using EBNF.

    response = { detection, "\n" }, "@done"
    detection = file path, ",", location, ",", problem type, ",", severity, [ "," explanation ]
    location = { construct type, ":", identifier, "/" }, construct type, ":", identifier
    construct type = "function" | "variable" | "type"
    problem type = "bad_name" | "bad_comment" | "bad_documentation" | "duplicate_code" | "exposed_implementation_detail" | "unnecessarily_detailed_dependency" | "multiple_responsibilities" | "bad_subtype"
    severity = "1" | "2" | "3" | "4"

Here is the semantics of the nonterminals:

- response: this nonterminal corresponds to your entire response message; it consists of zero or more detection, each on its own line, and ends with the word "@done" on the last line
- detection: this nonterminal corresponds to a particular problem you found on a particular place the source code
- file path: this nonterminal is just the path to the file containing the issue - the path you've been given in the input 
- location: this nonterminal describes, where a problem is within a file; it uses the structure of the code to locate the problem. For example, value `variable:HELLO` would indicate the problem pertains to to a global variable (or a constant) named `HELLO`, value `function:main/variable:x` would indicate the problem pertains to a local variable `x` within the function `main`, value `type:Dog/function:woof` would mean the problem pertains to a method `woof` in the class `Dog`, and so on
- construct type: specifies the type of a programming language construct for navigating the source code and locating a problem. The values can be
    - "function": pertains to a function or a method
    - "variable": pertains to a local or global variable or constant
    - "type": pertains to a type (may be a class, an interface, etc.)
    - "top_level": pertains only to procedural top-level code (that is not inside any function)
- identifier: the name of a specific instance of a programming language construct, for example the name of a function, the name of a variable, or the name of a class. Can be empty if construct type is "top_level".
- problem type: identifies the actual type of the problem. The values can be
    - "bad_name": the name the referenced construct is not informative enough or is misleading.
    - "bad_comment": a comment in the body of the referenced construct is misleading, incorrect, or out of date
    - "bad_documentation": the description of the referenced construct is misleading, incorrect, or out of date
    - "duplicate_code": the codebase contains two pieces of code that do roughly the same thing and the referenced construct contains at least one of those pieces of code
    - "exposed_implementation_detail": the referenced construct exposes an implementation detail that doesn't need to be exposed and is only contributes to the emergence of undesirable coupling.
    - "unnecessarily_detailed_dependency": a violation of the Dependency Inversion Principle. The referenced construct references an unnecessarily concrete instance of another piece of code, creating undesirable coupling between the implementations.
    - "multiple_responsibilities": a violation of the Single Responsibility Principle. The referenced construct does more than one thing, i.e. has multiple possible reasons to change, i.e. its purpose cannot be easily explained with one sentence.
    - "bad_subtype": a violation of the Liskov Substitution Principle. The referenced construct - a type in this case - breaks the contract established by its supertype and therefore its supertype cannot be always safely substituted by it. This might entail introducing the possibility of breaking an invariant, breaking some post-conditions, or adding additional pre-conditions.
    - "unchecked_input": an unchecked input that is not validated nor addresed by some documentation comment can have values that may cause unexpected behavior.
- severity: specifies the severity of an issue. The values can be
    - "4": catastrophic - objectively bad design, indicative of a severe lack of experience or of serious negligence of the programmer. Needs to be fixed
    - "3": considerable - bad design, but could be made by more adept and responsible programmers too. Needs to be fixed
    - "2": medium - an issue that doesn't need to be fixed right now, but if left unattended, could slow down development in the future
    - "1": nitpick - a very nuanced issue, might not be worth the effort required to fix it
- explanation: explanation of the issue in plain English in no more than 30 words

ONLY report problems that you are certain of.

Examples: 

1. Input:
main.py

    def factorial(n: int) -> int:
        """computes the product"""
        if n == 0:
            return 1
        return factorial(n - 1) * n

    print(factorial(10))
    print(factorial(5))

1. Output:
main.py,function:main,unchecked_input,3,Calling the function with a negative number will result in infinite recursion.
main.py,function:main,bad_documentation,4,It is not specified which product is being computed.
@done

2. Input:
src/animals.py:
    class Rectangle:
        def __init__(self, width: float, height: float):
            self._width = width
            self._height = height

        def set_width(self, width: float):
            self._width = width

        def set_height(self, height: float):
            self._height = height

        def get_area(self):
            return self._width * self._height

    class Square(Rectangle):
        def __init__(self, width: float):
            super().__init__(width, width)
        
        def set_width(self, width: float):
            self._width = width
            self._height = width

        def set_height(self, height: float):
            self._width = height
            self._height = height

2. Output
src/animals.py,type:Square/function:set_width,bad_subtype,2,The set_width method maybe breaks a contract that the result of get_area would only change linearly when changing width.
src/animals.py,type:Square/function:set_height,bad_subtype,2,The set_height method maybe breaks a contract that the result of get_area would only change linearly when changing height.
@done
