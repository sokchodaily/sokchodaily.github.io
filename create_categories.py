#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
속초일보 카테고리 페이지 자동 생성 스크립트
전문적인 뉴스 사이트 레이아웃 구현
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

# 카테고리 정의
CATEGORIES = {
    'breaking': {
        'title': '속보',
        'icon': '🚨',
        'description': '속초의 긴급하고 중요한 소식',
        'color': '#dc2626'
    },
    'politics': {
        'title': '정치',
        'icon': '🏛️',
        'description': '속초시정과 지방정치',
        'color': '#1e40af'
    },
    'economy': {
        'title': '경제',
        'icon': '💼',
        'description': '속초 지역 경제와 산업',
        'color': '#059669'
    },
    'society': {
        'title': '사회',
        'icon': '🏘️',
        'description': '속초 시민 생활과 사회',
        'color': '#7c3aed'
    },
    'culture': {
        'title': '문화',
        'icon': '🎭',
        'description': '속초 문화예술과 축제',
        'color': '#db2777'
    },
    'tourism': {
        'title': '관광',
        'icon': '🌊',
        'description': '속초 관광과 여행정보',
        'color': '#0891b2'
    },
    'sports': {
        'title': '스포츠',
        'icon': '⚽',
        'description': '속초 지역 스포츠',
        'color': '#ea580c'
    }
}

def create_category_layout():
    """전문적인 뉴스 사이트 스타일의 카테고리 레이아웃 생성"""
    layout_dir = Path('_layouts')
    layout_dir.mkdir(exist_ok=True)
    
    layout_content = '''---
layout: default
---

<div class="category-page">
    <!-- 카테고리 헤더 -->
    <div class="category-header">
        <div class="container">
            <div class="category-nav">
                <a href="{{ '/' | relative_url }}" class="home-link">홈</a>
                <span class="nav-separator">></span>
                <span class="current-category">{{ page.title }}</span>
            </div>
            <h1 class="category-title">
                <span class="category-icon">{{ page.icon }}</span>
                {{ page.title }}
            </h1>
            <p class="category-description">{{ page.description }}</p>
        </div>
    </div>

    <div class="container">
        <div class="news-layout">
            <!-- 메인 뉴스 섹션 -->
            <main class="main-content">
                {% assign category_posts = site.posts | where: "category", page.category %}
                {% if category_posts.size > 0 %}
                    
                    <!-- 주요 뉴스 (첫 번째 포스트) -->
                    {% assign featured_post = category_posts.first %}
                    <article class="featured-article">
                        <div class="featured-image">
                            {% if featured_post.image %}
                                <img src="{{ featured_post.image }}" alt="{{ featured_post.title }}">
                            {% else %}
                                <div class="image-placeholder">
                                    <span>{{ page.icon }}</span>
                                </div>
                            {% endif %}
                        </div>
                        <div class="featured-content">
                            <span class="article-category" style="background-color: {{ page.color | default: '#3b82f6' }}">
                                {{ page.title }}
                            </span>
                            <h2 class="featured-title">
                                <a href="{{ featured_post.url }}">{{ featured_post.title }}</a>
                            </h2>
                            <p class="featured-excerpt">{{ featured_post.excerpt | strip_html | truncate: 200 }}</p>
                            <div class="article-meta">
                                <span class="meta-time">{{ featured_post.date | date: "%m월 %d일" }}</span>
                                <span class="meta-author">{{ featured_post.author | default: "속초일보" }}</span>
                                {% if featured_post.views %}
                                <span class="meta-views">조회 {{ featured_post.views }}회</span>
                                {% endif %}
                            </div>
                        </div>
                    </article>

                    <!-- 뉴스 목록 -->
                    <div class="news-list">
                        {% assign remaining_posts = category_posts | offset: 1 %}
                        {% for post in remaining_posts limit: 20 %}
                        <article class="news-item">
                            <div class="news-image">
                                {% if post.image %}
                                    <img src="{{ post.image }}" alt="{{ post.title }}">
                                {% else %}
                                    <div class="image-placeholder-small">{{ page.icon }}</div>
                                {% endif %}
                            </div>
                            <div class="news-content">
                                <h3 class="news-title">
                                    <a href="{{ post.url }}">{{ post.title }}</a>
                                </h3>
                                <p class="news-excerpt">{{ post.excerpt | strip_html | truncate: 120 }}</p>
                                <div class="news-meta">
                                    <span class="meta-time">{{ post.date | date: "%m월 %d일" }}</span>
                                    <span class="meta-author">{{ post.author | default: "속초일보" }}</span>
                                    <span class="meta-separator">|</span>
                                    {% if post.views %}
                                    <span class="meta-views">{{ post.views }}명 읽음</span>
                                    {% endif %}
                                </div>
                            </div>
                        </article>
                        {% endfor %}
                    </div>

                {% else %}
                    <!-- 빈 카테고리 상태 -->
                    <div class="empty-category">
                        <div class="empty-icon">{{ page.icon }}</div>
                        <h3>{{ page.title }} 카테고리의 기사가 준비 중입니다</h3>
                        <p>곧 새로운 소식을 전해드리겠습니다.</p>
                        <a href="{{ '/' | relative_url }}" class="back-home-btn">홈으로 돌아가기</a>
                    </div>
                {% endif %}
            </main>

            <!-- 사이드바 -->
            <aside class="sidebar">
                <!-- 다른 카테고리 -->
                <div class="sidebar-section">
                    <h3 class="sidebar-title">다른 카테고리</h3>
                    <ul class="category-list">
                        {% assign categories = "breaking,politics,economy,society,culture,tourism,sports" | split: "," %}
                        {% for cat in categories %}
                            {% unless cat == page.category %}
                            <li>
                                <a href="{{ '/category/' | append: cat | append: '/' | relative_url }}" 
                                   class="category-link {% if cat == page.category %}active{% endif %}">
                                    {% case cat %}
                                        {% when 'breaking' %}🚨 속보
                                        {% when 'politics' %}🏛️ 정치
                                        {% when 'economy' %}💼 경제
                                        {% when 'society' %}🏘️ 사회
                                        {% when 'culture' %}🎭 문화
                                        {% when 'tourism' %}🌊 관광
                                        {% when 'sports' %}⚽ 스포츠
                                    {% endcase %}
                                </a>
                            </li>
                            {% endunless %}
                        {% endfor %}
                    </ul>
                </div>

                <!-- 최신 뉴스 -->
                <div class="sidebar-section">
                    <h3 class="sidebar-title">최신 뉴스</h3>
                    <ul class="latest-news">
                        {% assign latest_posts = site.posts | limit: 5 %}
                        {% for post in latest_posts %}
                        <li class="latest-item">
                            <a href="{{ post.url }}" class="latest-link">
                                <span class="latest-title">{{ post.title | truncate: 30 }}</span>
                                <span class="latest-time">{{ post.date | date: "%m.%d" }}</span>
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </aside>
        </div>
    </div>
</div>

<style>
/* 전문적인 뉴스 사이트 스타일 카테고리 페이지 */
.category-page {
    background: #ffffff;
}

.category-header {
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
    padding: 20px 0;
}

.category-nav {
    font-size: 13px;
    color: #6c757d;
    margin-bottom: 10px;
}

.category-nav a {
    color: #6c757d;
    text-decoration: none;
}

.category-nav a:hover {
    color: #1e40af;
}

.nav-separator {
    margin: 0 8px;
}

.current-category {
    color: #1e40af;
    font-weight: 500;
}

.category-title {
    font-family: 'SokchoBadaDotum', sans-serif;
    font-size: 2rem;
    color: #212529;
    margin: 0 0 5px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.category-icon {
    font-size: 1.8rem;
}

.category-description {
    color: #6c757d;
    margin: 0;
    font-size: 14px;
}

.news-layout {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 40px;
    padding: 30px 0;
}

.main-content {
    min-height: 500px;
}

/* 주요 뉴스 */
.featured-article {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 40px;
    padding-bottom: 30px;
    border-bottom: 2px solid #e9ecef;
}

.featured-image img,
.image-placeholder {
    width: 100%;
    height: 250px;
    object-fit: cover;
    border-radius: 4px;
}

.image-placeholder {
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    color: #dee2e6;
}

.featured-content {
    padding: 10px 0;
}

.article-category {
    background: #1e40af;
    color: white;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 3px;
    display: inline-block;
    margin-bottom: 12px;
    font-weight: 500;
}

.featured-title {
    font-family: 'SokchoBadaBatang', serif;
    font-size: 1.4rem;
    line-height: 1.4;
    margin: 0 0 15px 0;
    font-weight: 600;
}

.featured-title a {
    color: #212529;
    text-decoration: none;
}

.featured-title a:hover {
    color: #1e40af;
}

.featured-excerpt {
    color: #495057;
    line-height: 1.6;
    margin-bottom: 15px;
    font-size: 14px;
}

.article-meta {
    font-size: 12px;
    color: #6c757d;
    display: flex;
    gap: 12px;
}

/* 뉴스 목록 */
.news-list {
    display: flex;
    flex-direction: column;
    gap: 25px;
}

.news-item {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 15px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e9ecef;
}

.news-image img {
    width: 120px;
    height: 80px;
    object-fit: cover;
    border-radius: 4px;
}

.image-placeholder-small {
    width: 120px;
    height: 80px;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: #dee2e6;
    border-radius: 4px;
}

.news-title {
    font-family: 'SokchoBadaBatang', serif;
    font-size: 16px;
    line-height: 1.4;
    margin: 0 0 8px 0;
    font-weight: 600;
}

.news-title a {
    color: #212529;
    text-decoration: none;
}

.news-title a:hover {
    color: #1e40af;
}

.news-excerpt {
    color: #6c757d;
    font-size: 13px;
    line-height: 1.5;
    margin: 0 0 8px 0;
}

.news-meta {
    font-size: 11px;
    color: #868e96;
    display: flex;
    gap: 8px;
    align-items: center;
}

.meta-separator {
    color: #dee2e6;
}

/* 사이드바 */
.sidebar {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    height: fit-content;
    position: sticky;
    top: 20px;
}

.sidebar-section {
    margin-bottom: 30px;
}

.sidebar-section:last-child {
    margin-bottom: 0;
}

.sidebar-title {
    font-family: 'SokchoBadaBatang', serif;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #1e40af;
    color: #212529;
}

.category-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.category-list li {
    margin-bottom: 8px;
}

.category-link {
    display: block;
    padding: 8px 12px;
    color: #495057;
    text-decoration: none;
    border-radius: 4px;
    font-size: 14px;
    transition: all 0.2s;
}

.category-link:hover,
.category-link.active {
    background: #1e40af;
    color: white;
}

.latest-news {
    list-style: none;
    margin: 0;
    padding: 0;
}

.latest-item {
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e9ecef;
}

.latest-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.latest-link {
    display: block;
    text-decoration: none;
    color: #495057;
}

.latest-title {
    display: block;
    font-size: 13px;
    line-height: 1.4;
    margin-bottom: 4px;
}

.latest-link:hover .latest-title {
    color: #1e40af;
}

.latest-time {
    font-size: 11px;
    color: #868e96;
}

/* 빈 카테고리 */
.empty-category {
    text-align: center;
    padding: 80px 20px;
    color: #6c757d;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 20px;
    opacity: 0.5;
}

.empty-category h3 {
    font-family: 'SokchoBadaBatang', serif;
    margin-bottom: 10px;
    color: #495057;
}

.back-home-btn {
    display: inline-block;
    margin-top: 20px;
    padding: 10px 20px;
    background: #1e40af;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-size: 14px;
}

.back-home-btn:hover {
    background: #1e3a8a;
}

/* 반응형 */
@media (max-width: 768px) {
    .news-layout {
        grid-template-columns: 1fr;
        gap: 30px;
    }
    
    .featured-article {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .featured-image img,
    .image-placeholder {
        height: 200px;
    }
    
    .news-item {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    
    .news-image img,
    .image-placeholder-small {
        width: 100%;
        height: 150px;
    }
    
    .category-title {
        font-size: 1.5rem;
    }
    
    .sidebar {
        order: -1;
        margin-bottom: 20px;
    }
}
</style>
'''
    
    with open(layout_dir / 'category.html', 'w', encoding='utf-8') as f:
        f.write(layout_content)
    
    print("✅ 전문적인 뉴스 사이트 스타일 카테고리 레이아웃 생성됨: _layouts/category.html")

def create_category_pages():
    """각 카테고리별 페이지 생성"""
    category_dir = Path('category')
    category_dir.mkdir(exist_ok=True)
    
    for category_key, category_data in CATEGORIES.items():
        page_content = f'''---
layout: category
title: {category_data['title']}
category: {category_key}
icon: {category_data['icon']}
description: {category_data['description']}
color: {category_data['color']}
permalink: /category/{category_key}/
---
'''
        
        page_file = category_dir / f'{category_key}.md'
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_content)
        
        print(f"✅ 카테고리 페이지 생성됨: {page_file}")

def create_sample_posts():
    """현실적인 샘플 뉴스 포스트 생성"""
    posts_dir = Path('_posts')
    posts_dir.mkdir(exist_ok=True)
    
    sample_posts = [
        {
            'filename': '2024-06-12-budget-tourism-investment.md',
            'title': '속초시 2024년 예산안 확정... 관광개발에 78억원 집중 투입',
            'category': 'politics',
            'image': 'https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=600&h=300&fit=crop',
            'author': '김기자',
            'views': 1247,
            'content': '''속초시가 내년도 예산을 총 580억원 규모로 확정했다고 12일 발표했다.

이번 예산안의 핵심은 관광인프라 개발에 78억원을 대폭 투입하기로 한 점이다. 시는 코로나19 이후 침체된 관광산업 회복을 위해 과감한 투자가 필요하다고 판단했다고 밝혔다.

주요 투자 분야는 ▲설악산 관광 활성화 사업 25억원 ▲해수욕장 시설 현대화 20억원 ▲속초항 관광 인프라 구축 18억원 ▲신규 관광 콘텐츠 개발 15억원 등이다.

속초시 관계자는 "속초만의 차별화된 관광 상품 개발과 인프라 구축을 통해 연간 관광객 1천만명 유치를 목표로 하고 있다"고 말했다.'''
        },
        {
            'filename': '2024-06-12-seorak-cable-car.md',
            'title': '설악산 케이블카 재추진... 환경단체 "강력 반대" 입장 표명',
            'category': 'tourism',
            'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=300&fit=crop',
            'author': '박기자',
            'views': 892,
            'content': '''설악산 케이블카 설치 논의가 다시 수면 위로 올라왔다. 강원도와 속초시는 관광 활성화를 위해 필요하다는 입장이지만, 환경단체들은 자연 훼손을 우려하며 강력히 반대하고 있다.

강원도는 11일 "설악산 케이블카 설치를 통해 연간 관광객 200만명 증가 효과를 기대할 수 있다"며 "경제적 파급효과가 클 것"이라고 밝혔다.

반면 환경운동연합 등 시민단체들은 "설악산은 천연기념물이자 생물권보전지역으로 절대 보전해야 할 자연유산"이라며 "케이블카 설치는 생태계 파괴를 가져올 것"이라고 반박했다.

환경부는 "정밀한 환경영향평가를 통해 신중하게 검토하겠다"는 입장을 밝혔다.'''
        },
        {
            'filename': '2024-06-11-sokcho-beach-safety.md',
            'title': '속초해수욕장 피서철 대비 안전점검 완료... 7월 1일 개장',
            'category': 'society',
            'image': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&h=300&fit=crop',
            'author': '이기자',
            'views': 654,
            'content': '''속초시는 다가오는 피서철을 대비해 속초해수욕장 전체 시설에 대한 안전점검을 완료했다고 11일 발표했다.

이번 점검에서는 ▲해수욕장 편의시설 ▲안전시설 ▲수질 상태 ▲주변 교통 인프라 등을 종합적으로 검토했다.

특히 올해는 코로나19 완화로 많은 피서객이 몰릴 것으로 예상됨에 따라 안전관리에 더욱 신경을 쓰고 있다고 시는 설명했다.

속초해수욕장은 7월 1일 공식 개장하며, 8월 31일까지 운영된다. 해수욕장에는 안전요원 24명이 배치되고, 의료진과 구급차도 상시 대기할 예정이다.'''
        },
        {
            'filename': '2024-06-11-fishing-port-renovation.md',
            'title': '속초항 수산물 직판장 리모델링 완료... 관광객 유치 기대',
            'category': 'economy',
            'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&h=300&fit=crop',
            'author': '최기자',
            'views': 423,
            'content': '''30억원을 투입한 속초항 수산물 직판장 리모델링 공사가 완료됐다.

새롭게 단장된 직판장은 현대적인 시설과 쾌적한 환경으로 탈바꿈했다. 특히 관광객들이 편리하게 이용할 수 있도록 편의시설을 대폭 확충했다.

주요 개선사항으로는 ▲냉장·냉동 보관시설 현대화 ▲고객 휴게공간 확대 ▲주차장 정비 ▲화장실 시설 개선 등이 있다.

속초항수협 관계자는 "깨끗하고 현대적인 시설로 더 많은 관광객들이 찾아올 것으로 기대한다"며 "신선한 수산물을 합리적인 가격에 제공하겠다"고 말했다.'''
        },
        {
            'filename': '2024-06-10-food-festival.md',
            'title': '속초 대표 음식축제 개최... 오징어순대와 닭강정 인기',
            'category': 'culture',
            'image': 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=600&h=300&fit=crop',
            'author': '정기자',
            'views': 1156,
            'content': '''속초시 대표 먹거리를 한자리에서 즐길 수 있는 '속초 음식축제'가 중앙시장 일대에서 성황리에 열렸다.

10일 오후 2시부터 시작된 축제에는 시민과 관광객 약 5천명이 참여해 속초의 대표 음식들을 맛봤다.

특히 속초의 명물인 오징어순대와 닭강정, 아바이순대 등이 큰 인기를 끌었다. 또한 최근 SNS에서 화제가 된 속초 어묵과 물닭갈비도 많은 관심을 받았다.

시 관계자는 "속초만의 독특한 음식 문화를 널리 알리는 기회가 됐다"며 "앞으로도 지역 음식 홍보에 더욱 힘쓰겠다"고 밝혔다.

축제는 이틀간 계속되며, 11일 오후 8시에 마무리된다.'''
        },
        {
            'filename': '2024-06-10-highway-extension.md',
            'title': '속초-양양 고속도로 연장 공사 순조... 내년 상반기 개통 예정',
            'category': 'society',
            'image': 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600&h=300&fit=crop',
            'author': '김기자',
            'views': 789,
            'content': '''동해고속도로 속초-양양 구간 연장 공사가 순조롭게 진행되고 있어 내년 상반기 개통이 가능할 것으로 보인다.

한국도로공사는 10일 "현재 공정률이 85%에 달하며, 예정대로 2025년 6월 개통을 목표로 하고 있다"고 밝혔다.

이 구간이 개통되면 서울에서 양양까지의 접근성이 크게 향상될 것으로 기대된다. 현재 서울-속초 구간은 2시간 30분이 걸리지만, 연장 구간 개통 후에는 양양까지 추가로 20분 정도만 더 소요될 전망이다.

이는 강원 영동지역 관광 활성화에도 큰 도움이 될 것으로 예상된다. 특히 설악산과 낙산사, 하조대 등 주요 관광지 접근성이 향상되면서 관광객 증가 효과를 기대할 수 있다.'''
        }
    ]
    
    for i, post_data in enumerate(sample_posts):
        # 게시 날짜를 점진적으로 과거로 설정
        post_date = datetime.now() - timedelta(days=i)
        
        post_content = f'''---
layout: post
title: "{post_data['title']}"
date: {post_date.strftime('%Y-%m-%d %H:%M:%S')} +0900
category: {post_data['category']}
author: {post_data['author']}
image: {post_data['image']}
views: {post_data['views']}
excerpt: "{post_data['content'][:100]}..."
---

{post_data['content']}

---

**관련 기사**
- [속초시 공식 홈페이지](https://www.sokcho.go.kr)
- [강원도청 보도자료](https://www.gangwon.go.kr)

**태그**: #{post_data['category']} #속초 #속초시 #강원도 #뉴스
'''
        
        post_file = posts_dir / post_data['filename']
        with open(post_file, 'w', encoding='utf-8') as f:
            f.write(post_content)
        
        print(f"✅ 샘플 뉴스 포스트 생성됨: {post_file}")

def create_post_layout():
    """포스트 레이아웃 생성 (개별 기사 페이지용)"""
    layout_dir = Path('_layouts')
    layout_dir.mkdir(exist_ok=True)
    
    post_layout = '''---
layout: default
---

<article class="news-article">
    <div class="container">
        <!-- 기사 헤더 -->
        <header class="article-header">
            <div class="article-category-nav">
                <a href="{{ '/' | relative_url }}">홈</a>
                <span>></span>
                <a href="{{ '/category/' | append: page.category | append: '/' | relative_url }}">
                    {% case page.category %}
                        {% when 'breaking' %}속보
                        {% when 'politics' %}정치
                        {% when 'economy' %}경제
                        {% when 'society' %}사회
                        {% when 'culture' %}문화
                        {% when 'tourism' %}관광
                        {% when 'sports' %}스포츠
                    {% endcase %}
                </a>
                <span>></span>
                <span class="current-article">{{ page.title | truncate: 30 }}</span>
            </div>
            
            <h1 class="article-title">{{ page.title }}</h1>
            
            <div class="article-meta">
                <div class="meta-left">
                    <span class="meta-author">{{ page.author | default: "속초일보" }}</span>
                    <span class="meta-date">{{ page.date | date: "%Y년 %m월 %d일 %H:%M" }}</span>
                </div>
                <div class="meta-right">
                    {% if page.views %}
                    <span class="meta-views">조회 {{ page.views }}회</span>
                    {% endif %}
                    <button class="share-btn" onclick="shareArticle()">공유</button>
                </div>
            </div>
        </header>

        <!-- 기사 내용 -->
        <div class="article-body">
            {% if page.image %}
            <figure class="article-image">
                <img src="{{ page.image }}" alt="{{ page.title }}">
                <figcaption>{{ page.title }}</figcaption>
            </figure>
            {% endif %}
            
            <div class="article-content">
                {{ content }}
            </div>
        </div>

        <!-- 기사 하단 -->
        <footer class="article-footer">
            <div class="article-tags">
                {% if page.tags %}
                    {% for tag in page.tags %}
                        <span class="tag">#{{ tag }}</span>
                    {% endfor %}
                {% endif %}
            </div>
            
            <div class="article-actions">
                <button class="action-btn like-btn">👍 좋아요</button>
                <button class="action-btn share-btn" onclick="shareArticle()">📤 공유</button>
                <button class="action-btn print-btn" onclick="window.print()">🖨️ 인쇄</button>
            </div>
        </footer>

        <!-- 관련 기사 -->
        <section class="related-articles">
            <h3>관련 기사</h3>
            <div class="related-grid">
                {% assign related_posts = site.posts | where: "category", page.category | limit: 4 %}
                {% for post in related_posts %}
                    {% unless post.url == page.url %}
                    <article class="related-item">
                        <a href="{{ post.url }}">
                            {% if post.image %}
                                <img src="{{ post.image }}" alt="{{ post.title }}">
                            {% endif %}
                            <h4>{{ post.title | truncate: 50 }}</h4>
                            <span class="related-date">{{ post.date | date: "%m.%d" }}</span>
                        </a>
                    </article>
                    {% endunless %}
                {% endfor %}
            </div>
        </section>
    </div>
</article>

<style>
/* 기사 페이지 스타일 */
.news-article {
    background: white;
    padding: 20px 0;
}

.article-header {
    border-bottom: 1px solid #e9ecef;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.article-category-nav {
    font-size: 13px;
    color: #6c757d;
    margin-bottom: 15px;
}

.article-category-nav a {
    color: #6c757d;
    text-decoration: none;
}

.article-category-nav a:hover {
    color: #1e40af;
}

.article-category-nav span {
    margin: 0 8px;
}

.current-article {
    color: #1e40af;
}

.article-title {
    font-family: 'SokchoBadaBatang', serif;
    font-size: 2rem;
    line-height: 1.3;
    color: #212529;
    margin: 0 0 20px 0;
    font-weight: 600;
}

.article-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    color: #6c757d;
}

.meta-left {
    display: flex;
    gap: 15px;
}

.meta-author {
    font-weight: 600;
    color: #495057;
}

.meta-right {
    display: flex;
    gap: 10px;
    align-items: center;
}

.share-btn {
    background: #1e40af;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    font-size: 12px;
    cursor: pointer;
}

.article-body {
    max-width: 800px;
    margin: 0 auto;
}

.article-image {
    margin: 0 0 30px 0;
    text-align: center;
}

.article-image img {
    width: 100%;
    max-width: 600px;
    height: auto;
    border-radius: 4px;
}

.article-image figcaption {
    font-size: 12px;
    color: #6c757d;
    margin-top: 8px;
    font-style: italic;
}

.article-content {
    font-size: 16px;
    line-height: 1.8;
    color: #212529;
}

.article-content p {
    margin-bottom: 20px;
}

.article-content h3 {
    font-family: 'SokchoBadaBatang', serif;
    margin: 30px 0 15px 0;
    color: #1e40af;
}

.article-footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #e9ecef;
}

.article-tags {
    margin-bottom: 20px;
}

.tag {
    display: inline-block;
    background: #f8f9fa;
    color: #495057;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    margin-right: 8px;
    margin-bottom: 8px;
}

.article-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
}

.action-btn {
    background: white;
    border: 1px solid #dee2e6;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.action-btn:hover {
    background: #f8f9fa;
}

.related-articles {
    margin-top: 50px;
    padding-top: 30px;
    border-top: 2px solid #e9ecef;
}

.related-articles h3 {
    font-family: 'SokchoBadaBatang', serif;
    font-size: 1.3rem;
    margin-bottom: 20px;
    color: #212529;
}

.related-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.related-item {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s;
}

.related-item:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.related-item a {
    display: block;
    text-decoration: none;
    color: #212529;
}

.related-item img {
    width: 100%;
    height: 120px;
    object-fit: cover;
}

.related-item h4 {
    padding: 12px;
    font-size: 14px;
    line-height: 1.4;
    margin: 0;
    font-weight: 500;
}

.related-date {
    display: block;
    padding: 0 12px 12px 12px;
    font-size: 12px;
    color: #6c757d;
}

/* 반응형 */
@media (max-width: 768px) {
    .article-title {
        font-size: 1.5rem;
    }
    
    .article-meta {
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
    }
    
    .article-content {
        font-size: 15px;
    }
    
    .related-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
function shareArticle() {
    if (navigator.share) {
        navigator.share({
            title: document.title,
            url: window.location.href
        });
    } else {
        // 폴백: URL 복사
        navigator.clipboard.writeText(window.location.href);
        alert('링크가 복사되었습니다.');
    }
}
</script>
'''
    
    with open(layout_dir / 'post.html', 'w', encoding='utf-8') as f:
        f.write(post_layout)
    
    print("✅ 포스트 레이아웃 생성됨: _layouts/post.html")

def update_config():
    """_config.yml에 필요한 설정 추가"""
    config_file = Path('_config.yml')
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 페이지네이션 설정 추가
        if 'paginate:' not in content:
            pagination_config = '''
# 페이지네이션 설정
paginate: 10
paginate_path: "/page:num/"

# 컬렉션 설정
collections:
  posts:
    output: true
    permalink: /:year/:month/:day/:title/

# 기본값 설정
defaults:
  - scope:
      path: ""
      type: "posts"
    values:
      layout: "post"
      author: "속초일보"
  - scope:
      path: "category"
      type: "pages"
    values:
      layout: "category"
'''
            
            with open(config_file, 'a', encoding='utf-8') as f:
                f.write(pagination_config)
            
            print("✅ _config.yml에 페이지네이션 및 기본값 설정 추가")
        else:
            print("✅ _config.yml 설정이 이미 존재합니다.")
    else:
        print("⚠️  _config.yml 파일이 없습니다. Jekyll 설정을 확인해주세요.")

def main():
    """메인 실행 함수"""
    print("🚀 전문적인 뉴스 사이트 스타일 속초일보 카테고리 페이지 생성 시작...")
    print("="*60)
    
    try:
        # 1. 카테고리 레이아웃 생성
        create_category_layout()
        
        # 2. 포스트 레이아웃 생성
        create_post_layout()
        
        # 3. 카테고리 페이지들 생성
        create_category_pages()
        
        # 4. 샘플 포스트 생성 (선택적)
        response = input("\n현실적인 샘플 뉴스 포스트를 생성하시겠습니까? (y/n): ")
        if response.lower() in ['y', 'yes', '예']:
            create_sample_posts()
        
        # 5. 설정 파일 업데이트
        update_config()
        
        print("\n" + "="*60)
        print("✨ 전문적인 뉴스 사이트 스타일 카테고리 페이지 생성 완료!")
        print("\n📋 생성된 파일들:")
        print("├── _layouts/category.html  (카테고리 페이지 레이아웃)")
        print("├── _layouts/post.html      (개별 기사 페이지 레이아웃)")
        print("├── category/politics.md    (정치 카테고리)")
        print("├── category/economy.md     (경제 카테고리)")
        print("├── category/society.md     (사회 카테고리)")
        print("├── category/culture.md     (문화 카테고리)")
        print("├── category/tourism.md     (관광 카테고리)")
        print("├── category/sports.md      (스포츠 카테고리)")
        print("└── _posts/*.md             (샘플 뉴스 포스트들)")
        
        print("\n🎯 주요 기능:")
        print("✅ 현대적이고 전문적인 뉴스 레이아웃")
        print("✅ 반응형 디자인 (모바일/태블릿/데스크톱 대응)")
        print("✅ 카테고리별 색상 구분")
        print("✅ 주요 뉴스와 일반 뉴스 구분 표시")
        print("✅ 사이드바에 다른 카테고리 및 최신 뉴스")
        print("✅ 개별 기사 페이지 최적화")
        print("✅ 소셜 공유 기능")
        
        print("\n🚀 다음 단계:")
        print("1. git add . && git commit -m '전문적인 뉴스 스타일 카테고리 페이지 추가'")
        print("2. git push")
        print("3. GitHub Pages 빌드 대기 (약 1-2분)")
        print("4. https://sokchodaily.github.io에서 확인")
        print("5. 네비게이션 메뉴 클릭하여 404 에러 해결 확인")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()