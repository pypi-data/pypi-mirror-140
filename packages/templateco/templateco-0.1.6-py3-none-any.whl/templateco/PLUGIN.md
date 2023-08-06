# Templateco plugin documentation
If you're wanting to write a plugin for Templateco, this is the documentation for you.

## Bootstrap a new plugin
You can bootstrap a new Templateco plugin using Templateco itself.
```shell
pip install templateco templateco-cli templateco-plugin-plugin
templateco make templateco namespace_name_plugin
```
The folder of the plugin must match the format `(namespace)_(name)_plugin`.

## Python
Your Python package must export the following:

| Name                                        | Type      | Required | Minimum version | Example           | Description                                                                          |
|---------------------------------------------|-----------|----------|-----------------|-------------------|--------------------------------------------------------------------------------------|
| friendly_name                               | string    | yes      | 1.0.0           | My Python project | A friendly name used to identify your plugin in a list.                              |
| compatible_languages                        | list[str] | yes      | 1.0.0           | ["python"]        | List of languages that can be specified to invoke this plugin.                       |
| selected_by_default                         | boolean   | no       | 1.0.0           | False             | If the plugin appears in a list, should it be pre-selected.                          |
| [get_questions](#get_questions)             | function  | yes      | 1.0.0           |                   | A function that returns a list of questions for Questionary.                         |
| [folders_to_template](#folders_to_template) | function  | yes      | 1.0.0           |                   | A function that returns a list of strings for the folders to be used for templating. |
| [pre_template_hook](#pre_template_hook)     | function  | no       | 1.0.0           |                   | A function invoked before templating.                                                |
| [post_template_hook](#post_template_hook)   | function  | no       | 1.0.0           |                   | A function invoked after templating.                                                 |

### Functions
All arguments are passed exclusively as keywords, with the remaining discarded using
`**_: Any`. This ensures compatibility between releases, you just need to ensure that
the minimum version of Templateco specified matches the minimum version of the arguments
you're consuming.

**We do not guarantee compatibility between major releases.**



#### get_questions
This function is invoked by Templateco and returns a Questionary dictionary-type
iterable.

For more information:
https://questionary.readthedocs.io/en/1.10.0/pages/advanced.html#create-questions-from-dictionaries

##### Example
```python
@get_questions_decorator
def get_questions(**_: Any) -> Questions:
    return []
```

##### Keyword Arguments
| Name     | Type            | Type Alias | Minimum version | Description                               |
|----------|-----------------|------------|-----------------|-------------------------------------------|
| language | str             |            | 1.0.0           | Name of the requested language.           |
| folder   | str             |            | 1.0.0           | Name of the top-level folder.             |
| config   | Dict[str, Any]  | Config     | 1.0.0           | Extra configuration passed to Templateco. |
| plugins  | Tuple[str, ...] | Plugins    | 1.0.0           | Tuple containing all selected plugins.    |

#### folders_to_template
Templateco can conditionally template folders & files based upon the values returned
here.

##### Example
```python
@folders_to_template_decorator
def folders_to_template(**_: Any) -> Folders:
    return ["template"]
```

##### Keyword Arguments
| Name     | Type            | Type Alias | Minimum version | Description                                   |
|----------|-----------------|------------|-----------------|-----------------------------------------------|
| language | str             |            | 1.0.0           | Name of the requested language.               |
| folder   | str             |            | 1.0.0           | Name of the top-level folder.                 |
| config   | Dict[str, Any]  | Config     | 1.0.0           | Extra configuration passed to Templateco.     |
| answers  | Dict[str, Any]  | Answers    | 1.0.0           | Dictionary of answers from the questionnaire. |
| plugins  | Tuple[str, ...] | Plugins    | 1.0.0           | Tuple containing all selected plugins.        |

#### pre_template_hook
This function is invoked after the questions have been asked, but before Templateco
templates the files. It's useful for mutating the data into a format that's more easily
palatable by Jinja2, or injecting/cleaning up data.

##### Example
```python
@pre_template_hook_decorator
def pre_template_hook(**_: Any) -> None:
    pass
```

##### Keyword Arguments
| Name     | Type            | Type Alias | Minimum version | Description                                   |
|----------|-----------------|------------|-----------------|-----------------------------------------------|
| language | str             |            | 1.0.0           | Name of the requested language.               |
| folder   | str             |            | 1.0.0           | Name of the top-level folder.                 |
| config   | Dict[str, Any]  | Config     | 1.0.0           | Extra configuration passed to Templateco.     |
| answers  | Dict[str, Any]  | Answers    | 1.0.0           | Dictionary of answers from the questionnaire. |
| plugins  | Tuple[str, ...] | Plugins    | 1.0.0           | Tuple containing all selected plugins.        |

#### post_template_hook
This function is called after all of the physical files have been written, and is useful
for invoking commands e.g. `terraform fmt`.

##### Example
```python
@post_template_hook_decorator
def post_template_hook(**_: Any) -> None:
    pass
```

##### Keyword Arguments
| Name          | Type            | Type Alias | Minimum version | Description                                   |
|---------------|-----------------|------------|-----------------|-----------------------------------------------|
| language      | str             |            | 1.0.0           | Name of the requested language.               |
| folder        | str             |            | 1.0.0           | Name of the top-level folder.                 |
| output_folder | Path            |            | 1.0.0           | Path to the generated folder.                 |
| config        | Dict[str, Any]  | Config     | 1.0.0           | Extra configuration passed to Templateco.     |
| answers       | Dict[str, Any]  | Answers    | 1.0.0           | Dictionary of answers from the questionnaire. |
| plugins       | Tuple[str, ...] | Plugins    | 1.0.0           | Tuple containing all selected plugins.        |

## Questionary
Templateco uses Questionary under the hood to power user interactions. It takes data in
the dictionary form, and returns a dictionary of answers e.g.
```python
# Questions asked to Templateco.
questions = [
    {
        "type": 'text',
        "name": 'name',
        "message": "What is your name?",
    }
]

# Data argument in pre/post template hooks:
data = {
    "name": "my name"
}
```

## Jinja2
The templating side of Templateco is handled by Jinja2. If a variable is unspecified,
Templateco will halt the entire plugin rather than substitute it with a different value.

You can template files names too, so it's possible to have a folder structure like:
```
template
 > {% if foo %}foo{% else %}bar{% endif %}
   > my_file.jinja2
```

All filenames must end in .jinja2 otherwise they will be ignored by Templateco.

You can generate multiple files by using a `;` e.g.
```
template
  > {% for foo in bar %}
    > {{ foo }}_file.jinja2;{% endfor %}
```
which will generate a series of files in the list `bar`.

### Variables passed to Templateco
#### By the user
All answers are passed to Jinja2 as top-level variables e.g.
```python
questions = [
    {
        "type": 'text',
        "name": 'name',
        "message": "What is your name?",
    }
]

# Accessed in Jinja2 template:
# Hi there {{ name }}!
```

#### By Templateco
Templateco passes some runtime configuration to the template as `_metadata`, and can be
accessed with `{{ _metadata.value }}` (substituting as appropriate below).

#####
| Name          | Type       | Minimum version | Example          | Description                                                          |
|---------------|------------|-----------------|------------------|----------------------------------------------------------------------|
| file_path     | string     | 1.0.0           | foo/bar/bazz.yml | Name of the file about to be written, fully templated by Templateco. |
