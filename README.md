# docker-render-template

This is a Docker container to render Jinja2 templates using JSON or XML file as
data source.

More than one data source file can be used.  They will be merged together.

Once the rendering of a template is done, the result is used as the template for
a another rendering pass.  As result, a template can generate Jinja2
instructions, which will be resolved by the next rendering pass.  when no change
occurs between two passes, processing is stopped and the final result is
outputted.

## Quick Start

Use the provided helper script:

```
curl -s https://raw.githubusercontent.com/jlesage/docker-render-template/master/render_template.sh | sh -s TEMPLATE TEMPLATE_DATA_SOURCE [TEMPLATE_DATA_SOURCE...]
```

Where:
  * `TEMPLATE` is the path to the Jinja2 template.
  * `TEMPLATE_DATA_SOURCE` is the path to the data source file (JSON or XML).
    More than one data source file can be specified.
