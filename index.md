---
layout: default
title: 속초일보
---

<div class="hero-section">
  <h1>🚨 속보</h1>
  <div class="breaking-news">
    <marquee>최신 뉴스가 자동으로 업데이트됩니다 📰</marquee>
  </div>
</div>

<div class="weather-info">
  <span>🌤️ 속초 날씨: 23°C 맑음</span>
</div>

<main class="main-content">
  <section class="welcome-section">
    <h1>속초일보에 오신 것을 환영합니다</h1>
    <p>바다와 산이 만나는 도시 속초의 모든 소식을 정확하고 신속하게 전달합니다.</p>
    <p>시민 여러분과 함께 만들어가는 지역 언론사입니다.</p>
    <a href="/latest/" class="cta-button">최신 뉴스 보기 📰</a>
  </section>

  <section class="latest-news">
    <h2>🔥 주요 뉴스</h2>
    <div class="news-grid">
      {% for post in site.posts limit:6 %}
      <article class="news-card">
        {% if post.image %}
        <img src="{{ post.image }}" alt="{{ post.title }}" class="news-image">
        {% endif %}
        <div class="news-content">
          <span class="category {{ post.category | downcase }}">{{ post.category }}</span>
          <h3><a href="{{ post.url }}">{{ post.title }}</a></h3>
          <p>{{ post.excerpt | strip_html | truncate: 100 }}</p>
          <div class="news-meta">
            <span>📅 {{ post.date | date: "%Y.%m.%d" }}</span>
            <span>✍️ {{ post.author }}</span>
            <span>👁️ {{ post.views | default: 0 }}명 읽음</span>
          </div>
        </div>
      </article>
      {% endfor %}
    </div>
    <div class="more-news">
      <a href="/all-news/">더 많은 뉴스 보기 →</a>
    </div>
  </section>

  <section class="about-section">
    <h2>🌊 속초와 함께하는 속초일보 🏔️</h2>
    <div class="features-grid">
      <div class="feature">
        <h3>📰 정확한 보도</h3>
        <p>팩트 체크를 통한 정확하고 공정한 뉴스 전달</p>
      </div>
      <div class="feature">
        <h3>⚡ 신속한 전달</h3>
        <p>속초의 새로운 소식을 가장 빠르게 전해드립니다</p>
      </div>
      <div class="feature">
        <h3>🤝 시민과 함께</h3>
        <p>시민의 목소리를 듣고 함께 발전하는 언론사</p>
      </div>
      <div class="feature">
        <h3>🌐 디지털 혁신</h3>
        <p>AI 기술로 더 나은 뉴스 서비스 제공</p>
      </div>
    </div>
  </section>
</main> 