
__author__ = "aqur1n" # Author name
__github__ = r"https://github.com/aqur1n-lab/aqur1n-tools" # GitHub link
__version__ = "2022.2.25" # Versin (YYYY.mm.dd) A - alpha B - beta
__modules__ = __all__ = (
    "sqlite3",
    "basic",
    "path",
    "cache",
    "cfg"
 ) # All modules in library

if __name__ == "__main__":
    print(
    """
                              {0}
        aqur1n-tools - Collection of modules for convenient work.

    Please use "from atools.<module> import *" or "from atools import <module>"
                    rather than "import atools".

                            MIT License
                    Copyright (c) 2022 aqur1n-lab
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.   
    """.format(__version__)
    )
