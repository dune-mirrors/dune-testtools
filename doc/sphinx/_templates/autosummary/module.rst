{{ fullname }}
{{ underline }}

.. automodule:: {{ fullname }}

   {% block functions %}
   {% if functions %}
   .. rubric:: Functions

   .. autosummary::
   {% for item in functions %}
      {{ item }}
   {%- endfor %}

   {% for item in functions %}
   {{ item }}
   {{ '*' * (fullname | length) }}

   .. currentmodule:: {{ fullname }}

   .. autofunction:: {{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: Classes

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}

   {% for item in classes %}
   {{ item }}
   {{ '*' * (fullname | length) }}

   .. currentmodule:: {{ fullname }}

   .. autoclass:: {{ item }}
      :members:

   {%- endfor %}

   {% endif %}
   {% endblock %}
