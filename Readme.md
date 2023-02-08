# Convert XLIFF to ttag JSON (compact format)

Based on https://ttag.js.org/ 


## requirements

- python 3.x (3.9 _during this dev_)
- `lxml`
- `pipenv` _optional_

## CLI

```sh
usage: convert.py [-h] --input INPUT --output OUTPUT --locale LOCALE

convert xliff to ttag JSON (compact)

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    input xliff file
  --output OUTPUT  output JSON file
  --locale LOCALE  locale from crowdin you're using
```

ex: `$ python convert.py --input demo/webapp.xliff --output monique.json --locale fr`

> for `[--locale]` you can open the file `lib/config/gettext-plurals.json` to see all the options you have
