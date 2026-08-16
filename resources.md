---
layout: page
title: Resources
permalink: /resources/
subtitle: Open-source software, datasets, and other resources from HEAL Lab.
---

{% for section in site.data.resources.sections %}
<section class="resource-section">
  <h2>{{ section.title }}</h2>
  <div class="resource-list">
  {% for item in section.items %}
    {% include resource-item.html item=item %}
  {% endfor %}
  </div>
</section>
{% endfor %}
