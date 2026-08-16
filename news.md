---
layout: page
title: News
permalink: /news/
subtitle: Announcements and updates from HEAL Lab.
---

<div class="news-list news-list--full">
{% for item in site.data.news %}
  {% include news-item.html item=item %}
{% endfor %}
</div>
