
You will be given computer code. Your task is to analyze it and look for code smells and bad design. You will receive one or more files at once, and these files will likely be related (importing each other). The format of the input is as follows:

path/to/file/one.c:
1       #include "two.h"
2   
3       void main(void) {
4           hello("world");
5       }

path/to/file/two.h:
1       #include "stdio.h"
2   
3       void hello(const char* s) {
4           printf("hello, %s\n", s);
5       }

The first line of the file is always directly below the file path, without any blank lines inbetween. Every line of code is idented by 8 characters, which are not in the original source file. These characters are mostly whitespace, but the leftmost ones indicate the line number.

You will look ONLY for the following problems:

- bad_name
    - the name of a function, variable, class, method, etc., is not informative enough or misleading
    - you can suggest a better name
- bad_comment
    - a comment in the code is misleading or doesn't accurately reflect, what the code does
    - this doesn't apply to comments that are meant as documentation for functions, classes, etc. - for that, there is bad_documentation
    - you can suggest a better comment
- bad_documentation
    - a description of a function, variable, class, method, etc., is misleading or doesn't accurately reflect what it does
    - you can suggest a better text
- duplicate_code
    - there are two or more instances of code that does the same thing (i.e. if one were to change, the other would have to change to)
    - you can suggest a way to merge this duplicate code into a single constant, a variable, a function or a class
- exposed_implementation_detail
    - some implementation detail of a class is exposed, although it doesn't have to be for the class to serve its purpose, and this increases the risk of unnecessary coupling emerging
    - you can suggest changing the visibility of these details
- unnecessarily_detailed_dependency
    - a function or a class depends on another type with an unnecessary level of detail, violating the Dependency Inversion principle and creating unnecessary coupling - an abstraction should be used instead to reduce coupling
    - you may suggest a way to make the dependencies more abstract
- multiple_responsibilities
    - a function or a class serves more than one responsibility, violating the Single Responsibility Principle
    - you may suggest a way to split the function or class into multiple ones
- bad_subtype
    - a type defined in the inspected code doesn't adhere to the contract established by its supertype, violating the Liskov Substitution Principle
    - you may suggest an alternative way to organize the type hiearchy to fix this issue

ONLY report problems that you are certain of.

Each problem can appear zero or more times in the input. For each problem you detect, report it in this format

[file name]#[line number], [problem name]/[severity]: [suggestion]

When reporting multiple detections, don't put blank lines inbetween.

The severity is a number from 1 to 5. 1 means that it is just a nitpick, 5 means that a very serious violation of sensible coding principles has been presented to you.

The suggestion must be less than 20 words and contain no newline characters. If you are unsure about the suggestion, you don't have to suggest anything and use this format:

[file name]#[line number], [problem name]/[severity]

Notice that there is no colon after the line number. Examples:

src/mathUtils.js#121, bad_documentation/2: change the documentation comment to "adds two numbers together"
src/main.cpp#333, unnecessarily_detailed_dependency/2: replace the type "const std::ifstream&" of parameter "input" with "const std::istream&"
Program.cs#60, bad_subtype/3

The last line of your output should be "done". This would be the only line of your output if you find no issues with the code. Like this:

done
