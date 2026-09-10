---
layout: page
title: Team
permalink: /team/
subtitle: Meet the people behind HEAL Lab.
---

{% if site.data.lab.directors.size > 0 %}
<section class="leadership-section">
  <h2>Leadership</h2>
  <div class="directors-grid">
    {% for director in site.data.lab.directors %}
      {% include director-card.html director=director %}
    {% endfor %}
  </div>
</section>
{% endif %}

{% if site.data.team.collaborators.size > 0 %}
## Collaborators

<div class="team-grid">
{% for member in site.data.team.collaborators %}
  {% include team-member.html member=member %}
{% endfor %}
</div>
{% endif %}

{% if site.data.team.postdocs.size > 0 %}
## Postdoctoral Researchers

<div class="team-grid">
{% for member in site.data.team.postdocs %}
  {% include team-member.html member=member %}
{% endfor %}
</div>
{% endif %}

{% if site.data.team.phd_students.size > 0 %}
## PhD Students

<div class="team-grid">
{% for member in site.data.team.phd_students %}
  {% include team-member.html member=member %}
{% endfor %}
</div>
{% endif %}

{% if site.data.team.masters_students.size > 0 %}
## Master's Students

<div class="team-grid">
{% for member in site.data.team.masters_students %}
  {% include team-member.html member=member %}
{% endfor %}
</div>
{% endif %}

{% if site.data.team.visiting_scholars.size > 0 %}
## Visiting Scholars

<div class="team-grid">
{% for member in site.data.team.visiting_scholars %}
  {% include team-member.html member=member %}
{% endfor %}
</div>
{% endif %}
