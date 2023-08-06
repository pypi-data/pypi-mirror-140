# ![sly logo](https://raw.githubusercontent.com/dunkyl/SlyMeta/main/sly%20logo.svg) Sly Gmail for Python

> 🚧 **This library is an early work in progress! Breaking changes may be frequent.**

> 🐍 For Python 3.10+

## No boilerplate, _async_ and _typed_ Gmail access. 😋

```shell
pip install slygmail
```

This library does not have full coverage.
Currently, the following topics are supported:

* Sending emails
* Sending emails with attachments

You can directly grant user tokens using the command line, covering the whole OAuth 2 grant process.

---

Example usage:

```python
import asyncio
from SlyGmail import *

async def main():
    gmail = Gmail('test/app.json', 'test/user.json', Scope.GmailSend)

    await gmail.send('person@example.com', 'test subject', 'test body')

asyncio.run(main())
```
