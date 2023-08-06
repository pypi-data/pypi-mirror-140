# License
© 2022 Siemens.

 This material may only be used with products of Siemens Industry Software Inc.
 or its affiliates, and for no other purpose.

**License continued below**

# pyquesta module

**pyquesta* provides resources for Python programmers using Questa. The first
resource released is `SVconduit`

## SVConduit

The SystemVerilog Conduit system with the **SVConduit** module allows a Python
testbench writer to exchange an object with SystemVerilog.  This allows the
Python programmer to leverage Questa's advanced constraint-solver, and
functional coverage and the UCDB.

### SVconduit introduction

The first step to using SVConduit is to define a class using YAML. The system will generated
modules that define a Python version of the class and a SystemVerilog version of the class.

#### Define the communication class

For example, here is a transction class (`ALUCommand`) that sends instructions
to the TinyALU, which has two 8-bit legs and four operations.  

```YAML
ALUCommand:
  A:
   uchar
  B:
   uchar
  op:
   uchar
```


The `gen_svconduit_pkgs` program reads this YAML file and generates a Python module
and SystemVerilog package that define the class in those languages along with the 
serialization methods to pass it between Python and SystemVerilog.

#### Commuinate with SystemVerilog from Python

This snippet of test code creates a `cmd` using the SystemVerilog constraint-solver 
and writes the command into a SystemVerilog covergroup:

```python
from pyquesta import SVConduit
from ALUCommand import *

<snip>
    for _ in range(2):
        cmd = SVConduit.get(ALUCommand)  # get random command
        SVConduit.put(cmd)  # put in coverage
<snip>
```

`SVConduit.get()` class method knows where to get the object based on the
`ALUCommand` class passed to it. The `SVConduit.put()` class method knows where
to send the object based on its type.

#### Populate the SystemVerilog functions

The `ALUCommand.sv` file defines a package named `ALUCommand`.  This package
defines `sv_put()` and `sv_get()` which define the SystemVerilog behavior
associated with `ALUCommand` objects.

The `sv_get()` function uses the constraint solver to randomize an `ALUCommand` object
and return it to Python:

```SystemVerilog
function string sv_get();
    ALUCommand obj;
    string obj_str;
    obj = new();
    // Insert user to populate obj
    void'(obj.randomize() with {op inside {[1:4]};});
    // User code ends. You must have populated obj
    obj_str = obj.serialize();
    return obj_str;
endfunction
```
The `sv_put()` function gets a handle to a singleton containing a covergroup and samples the command:

```SystemVerilog
function void sv_put(ALUCommand_buf_t byte_buf);
    ALUCommand obj;
    obj = new(byte_buf);
    // Replace with user code for put function
    cov = Coverer::get();
    cov.A = obj.A;
    cov.B = obj.B;
    cov.op = obj.op;
    cov.op_cov.sample();
    // User code ends. You have used data from obj
endfunction
```

Now the Python code can get objects and send objects to the SystemVerilog package.

## Learn more about SVConduit

You can get a copy of the example used in this `README.md` file as well as read a tutorial
and documentation about SVConduit at the [Verification Academy](www.verificationacademy.com). 

# Full license
© 2022 Siemens.

 This material may only be used with products of Siemens Industry Software Inc.
 or its affiliates, and for no other purpose.

If you have a signed license agreement with Siemens for the product with which
this Software will be used, your use of this Software is subject to the scope of
license and the software protection and security provisions of that agreement.
If you do not have such a signed license agreement, your use is subject to the
Siemens Universal Customer Agreement, which may be viewed at
https://www.sw.siemens.com/en-US/sw-terms/base/uca/, as supplemented by the
electronic design automation (EDA) specific terms which may be viewed at
https://www.sw.siemens.com/en-US/sw-terms/supplements/.

NOTWITHSTANDING ANYTHING TO THE CONTRARY IN YOUR SIGNED LICENSE AGREMENT WITH
SISW OR THE SISW END USER LICENSE AGREEMENT, THIS SOFTWARE IS BEING PROVIDED “AS
IS;” SISW MAKES NO WARRANTY OF ANY KIND WITH REGARD TO THIS SOFTWARE INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF INTELLECTUAL PROPERTY. SISW SHALL
NOT BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, CONSEQUENTIAL OR PUNITIVE
DAMAGES, LOST DATA OR PROFITS, EVEN IF SUCH DAMAGES WERE FORESEEABLE, ARISING
OUT OF OR RELATED TO THIS SOFTWARE OR THE INFORMATION CONTAINED IN IT, EVEN IF
SISW HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

Unless agreed in writing, SISW has no obligation to support or otherwise
maintain this Software.



