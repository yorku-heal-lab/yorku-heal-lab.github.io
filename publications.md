---
layout: page
title: Publications
permalink: /publications/
subtitle: Selected publications from HEAL Lab members.
---

<div class="publication-list">
{% for pub in site.data.publications %}
  {% include publication-item.html pub=pub %}
{% endfor %}
</div>
