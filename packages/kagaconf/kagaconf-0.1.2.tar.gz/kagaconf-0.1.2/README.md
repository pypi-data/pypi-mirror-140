# kagaconf
Simple Python configuration loading interface I wrote for use in KAGAYAKI.
Actually most of this code was written during the development of gmsh, but I've finally found a nice name
to turn this into a standalone package.

# Usage
kagaconf provides a global configuration dictionary, which can be nested arbitrarily.
Adding items to this dictionary is easy:
```python
import kagaconf

# The simplest way to fill the dict is by copying another dict.
# I recommend this for default values.
kagaconf.from_dict({"key": "value"})

# Filling configuration from a file or all files in a directory is also very easy.
# There are many options for controlling this process, please refer to the API docs.
# Right now it only supports yaml, but adding at least json and toml should be trivial.
kagaconf.from_path('./path/to/your/config.yaml')
kagaconf.from_path('./path/to/your/config/directory', filter=r'[^_].*\.yaml', recursive=True)

# Lastly you can use a list of named variables to fill a skeleton dict with data.
# I imagine this will mainly be used to import environment variables into the config,
# that's why os.environ is the default data source (but you can obviously specify your own).
kagaconf.from_env_mapping({"this_key_will_be_filled": "BY_THIS_ENV_VARIABLE"})

# Found values are applied in order, so default values should go first
# and values with high precedence (e.g. environment overrides) last.
```

Once the configuration dict is prepared, it can easily be accessed from anywhere:
```python
from kagaconf import cfg

# Use normal python dot syntax to get to the key you want.
# Call it like a function to get the value behind it.
cfg.hello()

# This will throw a KeyError if the key has no value, unless you provide a default value.
# If no default was provided here, resolution would stop at "nonexistent".
cfg.nonexistent.key("this is fine")

# You can also use dict syntax to get subsequent elements.
# This can be freely mixed with the dot syntax.
cfg["this is cool"].and_even_required_for_using_number_indices[1234]\
    .but_also.you_can_do["something.like.this"]()
```

The paths you build are stored as `PathChainer` objects and can be completely arbitrary in structure.
They are only evaluated when you call them like a function, at which point a value will be resolved.
So you will never encounter a `KeyError` when building the path, only when resolving without a fallback value.

# Installation
You can install this library via `pip install kagaconf`. That is a sentence I never thought
I could write, but here we are.

# License
If you find this, think the API looks sweet and wanna use it, go ahead.
If you think the code magic I did to make this work seamlessly is cool, 1)
stop bc it's really not, and 2) feel free to use and abuse as much of it as you like.