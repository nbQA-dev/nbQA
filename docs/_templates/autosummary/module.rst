{% block module %}
{{ fullname | replace("nbqa.", "") | escape | underline}}
{#{% set reduced_name={child_modules} %}#}

.. currentmodule:: {{ module }}

.. automodule:: {{ fullname }}
   :members:
   :private-members:
   :special-members:

{% endblock %}
