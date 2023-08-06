# file-type-indentifier

Library for identifying file type

## Examples

```
import asyncio

from fti import FileTypes, get_file_types, get_file_types_async


# sync
file_types = get_file_types("http://example.com/download_pdf")

FileTypes.PDF in file_types


# async
file_types = asyncio.run(
    get_file_types_async("http://example.com/download_pdf")
)

FileTypes.PDF in file_types
```