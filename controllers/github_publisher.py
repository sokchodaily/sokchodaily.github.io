"""
🚀 GitHub Pages 자동 발행 시스템 - 속초일보 AI 뉴스 시스템
완성된 기사를 GitHub Pages에 자동으로 커밋하고 배포

작성자: AI 시스템 for 김도엽 발행인
"""

import os
import sys
import logging
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import shutil

# Git 관련
try:
    import git
except ImportError:
    print("⚠️ GitPython 라이브러리가 없습니다: pip install GitPython")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_publisher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GitHubPublisher:
    """
    📤 GitHub Pages 발행 클래스
    완성된 기사를 GitHub 리포지토리에 자동 커밋하고 배포합니다.
    """
    
    def __init__(self, repo_path: str = ".", branch: str = "main"):
        """
        🎯 GitHub 발행기 초기화
        
        Args:
            repo_path (str): Git 리포지토리 경로
            branch (str): 배포할 브랜치명 (기본값: main)
        """
        self.repo_path = Path(repo_path).resolve()
        self.branch = branch
        
        try:
            self.repo = git.Repo(self.repo_path)
            logger.info(f"📂 Git 리포지토리 연결: {self.repo_path}")
        except git.exc.InvalidGitRepositoryError:
            logger.error("❌ Git 리포지토리가 아닙니다. git init을 먼저 실행하세요.")
            raise
        except Exception as e:
            logger.error(f"❌ Git 연결 실패: {e}")
            raise
        
        # 배포 설정
        self.deploy_config = {
            'auto_push': True,
            'commit_message_template': '🤖 AI 기사 자동 발행: {title}',
            'max_files_per_commit': 10,
            'backup_before_push': True
        }
        
        logger.info("🚀 GitHub 발행기 초기화 완료")
    
    def publish_article(self, article_data: Dict, article_file_path: str) -> bool:
        """
        📰 단일 기사 발행
        
        Args:
            article_data (Dict): 기사 데이터
            article_file_path (str): 기사 파일 경로
            
        Returns:
            bool: 발행 성공 여부
        """
        try:
            logger.info(f"📰 기사 발행 시작: {article_data['title']}")
            
            # 1. 파일 상태 확인
            if not Path(article_file_path).exists():
                raise FileNotFoundError(f"기사 파일을 찾을 수 없습니다: {article_file_path}")
            
            # 2. 이미지 파일 처리 (있는 경우)
            image_files = self._process_article_images(article_data)
            
            # 3. Git에 파일 추가
            files_to_add = [article_file_path] + image_files
            self._add_files_to_git(files_to_add)
            
            # 4. 커밋 생성
            commit_message = self.deploy_config['commit_message_template'].format(
                title=article_data['title'][:50]
            )
            commit_hash = self._create_commit(commit_message)
            
            # 5. GitHub에 푸시 (설정된 경우)
            if self.deploy_config['auto_push']:
                self._push_to_github()
            
            logger.info(f"✅ 기사 발행 완료: {commit_hash}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 기사 발행 실패: {e}")
            return False
    
    def publish_multiple_articles(self, articles: List[Dict], article_files: List[str]) -> Dict:
        """
        📰 여러 기사 일괄 발행
        
        Args:
            articles (List[Dict]): 기사 데이터 리스트
            article_files (List[str]): 기사 파일 경로 리스트
            
        Returns:
            Dict: 발행 결과 요약
        """
        try:
            logger.info(f"📚 일괄 발행 시작: {len(articles)}개 기사")
            
            results = {
                'success': [],
                'failed': [],
                'total_files': 0,
                'commit_hash': None
            }
            
            all_files_to_add = []
            successful_articles = []
            
            # 각 기사 처리
            for i, (article, file_path) in enumerate(zip(articles, article_files)):
                try:
                    if Path(file_path).exists():
                        # 이미지 파일 처리
                        image_files = self._process_article_images(article)
                        
                        # 파일 목록에 추가
                        all_files_to_add.extend([file_path] + image_files)
                        successful_articles.append(article)
                        results['success'].append(article['title'])
                        
                    else:
                        logger.warning(f"⚠️ 파일 없음: {file_path}")
                        results['failed'].append(article['title'])
                        
                except Exception as e:
                    logger.error(f"❌ 기사 처리 실패: {article['title']} - {e}")
                    results['failed'].append(article['title'])
            
            # Git에 모든 파일 추가
            if all_files_to_add:
                self._add_files_to_git(all_files_to_add)
                results['total_files'] = len(all_files_to_add)
                
                # 커밋 메시지 생성
                commit_message = f"🤖 AI 뉴스 일괄 발행: {len(successful_articles)}개 기사 업데이트"
                if len(successful_articles) > 0:
                    first_title = successful_articles[0]['title'][:30]
                    commit_message += f" (대표: {first_title}...)"
                
                # 커밋 생성
                commit_hash = self._create_commit(commit_message)
                results['commit_hash'] = commit_hash
                
                # GitHub에 푸시
                if self.deploy_config['auto_push']:
                    self._push_to_github()
            
            logger.info(f"✅ 일괄 발행 완료: 성공 {len(results['success'])}개, 실패 {len(results['failed'])}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ 일괄 발행 실패: {e}")
            raise
    
    def _process_article_images(self, article_data: Dict) -> List[str]:
        """
        🖼️ 기사 이미지 파일 처리
        """
        image_files = []
        
        try:
            source_images = article_data.get('source_data', {}).get('images', [])
            
            for image_info in source_images:
                source_path = Path(image_info['path'])
                
                if source_path.exists():
                    # 이미지를 assets/images/ 폴더로 복사
                    target_dir = self.repo_path / 'assets' / 'images'
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 파일명 생성 (날짜 + 원본명)
                    date_prefix = datetime.now().strftime("%Y%m%d")
                    target_filename = f"{date_prefix}_{source_path.name}"
                    target_path = target_dir / target_filename
                    
                    # 파일 복사
                    shutil.copy2(source_path, target_path)
                    image_files.append(str(target_path.relative_to(self.repo_path)))
                    
                    logger.info(f"🖼️ 이미지 복사: {target_filename}")
        
        except Exception as e:
            logger.warning(f"⚠️ 이미지 처리 실패: {e}")
        
        return image_files
    
    def _add_files_to_git(self, file_paths: List[str]) -> None:
        """
        📁 Git에 파일 추가
        """
        try:
            # 파일 경로를 상대 경로로 변환
            relative_paths = []
            for file_path in file_paths:
                if Path(file_path).is_absolute():
                    rel_path = Path(file_path).relative_to(self.repo_path)
                else:
                    rel_path = Path(file_path)
                relative_paths.append(str(rel_path))
            
            # Git에 파일 추가
            self.repo.index.add(relative_paths)
            logger.info(f"📁 Git에 파일 추가: {len(relative_paths)}개")
            
        except Exception as e:
            logger.error(f"❌ Git 파일 추가 실패: {e}")
            raise
    
    def _create_commit(self, message: str) -> str:
        """
        💾 Git 커밋 생성
        """
        try:
            # 변경사항 확인
            if not self.repo.index.diff("HEAD"):
                logger.warning("⚠️ 변경사항이 없어 커밋을 생략합니다.")
                return ""
            
            # 커밋 생성
            commit = self.repo.index.commit(message)
            commit_hash = commit.hexsha[:8]
            
            logger.info(f"💾 커밋 생성: {commit_hash} - {message}")
            return commit_hash
            
        except Exception as e:
            logger.error(f"❌ 커밋 생성 실패: {e}")
            raise
    
    def _push_to_github(self) -> None:
        """
        🚀 GitHub에 푸시
        """
        try:
            # 원격 리포지토리 확인
            if not self.repo.remotes:
                logger.warning("⚠️ 원격 리포지토리가 설정되지 않았습니다.")
                return
            
            # origin 리모트 확인
            origin = self.repo.remotes.origin
            
            # 푸시 실행
            logger.info(f"🚀 GitHub에 푸시 시작: {self.branch} 브랜치")
            push_info = origin.push(self.branch)
            
            # 푸시 결과 확인
            for info in push_info:
                if info.flags & info.ERROR:
                    raise Exception(f"푸시 오류: {info.summary}")
                elif info.flags & info.REJECTED:
                    raise Exception("푸시 거부됨 (충돌 가능성)")
            
            logger.info("✅ GitHub 푸시 완료")
            
        except Exception as e:
            logger.error(f"❌ GitHub 푸시 실패: {e}")
            raise
    
    def deploy_site_updates(self) -> bool:
        """
        🌐 웹사이트 전체 업데이트 배포
        """
        try:
            logger.info("🌐 웹사이트 전체 업데이트 시작")
            
            # Jekyll 설정 파일들 확인
            config_files = [
                '_config.yml',
                'index.md',
                '_layouts/default.html',
                '_layouts/post.html'
            ]
            
            missing_files = []
            for config_file in config_files:
                file_path = self.repo_path / config_file
                if not file_path.exists():
                    missing_files.append(config_file)
            
            if missing_files:
                logger.warning(f"⚠️ 누락된 설정 파일: {missing_files}")
            
            # 모든 변경사항 추가
            self.repo.git.add(A=True)
            
            # 커밋 생성
            commit_message = f"🌐 속초일보 웹사이트 업데이트 - {datetime.now().strftime('%Y.%m.%d %H:%M')}"
            commit_hash = self._create_commit(commit_message)
            
            # GitHub에 푸시
            if self.deploy_config['auto_push']:
                self._push_to_github()
            
            logger.info(f"✅ 웹사이트 업데이트 완료: {commit_hash}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 웹사이트 업데이트 실패: {e}")
            return False
    
    def create_backup(self) -> str:
        """
        💾 현재 상태 백업
        """
        try:
            backup_dir = self.repo_path / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = backup_dir / backup_name
            
            # 현재 브랜치 백업
            current_branch = self.repo.active_branch.name
            self.repo.git.checkout('-b', backup_name)
            self.repo.git.checkout(current_branch)
            
            logger.info(f"💾 백업 생성: {backup_name}")
            return backup_name
            
        except Exception as e:
            logger.error(f"❌ 백업 생성 실패: {e}")
            return ""
    
    def get_deployment_status(self) -> Dict:
        """
        📊 배포 상태 확인
        """
        try:
            status = {
                'branch': self.repo.active_branch.name,
                'last_commit': {
                    'hash': self.repo.head.commit.hexsha[:8],
                    'message': self.repo.head.commit.message.strip(),
                    'date': datetime.fromtimestamp(self.repo.head.commit.committed_date).isoformat()
                },
                'pending_changes': len(self.repo.index.diff(None)),
                'untracked_files': len(self.repo.untracked_files),
                'remote_url': str(self.repo.remotes.origin.url) if self.repo.remotes else None,
                'is_dirty': self.repo.is_dirty()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ 배포 상태 확인 실패: {e}")
            return {}
    
    def setup_github_pages(self) -> bool:
        """
        ⚙️ GitHub Pages 초기 설정
        """
        try:
            logger.info("⚙️ GitHub Pages 설정 시작")
            
            # GitHub Pages 설정을 위한 CNAME 파일 생성 (커스텀 도메인 사용시)
            # cname_path = self.repo_path / 'CNAME'
            # if not cname_path.exists():
            #     with open(cname_path, 'w') as f:
            #         f.write('sokchodaily.com')  # 실제 도메인으로 변경
            
            # .nojekyll 파일 확인 (필요시)
            nojekyll_path = self.repo_path / '.nojekyll'
            if not nojekyll_path.exists():
                nojekyll_path.touch()
                logger.info("📄 .nojekyll 파일 생성")
            
            # README.md 파일 생성
            readme_path = self.repo_path / 'README.md'
            if not readme_path.exists():
                readme_content = """# 속초일보 AI 뉴스 시스템

🌊 바다와 산이 만나는 속초의 모든 이야기를 AI가 자동으로 전달합니다.

## 🤖 시스템 특징
- 보도자료 HWP 파일 자동 파싱
- AI 기반 기사 자동 작성
- GitHub Pages 자동 배포
- 속초일보 스타일 맞춤 포맷팅

## 🌐 웹사이트
[속초일보 공식 사이트](https://sokchodaily.github.io)

---
발행인: 김도엽 | 속초일보 | 강원, 아00263
"""
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                logger.info("📄 README.md 생성")
            
            logger.info("✅ GitHub Pages 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ GitHub Pages 설정 실패: {e}")
            return False


def main():
    """
    🧪 GitHub 발행기 테스트 함수
    """
    try:
        # 발행기 초기화
        publisher = GitHubPublisher()
        
        # 배포 상태 확인
        status = publisher.get_deployment_status()
        print("📊 현재 배포 상태:")
        print(f"브랜치: {status.get('branch', 'Unknown')}")
        print(f"마지막 커밋: {status.get('last_commit', {}).get('hash', 'Unknown')}")
        print(f"변경사항: {status.get('pending_changes', 0)}개")
        
        # GitHub Pages 설정
        publisher.setup_github_pages()
        
        print("✅ GitHub 발행기 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")


if __name__ == "__main__":
    main() 