{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

{% if objtype == 'class' %}
.. auto{{ objtype }}:: {{ objname }}
   :members:
{% else %}
.. auto{{ objtype }}:: {{ objname }}
{% endif %}

.. include_examples:: {{ objname }}.ipynb
