/*
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

*/
#ifndef INCLUDED_SHIM
#define INCLUDED_SHIM

#ifdef __cplusplus
#define DPI_LINK_DECL  extern "C" 
#else
#define DPI_LINK_DECL 
#endif

#include "svdpi.h"


DPI_LINK_DECL void
put(
    const char* path,
    const char* data_buf);

DPI_LINK_DECL void
sv_put(const char* data_buf);

DPI_LINK_DECL const char*
get(const char* path);

DPI_LINK_DECL const char*
sv_get();

DPI_LINK_DECL const char*
transport(
    const char* path,
    const char* data_buf);

DPI_LINK_DECL const char*
sv_transport(const char* data_buf);

#endif 
