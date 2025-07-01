#!/usr/bin/env python3
"""
🤖 속초일보 AI 뉴스 시스템 - 메인 실행기
HWP 보도자료 → AI 기사 작성 → GitHub Pages 자동 발행

작성자: AI 시스템 for 김도엽 발행인
실행 명령: python main_ai_news.py
"""

import sys
import os
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

# 프로젝트 모듈들 import
try:
    from models.hwp_parser import HWPParser
    from controllers.ai_writer import AINewsWriter
    from controllers.github_publisher import GitHubPublisher
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("📁 현재 디렉토리에서 실행하고 있는지 확인하세요.")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_news_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SokchoDailyAINewsSystem:
    """
    🌊 속초일보 AI 뉴스 시스템 메인 클래스
    전체 뉴스 제작 파이프라인을 관리합니다.
    """
    
    def __init__(self, config_path: str = None):
        """
        🎯 AI 뉴스 시스템 초기화
        
        Args:
            config_path (str): 설정 파일 경로 (선택사항)
        """
        self.config = self._load_config(config_path)
        
        # 시스템 컴포넌트 초기화
        self.hwp_parser = None
        self.ai_writer = AINewsWriter(api_key=self.config.get('openai_api_key'))
        self.github_publisher = GitHubPublisher(
            repo_path=self.config.get('repo_path', '.'),
            branch=self.config.get('git_branch', 'main')
        )
        
        # 작업 디렉토리 설정
        self.input_dir = Path(self.config.get('input_dir', '../'))
        self.output_dir = Path(self.config.get('output_dir', '_posts'))
        self.output_dir.mkdir(exist_ok=True)
        
        # 통계 정보
        self.stats = {
            'processed_files': 0,
            'generated_articles': 0,
            'published_articles': 0,
            'failed_files': 0,
            'start_time': datetime.now(),
            'errors': []
        }
        
        logger.info("🌊 속초일보 AI 뉴스 시스템 초기화 완료")
    
    def _load_config(self, config_path: str = None) -> Dict:
        """
        ⚙️ 설정 파일 로드
        """
        default_config = {
            'input_dir': '../',
            'output_dir': '_posts',
            'repo_path': '.',
            'git_branch': 'main',
            'auto_publish': True,
            'supported_extensions': ['.hwp'],
            'max_articles_per_batch': 10,
            'backup_before_publish': True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"⚙️ 설정 파일 로드: {config_path}")
            except Exception as e:
                logger.warning(f"⚠️ 설정 파일 로드 실패, 기본값 사용: {e}")
        
        return default_config
    
    def process_single_hwp(self, hwp_file_path: str) -> Dict:
        """
        📄 단일 HWP 파일 처리
        
        Args:
            hwp_file_path (str): HWP 파일 경로
            
        Returns:
            Dict: 처리 결과
        """
        try:
            logger.info(f"📄 HWP 파일 처리 시작: {hwp_file_path}")
            
            # 1. HWP 파일 파싱
            self.hwp_parser = HWPParser(hwp_file_path)
            hwp_data = self.hwp_parser.parse()
            
            if not hwp_data['text'].strip():
                raise Exception("추출된 텍스트가 비어있습니다.")
            
            # 2. AI 기사 작성
            article_data = self.ai_writer.write_article(hwp_data)
            
            # 3. 기사 파일 저장
            article_file_path = self.ai_writer.save_article(
                article_data, 
                str(self.output_dir)
            )
            
            # 4. GitHub에 발행 (설정된 경우)
            published = False
            if self.config.get('auto_publish', True):
                published = self.github_publisher.publish_article(
                    article_data, 
                    article_file_path
                )
            
            # 통계 업데이트
            self.stats['processed_files'] += 1
            self.stats['generated_articles'] += 1
            if published:
                self.stats['published_articles'] += 1
            
            result = {
                'status': 'success',
                'hwp_file': hwp_file_path,
                'article_title': article_data['title'],
                'article_file': article_file_path,
                'published': published,
                'category': article_data['category'],
                'word_count': len(article_data['content'])
            }
            
            logger.info(f"✅ 처리 완료: {article_data['title']}")
            return result
            
        except Exception as e:
            self.stats['failed_files'] += 1
            self.stats['errors'].append({
                'file': hwp_file_path,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.error(f"❌ 처리 실패: {hwp_file_path} - {e}")
            return {
                'status': 'failed',
                'hwp_file': hwp_file_path,
                'error': str(e)
            }
    
    def process_batch_hwp(self, hwp_files: List[str]) -> List[Dict]:
        """
        📚 여러 HWP 파일 일괄 처리
        
        Args:
            hwp_files (List[str]): HWP 파일 경로 리스트
            
        Returns:
            List[Dict]: 처리 결과 리스트
        """
        logger.info(f"📚 일괄 처리 시작: {len(hwp_files)}개 파일")
        
        results = []
        successful_articles = []
        successful_files = []
        
        # 각 파일 개별 처리
        for hwp_file in hwp_files:
            result = self.process_single_hwp(hwp_file)
            results.append(result)
            
            if result['status'] == 'success':
                # 나중에 일괄 발행용 데이터 수집
                article_file = result['article_file']
                if Path(article_file).exists():
                    # 기사 데이터 다시 로드 (일괄 발행용)
                    with open(article_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 간단한 기사 데이터 구성 (실제로는 더 정교하게)
                        article_data = {
                            'title': result['article_title'],
                            'category': result['category'],
                            'source_data': {'images': []}  # 이미지 정보는 별도 처리 필요
                        }
                        successful_articles.append(article_data)
                        successful_files.append(article_file)
        
        # 일괄 GitHub 발행 (개별 발행하지 않은 경우)
        if not self.config.get('auto_publish', True) and successful_articles:
            logger.info("📤 일괄 GitHub 발행 시작")
            publish_result = self.github_publisher.publish_multiple_articles(
                successful_articles, 
                successful_files
            )
            self.stats['published_articles'] = len(publish_result.get('success', []))
        
        logger.info(f"✅ 일괄 처리 완료: 성공 {len([r for r in results if r['status'] == 'success'])}개")
        return results
    
    def discover_hwp_files(self, search_dir: str = None) -> List[str]:
        """
        🔍 HWP 파일 자동 검색
        
        Args:
            search_dir (str): 검색할 디렉토리 (기본값: 설정의 input_dir)
            
        Returns:
            List[str]: 발견된 HWP 파일 경로 리스트
        """
        if search_dir is None:
            search_dir = self.input_dir
        
        search_path = Path(search_dir)
        hwp_files = []
        
        try:
            logger.info(f"🔍 HWP 파일 검색: {search_path}")
            
            # 하위 디렉토리까지 재귀 검색
            for ext in self.config.get('supported_extensions', ['.hwp']):
                pattern = f"**/*{ext}"
                found_files = list(search_path.glob(pattern))
                hwp_files.extend([str(f) for f in found_files])
            
            # 중복 제거 및 정렬
            hwp_files = sorted(list(set(hwp_files)))
            
            logger.info(f"🔍 HWP 파일 발견: {len(hwp_files)}개")
            for file_path in hwp_files:
                logger.info(f"  📄 {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 파일 검색 실패: {e}")
        
        return hwp_files
    
    def generate_daily_summary(self) -> str:
        """
        📊 일일 처리 요약 생성
        """
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']
        
        summary = f"""
# 🌊 속초일보 AI 뉴스 시스템 일일 요약

**📅 처리 일시:** {self.stats['start_time'].strftime('%Y년 %m월 %d일 %H:%M')} - {end_time.strftime('%H:%M')}
**⏱️ 소요 시간:** {duration.total_seconds():.1f}초

## 📊 처리 통계
- **📄 처리한 HWP 파일:** {self.stats['processed_files']}개
- **📰 생성한 기사:** {self.stats['generated_articles']}개  
- **🚀 발행한 기사:** {self.stats['published_articles']}개
- **❌ 실패한 파일:** {self.stats['failed_files']}개

## 📈 성공률
- **전체 성공률:** {(self.stats['generated_articles'] / max(1, self.stats['processed_files']) * 100):.1f}%
- **발행 성공률:** {(self.stats['published_articles'] / max(1, self.stats['generated_articles']) * 100):.1f}%

"""
        
        if self.stats['errors']:
            summary += "## ❌ 오류 목록\n"
            for error in self.stats['errors']:
                summary += f"- **{error['file']}:** {error['error']}\n"
        
        summary += f"""
---
💬 **속초일보 AI 뉴스 시스템** | 발행인: 김도엽  
🌐 [sokchodaily.github.io](https://sokchodaily.github.io)
"""
        
        # 요약 파일 저장
        summary_file = f"daily_summary_{datetime.now().strftime('%Y%m%d')}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"📊 일일 요약 생성: {summary_file}")
        return summary
    
    def run_interactive_mode(self):
        """
        🎮 대화형 모드 실행
        """
        print("🌊 속초일보 AI 뉴스 시스템에 오신 것을 환영합니다! 😊")
        print("=" * 60)
        
        while True:
            print("\n📋 사용 가능한 명령:")
            print("1. 🔍 HWP 파일 자동 검색 및 처리")
            print("2. 📄 특정 HWP 파일 처리")
            print("3. 📊 현재 통계 확인") 
            print("4. 🚀 GitHub Pages 상태 확인")
            print("5. 📋 일일 요약 생성")
            print("6. ❌ 종료")
            
            choice = input("\n🎯 선택하세요 (1-6): ").strip()
            
            if choice == '1':
                hwp_files = self.discover_hwp_files()
                if hwp_files:
                    print(f"\n📚 {len(hwp_files)}개 파일을 처리하시겠습니까? (y/n): ", end="")
                    if input().lower() == 'y':
                        self.process_batch_hwp(hwp_files)
                else:
                    print("📄 HWP 파일을 찾을 수 없습니다.")
            
            elif choice == '2':
                file_path = input("📄 HWP 파일 경로를 입력하세요: ").strip()
                if Path(file_path).exists():
                    self.process_single_hwp(file_path)
                else:
                    print("❌ 파일을 찾을 수 없습니다.")
            
            elif choice == '3':
                print(f"\n📊 현재 통계:")
                print(f"  처리한 파일: {self.stats['processed_files']}개")
                print(f"  생성한 기사: {self.stats['generated_articles']}개")
                print(f"  발행한 기사: {self.stats['published_articles']}개")
                print(f"  실패한 파일: {self.stats['failed_files']}개")
            
            elif choice == '4':
                status = self.github_publisher.get_deployment_status()
                print(f"\n🚀 GitHub 상태:")
                print(f"  브랜치: {status.get('branch', 'Unknown')}")
                print(f"  마지막 커밋: {status.get('last_commit', {}).get('hash', 'Unknown')}")
                print(f"  변경사항: {status.get('pending_changes', 0)}개")
            
            elif choice == '5':
                summary = self.generate_daily_summary()
                print("\n📋 일일 요약이 생성되었습니다!")
                print(summary[:300] + "...")
            
            elif choice == '6':
                print("👋 속초일보 AI 뉴스 시스템을 종료합니다. 수고하셨습니다!")
                break
            
            else:
                print("❌ 잘못된 선택입니다. 1-6 중에서 선택해주세요.")


def main():
    """
    🚀 메인 실행 함수
    """
    parser = argparse.ArgumentParser(
        description="🌊 속초일보 AI 뉴스 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_ai_news.py                    # 대화형 모드
  python main_ai_news.py --auto             # 자동 검색 및 처리  
  python main_ai_news.py --file report.hwp # 특정 파일 처리
  python main_ai_news.py --dir ../보도자료  # 특정 폴더 처리
        """
    )
    
    parser.add_argument('--config', '-c', 
                       help='설정 파일 경로')
    parser.add_argument('--file', '-f',
                       help='처리할 특정 HWP 파일')
    parser.add_argument('--dir', '-d', 
                       help='HWP 파일을 검색할 디렉토리')
    parser.add_argument('--auto', '-a', action='store_true',
                       help='자동 검색 및 처리 모드')
    parser.add_argument('--no-publish', action='store_true',
                       help='GitHub 발행 건너뛰기')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='일일 요약만 생성')
    
    args = parser.parse_args()
    
    try:
        # AI 뉴스 시스템 초기화
        system = SokchoDailyAINewsSystem(config_path=args.config)
        
        # 발행 설정 오버라이드
        if args.no_publish:
            system.config['auto_publish'] = False
        
        # 명령 실행
        if args.summary:
            # 일일 요약만 생성
            summary = system.generate_daily_summary()
            print(summary)
            
        elif args.file:
            # 특정 파일 처리
            if Path(args.file).exists():
                result = system.process_single_hwp(args.file)
                print(f"✅ 처리 결과: {result}")
            else:
                print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
                
        elif args.auto or args.dir:
            # 자동 검색 및 처리
            search_dir = args.dir if args.dir else None
            hwp_files = system.discover_hwp_files(search_dir)
            
            if hwp_files:
                results = system.process_batch_hwp(hwp_files)
                summary = system.generate_daily_summary()
                print("\n" + summary)
            else:
                print("📄 처리할 HWP 파일을 찾을 수 없습니다.")
                
        else:
            # 대화형 모드
            system.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n👋 사용자가 중단했습니다.")
    except Exception as e:
        logger.error(f"❌ 시스템 실행 실패: {e}")
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 