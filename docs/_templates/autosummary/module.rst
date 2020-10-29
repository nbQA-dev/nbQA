{% block module %}
{{ name  | escape | underline}}

.. currentmodule:: {{ module }}

.. automodule:: {{ fullname }}


   {% block modules %}
   {% if modules %}

   .. rubric:: Modules

   .. autosummary::
      :toctree: {{ name }}
      :recursive:

      {% for item in modules %}
         {{ item }}
      {%- endfor %}

   {% endif %}

   {% endblock %}


   {% block attributes %}
   {% if attributes %}
   .. rubric:: Module Attributes

   .. autosummary::
         :toctree: {{ name }}

         {% for item in attributes %}
            {{ item }}
         {%- endfor %}

   {% endif %}

   {% endblock %}

{% block functions %}
   {% if functions %}


   .. rubric:: Functions

   .. autosummary::
         :toctree: {{ name }}/functions
         :nosignatures:

         {% for item in functions %}
         {{ item }}
         {%- endfor %}

   {% endif %}

{% endblock %}

{% block classes %}
   {% if classes %}

   .. rubric:: Classes

   .. autosummary::
         :toctree: {{ name }}/classes
         :nosignatures:

         {% for item in classes %}
         {{ item }}
         {%- endfor %}

   {% endif %}

{% endblock %}


{% block exceptions %}
   {% if exceptions %}


   .. rubric:: Exceptions

   .. autosummary::
         :toctree: {{ name }}/exceptions
         :nosignatures:

         {% for item in exceptions %}
            {{ item }}
         {%- endfor %}

   {% endif %}

{% endblock %}


{% endblock %}
