{{ fullname }}
{{ underline }}

.. automodule:: {{ fullname }}

   {% block functions %}
   {% if functions %}
   Functions
   {{ '*' * 9 }}

   .. autosummary::
   {% for item in functions %}
      {{ item }}
   {%- endfor %}

   {% for item in functions %}

   {{ item }}
   {{ '+' * (item | length) }}

   .. currentmodule:: {{ fullname }}

   .. autofunction:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   Classes
   {{ '*' * 7 }}

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}

   {% for item in classes %}

   {{ item }}
   {{ '+' * (item | length) }}

   .. currentmodule:: {{ fullname }}

   .. autoclass:: {{ item }}
      :members:
   {%- endfor %}
   {% endif %}
   {% endblock %}
