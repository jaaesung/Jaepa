# 빌드 스테이지
FROM node:18-alpine as build

WORKDIR /app

# 패키지 파일 복사 및 의존성 설치
COPY package.json package-lock.json ./
RUN npm ci

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# 실행 스테이지
FROM nginx:alpine

# Nginx 설정 파일 복사
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# 빌드 결과물을 Nginx로 복사
COPY --from=build /app/build /usr/share/nginx/html

# 포트 노출
EXPOSE 80

# 실행 명령
CMD ["nginx", "-g", "daemon off;"]
