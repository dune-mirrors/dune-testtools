{{ fullname }}
{{ underline }}

.. automodule:: {{ fullname }}

   {% block functions %}
   {% if functions %}
   Functions
   {{ '*' * (fullname | length) }}

   .. autosummary::
   {% for item in functions %}
      {{ item }}
   {%- endfor %}

   {% for item in functions %}
   {{ item }}
   {{ '+' * (fullname | length) }}

   .. currentmodule:: {{ fullname }}

   .. autofunction:: {{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   Classes
   {{ '*' * (fullname | length) }}

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}

   {% for item in classes %}
   {{ item }}
   {{ '+' * (fullname | length) }}

   .. currentmodule:: {{ fullname }}

   .. autoclass:: {{ item }}
      :members:

   {%- endfor %}

   {% endif %}
   {% endblock %}
