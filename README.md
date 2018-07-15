# Swagger UI Updater


Swagger UI Updater is a simple python .

```sh
$ python3 main.py
```

Prerequisites:
----
  - `swagger-ui` key in _**package.json**_ that contains currently used Swagger UI version
  - `api-doc` key in _**package.json**_. directory relative path that `dist` directory contents will be moved to. **_Optional!_**
  - _**package.json**_ of course!

How It Works:
----
  - Reads `swagger-ui` key from _package.json_
  - Checks whether there are any updates
  - Downloads update tarball archive (with a progress bar!)
  - Extracts downloaded archive
  - Moves its `dist` directory contents to `api-doc` path
  - Removes unnecessary extracted files and downloaded archive
  - Update veresion of `swagger-ui` in _**package.json**_

License
----

MIT

**Free Software, Hell Yeah!**
