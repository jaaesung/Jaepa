#!/bin/bash

# 현재 디렉토리로 이동
cd /Users/baejaeseung/2025_Project/jaepa

# 변경된 파일 확인
echo "변경된 파일 목록:"
git status -s

# 커밋 메시지 파일에서 내용 가져오기
COMMIT_MSG=$(cat news_sources_api_commit_message.txt)

# 모든 변경 사항 스테이징
git add .

# 커밋 수행
git commit -m "$COMMIT_MSG"

# 푸시 명령어 (원격 저장소가 설정된 경우 사용)
# git push origin main
