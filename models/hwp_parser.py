"""
🏗️ HWP 파일 파서 - 속초일보 AI 뉴스 시스템
HWP 파일에서 텍스트와 이미지를 추출하는 모듈

작성자: AI 시스템 for 김도엽 발행인
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# HWP 파싱을 위한 라이브러리들
try:
    import olefile
    from pyhwp import hwp5
    from pyhwp.hwp5 import storage
except ImportError as e:
    print(f"⚠️ HWP 처리 라이브러리가 없습니다: {e}")
    print("📦 설치 명령어: pip install pyhwp olefile")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hwp_parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HWPParser:
    """
    🔍 HWP 파일 파싱 클래스
    보도자료 HWP 파일에서 텍스트와 이미지를 추출합니다.
    """
    
    def __init__(self, hwp_file_path: str):
        """
        🎯 HWP 파서 초기화
        
        Args:
            hwp_file_path (str): HWP 파일 경로
        """
        self.hwp_file_path = Path(hwp_file_path)
        self.extracted_data = {
            'text': '',
            'images': [],
            'metadata': {},
            'title': '',
            'content': '',
            'press_release_info': {}
        }
        
        logger.info(f"📄 HWP 파서 초기화: {self.hwp_file_path}")
    
    def parse(self) -> Dict:
        """
        🔧 HWP 파일 전체 파싱
        
        Returns:
            Dict: 파싱된 데이터 (텍스트, 이미지, 메타데이터)
        """
        try:
            logger.info(f"🔍 HWP 파일 파싱 시작: {self.hwp_file_path}")
            
            # 파일 존재 확인
            if not self.hwp_file_path.exists():
                raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {self.hwp_file_path}")
            
            # 텍스트 추출
            self._extract_text()
            
            # 이미지 추출  
            self._extract_images()
            
            # 메타데이터 추출
            self._extract_metadata()
            
            # 보도자료 정보 파싱
            self._parse_press_release_info()
            
            logger.info(f"✅ HWP 파싱 완료: {len(self.extracted_data['text'])}자")
            return self.extracted_data
            
        except Exception as e:
            logger.error(f"❌ HWP 파싱 실패: {e}")
            raise
    
    def _extract_text(self) -> None:
        """
        📝 HWP 파일에서 텍스트 추출
        """
        try:
            # pyhwp를 사용한 텍스트 추출
            with hwp5.open(str(self.hwp_file_path)) as hwp_doc:
                # 본문 텍스트 추출
                text_parts = []
                
                for section in hwp_doc.bodytext.sections:
                    for paragraph in section.paragraphs():
                        for line in paragraph.text():
                            if line.strip():  # 빈 줄 제외
                                text_parts.append(line.strip())
                
                full_text = '\n'.join(text_parts)
                self.extracted_data['text'] = full_text
                
                # 제목 추출 (첫 번째 줄 또는 가장 큰 글씨)
                self.extracted_data['title'] = self._extract_title(text_parts)
                
                # 본문 추출 (제목 제외)
                self.extracted_data['content'] = self._extract_content(text_parts)
                
                logger.info(f"📝 텍스트 추출 완료: {len(full_text)}자")
                
        except Exception as e:
            logger.warning(f"⚠️ pyhwp 추출 실패, 대체 방법 시도: {e}")
            self._extract_text_fallback()
    
    def _extract_text_fallback(self) -> None:
        """
        📝 대체 텍스트 추출 방법 (olefile 사용)
        """
        try:
            if olefile.isOleFile(str(self.hwp_file_path)):
                ole = olefile.OleFileIO(str(self.hwp_file_path))
                
                # HWP 구조에서 텍스트 스트림 찾기
                for stream_name in ole.listdir():
                    if 'BodyText' in str(stream_name):
                        stream_data = ole.openstream(stream_name).read()
                        # 간단한 텍스트 추출 (완벽하지 않음)
                        text = stream_data.decode('utf-16le', errors='ignore')
                        self.extracted_data['text'] = self._clean_text(text)
                        break
                
                ole.close()
                logger.info("📝 대체 방법으로 텍스트 추출 완료")
                
        except Exception as e:
            logger.error(f"❌ 텍스트 추출 실패: {e}")
            self.extracted_data['text'] = "텍스트 추출에 실패했습니다."
    
    def _extract_images(self) -> None:
        """
        🖼️ HWP 파일에서 이미지 추출
        """
        try:
            images = []
            
            if olefile.isOleFile(str(self.hwp_file_path)):
                ole = olefile.OleFileIO(str(self.hwp_file_path))
                
                # 이미지 스트림 찾기
                for stream_name in ole.listdir():
                    stream_str = str(stream_name)
                    if 'BinData' in stream_str or 'Pictures' in stream_str:
                        try:
                            image_data = ole.openstream(stream_name).read()
                            
                            # 이미지 파일 저장
                            image_filename = f"extracted_image_{len(images)+1}.jpg"
                            image_path = self.hwp_file_path.parent / image_filename
                            
                            with open(image_path, 'wb') as img_file:
                                img_file.write(image_data)
                            
                            images.append({
                                'filename': image_filename,
                                'path': str(image_path),
                                'size': len(image_data)
                            })
                            
                        except Exception as img_error:
                            logger.warning(f"⚠️ 이미지 추출 오류: {img_error}")
                
                ole.close()
            
            self.extracted_data['images'] = images
            logger.info(f"🖼️ 이미지 추출 완료: {len(images)}개")
            
        except Exception as e:
            logger.error(f"❌ 이미지 추출 실패: {e}")
            self.extracted_data['images'] = []
    
    def _extract_metadata(self) -> None:
        """
        📊 HWP 파일 메타데이터 추출
        """
        try:
            metadata = {}
            
            # 파일 정보
            stat = self.hwp_file_path.stat()
            metadata.update({
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'filename': self.hwp_file_path.name
            })
            
            # HWP 문서 속성 (가능한 경우)
            try:
                with hwp5.open(str(self.hwp_file_path)) as hwp_doc:
                    if hasattr(hwp_doc, 'docinfo'):
                        docinfo = hwp_doc.docinfo
                        metadata.update({
                            'pages': getattr(docinfo, 'pages', 0),
                            'words': getattr(docinfo, 'words', 0),
                            'chars': getattr(docinfo, 'chars', 0)
                        })
            except:
                pass
            
            self.extracted_data['metadata'] = metadata
            logger.info("📊 메타데이터 추출 완료")
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 추출 실패: {e}")
            self.extracted_data['metadata'] = {}
    
    def _extract_title(self, text_parts: List[str]) -> str:
        """
        📰 문서에서 제목 추출
        """
        if not text_parts:
            return "제목 없음"
        
        # 첫 번째 줄을 제목으로 간주 (일반적인 보도자료 형식)
        title = text_parts[0] if text_parts else "제목 없음"
        
        # 제목 정리 (특수문자 제거, 길이 제한)
        title = re.sub(r'[^\w\s가-힣]', '', title).strip()
        if len(title) > 100:
            title = title[:100] + "..."
        
        return title or "제목 없음"
    
    def _extract_content(self, text_parts: List[str]) -> str:
        """
        📄 문서에서 본문 추출 (제목 제외)
        """
        if len(text_parts) <= 1:
            return self.extracted_data['text']
        
        # 제목 제외한 나머지를 본문으로
        content_parts = text_parts[1:]
        return '\n'.join(content_parts)
    
    def _parse_press_release_info(self) -> None:
        """
        📋 보도자료 정보 파싱 (발신기관, 담당자 등)
        """
        text = self.extracted_data['text']
        info = {}
        
        # 정규표현식으로 보도자료 정보 추출
        patterns = {
            'agency': r'(속초시|강원도|고성군|교육청|해양경찰서|문화재청).*?(?=\n|$)',
            'contact': r'담당.*?[:：]\s*([^\n]+)',
            'phone': r'전화.*?[:：]\s*([0-9-]+)',
            'date': r'(\d{4})[년.\-\/](\d{1,2})[월.\-\/](\d{1,2})'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                info[key] = match.group(1) if key != 'agency' else match.group(0)
        
        self.extracted_data['press_release_info'] = info
        logger.info("📋 보도자료 정보 파싱 완료")
    
    def _clean_text(self, text: str) -> str:
        """
        🧹 텍스트 정리 (불필요한 문자 제거)
        """
        # 제어 문자 제거
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        # 연속된 줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def save_extracted_data(self, output_dir: str = None) -> str:
        """
        💾 추출된 데이터를 JSON 파일로 저장
        
        Args:
            output_dir (str): 출력 디렉토리 (기본값: HWP 파일과 같은 폴더)
            
        Returns:
            str: 저장된 JSON 파일 경로
        """
        import json
        
        if output_dir is None:
            output_dir = self.hwp_file_path.parent
        
        output_path = Path(output_dir) / f"{self.hwp_file_path.stem}_extracted.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 추출 데이터 저장: {output_path}")
        return str(output_path)


def main():
    """
    🧪 HWP 파서 테스트 함수
    """
    # 테스트용 HWP 파일 경로 (실제 파일로 변경 필요)
    test_hwp_file = "../02_강원도/sample.hwp"  # 예시 경로
    
    if Path(test_hwp_file).exists():
        parser = HWPParser(test_hwp_file)
        result = parser.parse()
        
        print("🎉 HWP 파싱 결과:")
        print(f"📰 제목: {result['title']}")
        print(f"📝 텍스트 길이: {len(result['text'])}자")
        print(f"🖼️ 이미지 개수: {len(result['images'])}개")
        print(f"📊 메타데이터: {result['metadata']}")
        
        # JSON 파일로 저장
        parser.save_extracted_data()
    else:
        print(f"❌ 테스트 파일이 없습니다: {test_hwp_file}")


if __name__ == "__main__":
    main() 