---
layout: page
title: Research
permalink: /research/
subtitle: Our research program focuses on health informatics, analytics, and AI for evidence-based health policy.
---

{% for section in site.data.research.sections %}
<h2>{{ section.title }}</h2>
{% if section.format == 'list' %}
<ul class="research-list">
  {% for item in section.items %}
  <li>
    {% if item.url %}
      <strong><a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title }}</a></strong>
    {% else %}
      <strong>{{ item.title }}</strong>
    {% endif %}
    {% if item.description %} — {{ item.description }}{% endif %}
  </li>
  {% endfor %}
</ul>
{% else %}
  {% for item in section.items %}
<h3>{{ item.title }}</h3>
<p>{{ item.description }}</p>
  {% endfor %}
{% endif %}
{% endfor %}

For publications related to these projects, see the [Publications]({{ '/publications/' | relative_url }}) page.
