"""
🤖 AI 기사 작성 엔진 - 속초일보 AI 뉴스 시스템
HWP 보도자료를 분석하여 속초일보 스타일의 기사를 자동 작성

작성자: AI 시스템 for 김도엽 발행인
"""

import os
import sys
import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests

# AI API 관련 (Google Gemini)
try:
    import google.generativeai as genai
except ImportError:
    print("⚠️ Google Generative AI 라이브러리가 없습니다: pip install google-generativeai")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_writer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AINewsWriter:
    """
    🖋️ AI 기사 작성 클래스
    보도자료를 분석하여 속초일보 스타일의 기사를 자동 생성합니다.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        🎯 AI 기사 작성기 초기화
        
        Args:
            api_key (str): Google Gemini API 키
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("🤖 Google Gemini API 연결 성공")
        else:
            self.model = None
            logger.warning("⚠️ AI API 키가 없습니다. 로컬 템플릿 모드로 실행됩니다.")
        
        # 속초일보 스타일 가이드라인
        self.style_guide = {
            'tone': '정확하고 공정한',
            'perspective': '지역 주민 중심',
            'focus': '속초와 강원도 지역',
            'length': '400-800자',
            'format': '육하원칙 기반'
        }
        
        # 카테고리 분류
        self.categories = {
            '속초시': '정치',
            '강원도': '정치', 
            '교육청': '사회',
            '문화재청': '문화',
            '해양경찰서': '사회',
            '관광': '관광',
            '축제': '문화',
            '예산': '정치',
            '개발': '경제'
        }
        
        logger.info("🖋️ AI 기사 작성기 초기화 완료")
    
    def write_article(self, hwp_data: Dict) -> Dict:
        """
        📰 보도자료 데이터를 기반으로 기사 작성
        
        Args:
            hwp_data (Dict): HWP 파서에서 추출한 데이터
            
        Returns:
            Dict: 완성된 기사 데이터 (제목, 본문, 메타데이터)
        """
        try:
            logger.info("🖋️ AI 기사 작성 시작")
            
            # 1. 원본 데이터 분석
            analysis = self._analyze_content(hwp_data)
            
            # 2. 카테고리 분류
            category = self._classify_category(hwp_data, analysis)
            
            # 3. 기사 제목 생성
            title = self._generate_title(hwp_data, analysis)
            
            # 4. 기사 본문 작성
            content = self._generate_content(hwp_data, analysis)
            
            # 5. 기사 메타데이터 생성
            metadata = self._generate_metadata(hwp_data, analysis, category)
            
            article = {
                'title': title,
                'content': content,
                'category': category,
                'metadata': metadata,
                'source_data': hwp_data,
                'analysis': analysis,
                'created_at': datetime.now().isoformat(),
                'author': 'AI 기자 (속초일보)',
                'status': 'draft'
            }
            
            logger.info(f"✅ AI 기사 작성 완료: {title}")
            return article
            
        except Exception as e:
            logger.error(f"❌ AI 기사 작성 실패: {e}")
            raise
    
    def _analyze_content(self, hwp_data: Dict) -> Dict:
        """
        🔍 보도자료 내용 분석
        """
        text = hwp_data.get('text', '')
        press_info = hwp_data.get('press_release_info', {})
        
        analysis = {
            'key_topics': self._extract_key_topics(text),
            'entities': self._extract_entities(text),
            'agency': press_info.get('agency', ''),
            'urgency': self._assess_urgency(text),
            'impact': self._assess_impact(text),
            'local_relevance': self._assess_local_relevance(text)
        }
        
        logger.info("🔍 내용 분석 완료")
        return analysis
    
    def _classify_category(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        📂 기사 카테고리 분류
        """
        text = hwp_data.get('text', '').lower()
        agency = analysis.get('agency', '')
        
        # 키워드 기반 분류
        category_keywords = {
            '정치': ['예산', '정책', '시장', '도지사', '의회', '조례'],
            '경제': ['사업', '투자', '개발', '기업', '일자리', '경제'],
            '사회': ['교육', '복지', '안전', '의료', '주민', '시민'],
            '문화': ['축제', '공연', '전시', '문화재', '예술', '체험'],
            '관광': ['관광객', '여행', '명소', '숙박', '맛집', '레저'],
            '스포츠': ['경기', '대회', '선수', '체육', '운동', '스포츠']
        }
        
        # 발신기관 기반 분류
        if agency in self.categories:
            return self.categories[agency]
        
        # 키워드 점수 계산
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # 최고 점수 카테고리 반환
        best_category = max(scores, key=scores.get) if scores else '사회'
        
        logger.info(f"📂 카테고리 분류: {best_category}")
        return best_category
    
    def _generate_title(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        📰 기사 제목 생성
        """
        original_title = hwp_data.get('title', '')
        
        if self.api_key:
            # AI를 사용한 제목 생성
            title = self._ai_generate_title(hwp_data, analysis)
        else:
            # 템플릿 기반 제목 생성
            title = self._template_generate_title(hwp_data, analysis)
        
        # 제목 최적화
        title = self._optimize_title(title)
        
        logger.info(f"📰 제목 생성: {title}")
        return title
    
    def _generate_content(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        📝 기사 본문 생성
        """
        if self.api_key:
            # AI를 사용한 본문 생성
            content = self._ai_generate_content(hwp_data, analysis)
        else:
            # 템플릿 기반 본문 생성
            content = self._template_generate_content(hwp_data, analysis)
        
        # 본문 최적화
        content = self._optimize_content(content)
        
        logger.info(f"📝 본문 생성 완료: {len(content)}자")
        return content
    
    def _ai_generate_title(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        🤖 AI를 사용한 제목 생성 (Google Gemini)
        """
        try:
            prompt = f"""
            당신은 속초일보의 전문 기자입니다. 다음 보도자료를 바탕으로 지역 주민들이 관심을 가질 만한 기사 제목을 작성해주세요.

            **속초일보 제목 가이드라인:**
            - 속초와 강원도 지역에 미치는 영향 강조
            - 50자 이내로 간결하게
            - 정확하고 객관적인 표현 사용
            - 지역 주민의 관심을 끌 수 있는 내용

            **보도자료 내용:**
            제목: {hwp_data.get('title', '')}
            발신기관: {analysis.get('agency', '')}
            주요 내용: {hwp_data.get('text', '')[:500]}...

            **생성할 제목만 답변해주세요:**
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=100,
                    temperature=0.7
                )
            )
            
            title = response.text.strip()
            return title
            
        except Exception as e:
            logger.warning(f"⚠️ AI 제목 생성 실패, 템플릿 사용: {e}")
            return self._template_generate_title(hwp_data, analysis)
    
    def _ai_generate_content(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        🤖 AI를 사용한 본문 생성 (Google Gemini)
        """
        try:
            prompt = f"""
            당신은 속초일보의 전문 기자입니다. 다음 보도자료를 바탕으로 지역 주민들을 위한 기사를 작성해주세요.

            **속초일보 기사 스타일:**
            - 육하원칙(누가, 언제, 어디서, 무엇을, 왜, 어떻게) 준수
            - 지역 주민의 시각에서 작성
            - 속초와 강원도 지역에 미치는 영향 중점 서술
            - 400-600자 분량
            - 정확하고 공정한 보도

            **보도자료 정보:**
            발신기관: {analysis.get('agency', '')}
            원문: {hwp_data.get('text', '')}

            **기사 작성 요구사항:**
            1. 리드 문단: 핵심 내용 요약
            2. 세부 내용: 구체적인 설명
            3. 배경/의미: 지역에 미치는 영향
            4. 마무리: 향후 전망이나 주민 반응

            **기사 본문만 작성해주세요:**
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.6
                )
            )
            
            content = response.text.strip()
            return content
            
        except Exception as e:
            logger.warning(f"⚠️ AI 본문 생성 실패, 템플릿 사용: {e}")
            return self._template_generate_content(hwp_data, analysis)
    
    def _template_generate_title(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        📝 템플릿 기반 제목 생성 (AI 미사용시)
        """
        original_title = hwp_data.get('title', '')
        agency = analysis.get('agency', '')
        
        # 기본 제목 정리
        title = original_title
        
        # 지역 관련 키워드 강조
        if '속초' not in title and agency == '속초시':
            title = f"속초시, {title}"
        elif '강원도' not in title and agency == '강원도':
            title = f"강원도, {title}"
        
        # 불필요한 문구 제거
        title = re.sub(r'보도자료|공지|알림', '', title).strip()
        
        # 길이 제한
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title or "제목 없음"
    
    def _template_generate_content(self, hwp_data: Dict, analysis: Dict) -> str:
        """
        📝 템플릿 기반 본문 생성 (AI 미사용시)
        """
        original_text = hwp_data.get('text', '')
        agency = analysis.get('agency', '')
        
        # 기본 기사 구조
        content_parts = []
        
        # 리드 문단
        lead = f"{agency}가 새로운 소식을 발표했다."
        content_parts.append(lead)
        
        # 본문 (원문에서 주요 내용 추출)
        sentences = re.split(r'[.!?]', original_text)
        main_content = []
        
        for sentence in sentences[:5]:  # 상위 5개 문장
            cleaned = sentence.strip()
            if len(cleaned) > 10:  # 의미있는 문장만
                main_content.append(cleaned + ".")
        
        if main_content:
            content_parts.extend(main_content)
        
        # 마무리
        closing = f"이번 발표는 속초 지역에 긍정적인 영향을 미칠 것으로 예상된다."
        content_parts.append(closing)
        
        return '\n\n'.join(content_parts)
    
    def _generate_metadata(self, hwp_data: Dict, analysis: Dict, category: str) -> Dict:
        """
        📊 기사 메타데이터 생성
        """
        metadata = {
            'category': category,
            'tags': self._generate_tags(hwp_data, analysis),
            'location': '속초',
            'source': analysis.get('agency', ''),
            'urgency': analysis.get('urgency', 'normal'),
            'images': len(hwp_data.get('images', [])),
            'word_count': len(hwp_data.get('text', '')),
            'reading_time': f"{max(1, len(hwp_data.get('text', '')) // 300)}분"
        }
        
        return metadata
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """
        🔑 주요 토픽 추출
        """
        # 간단한 키워드 추출 (TF-IDF나 다른 방법으로 개선 가능)
        topics = []
        keywords = ['속초', '강원도', '시민', '주민', '개발', '문화', '관광', '교육', '복지']
        
        for keyword in keywords:
            if keyword in text:
                topics.append(keyword)
        
        return topics[:5]  # 상위 5개만
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        🏢 개체명 추출 (기관명, 인명, 지명 등)
        """
        entities = []
        
        # 정규표현식으로 기본적인 개체명 추출
        patterns = {
            '기관': r'(속초시|강원도|교육청|해양경찰서|문화재청)',
            '인명': r'([가-힣]{2,3})\s*(시장|도지사|청장|과장)',
            '지명': r'(속초|강릉|춘천|원주|동해|태백)'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        return list(set(entities))  # 중복 제거
    
    def _assess_urgency(self, text: str) -> str:
        """
        ⚡ 긴급도 평가
        """
        urgent_keywords = ['긴급', '즉시', '신속', '조속', '우선']
        normal_keywords = ['추진', '계획', '예정', '진행']
        
        urgent_count = sum(1 for keyword in urgent_keywords if keyword in text)
        
        if urgent_count > 0:
            return 'urgent'
        else:
            return 'normal'
    
    def _assess_impact(self, text: str) -> str:
        """
        📊 영향도 평가
        """
        high_impact_keywords = ['대규모', '전체', '모든', '전면', '대폭']
        medium_impact_keywords = ['일부', '부분', '개선', '확대']
        
        high_count = sum(1 for keyword in high_impact_keywords if keyword in text)
        medium_count = sum(1 for keyword in medium_impact_keywords if keyword in text)
        
        if high_count > 0:
            return 'high'
        elif medium_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _assess_local_relevance(self, text: str) -> float:
        """
        🏠 지역 관련성 평가 (0-1 사이 점수)
        """
        local_keywords = ['속초', '강원도', '지역', '주민', '시민', '동해', '설악산']
        
        total_words = len(text.split())
        local_mentions = sum(1 for keyword in local_keywords if keyword in text)
        
        relevance = min(1.0, local_mentions / max(1, total_words * 0.1))
        return relevance
    
    def _generate_tags(self, hwp_data: Dict, analysis: Dict) -> List[str]:
        """
        🏷️ 기사 태그 생성
        """
        tags = []
        
        # 기본 태그
        agency = analysis.get('agency', '')
        if agency:
            tags.append(agency)
        
        # 토픽 기반 태그
        tags.extend(analysis.get('key_topics', []))
        
        # 개체명 기반 태그
        tags.extend(analysis.get('entities', [])[:3])  # 상위 3개만
        
        # 중복 제거 및 정리
        tags = list(set(tags))
        tags = [tag for tag in tags if len(tag) > 1]  # 1글자 태그 제외
        
        return tags[:8]  # 최대 8개
    
    def _optimize_title(self, title: str) -> str:
        """
        ✨ 제목 최적화
        """
        # 불필요한 공백 제거
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 특수문자 정리
        title = re.sub(r'[""''`]', '"', title)
        
        # 길이 제한
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def _optimize_content(self, content: str) -> str:
        """
        ✨ 본문 최적화
        """
        # 문단 정리
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 불필요한 공백 제거
        content = re.sub(r' +', ' ', content)
        
        # 문장 끝 정리
        content = re.sub(r'\.+', '.', content)
        
        return content.strip()
    
    def save_article(self, article: Dict, output_dir: str = "_posts") -> str:
        """
        💾 완성된 기사를 Jekyll 포스트 형식으로 저장
        
        Args:
            article (Dict): 완성된 기사 데이터
            output_dir (str): 출력 디렉토리
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            # Jekyll 포스트 파일명 형식: YYYY-MM-DD-title.md
            date_str = datetime.now().strftime("%Y-%m-%d")
            title_slug = re.sub(r'[^\w가-힣]', '-', article['title'])[:50]
            filename = f"{date_str}-{title_slug}.md"
            
            output_path = Path(output_dir) / filename
            output_path.parent.mkdir(exist_ok=True)
            
            # Jekyll Front Matter 생성
            front_matter = {
                'layout': 'post',
                'title': article['title'],
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S +0900"),
                'category': article['category'],
                'author': article['author'],
                'tags': article['metadata']['tags'],
                'source': article['metadata']['source'],
                'location': article['metadata']['location']
            }
            
            # 마크다운 파일 생성
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("---\n")
                for key, value in front_matter.items():
                    if isinstance(value, list):
                        f.write(f"{key}: {value}\n")
                    else:
                        f.write(f"{key}: \"{value}\"\n")
                f.write("---\n\n")
                f.write(article['content'])
            
            logger.info(f"💾 기사 저장 완료: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ 기사 저장 실패: {e}")
            raise


def main():
    """
    🧪 AI 기사 작성기 테스트 함수
    """
    # 테스트용 HWP 데이터 (실제로는 HWPParser에서 가져옴)
    test_hwp_data = {
        'title': '속초시 2025년 관광 활성화 계획 발표',
        'text': '속초시가 2025년 관광 활성화를 위한 종합계획을 발표했다. 이번 계획에는 해수욕장 시설 개선과 설악산 케이블카 검토가 포함되어 있다.',
        'images': [],
        'metadata': {'filename': 'test.hwp'},
        'press_release_info': {'agency': '속초시'}
    }
    
    # AI 기사 작성기 초기화
    writer = AINewsWriter()
    
    # 기사 작성
    article = writer.write_article(test_hwp_data)
    
    print("🎉 AI 기사 작성 결과:")
    print(f"📰 제목: {article['title']}")
    print(f"📂 카테고리: {article['category']}")
    print(f"📝 본문: {article['content'][:200]}...")
    print(f"🏷️ 태그: {article['metadata']['tags']}")
    
    # 기사 저장
    saved_path = writer.save_article(article)
    print(f"💾 저장 위치: {saved_path}")


if __name__ == "__main__":
    main() 