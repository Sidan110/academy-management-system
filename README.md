# EduManager - 소규모 학원 관리 시스템

Docker Compose 기반 Django + PostgreSQL + Nginx 웹 애플리케이션입니다.

## 사용 기술

- Django
- PostgreSQL
- Nginx
- Docker Compose
- HTML
- CSS
- JavaScript

## 주요 기능

- 대시보드
- 학생 등록 / 조회 / 수정 / 삭제
- 수업반 등록 / 조회 / 수정 / 삭제
- 학생을 수업반에 배정하는 수강 등록
- 학생별 진도 기록
- 수업반별 출석 체크

## 실행 방법

1. 저장소를 다운로드합니다.

git clone 저장소주소

2. 프로젝트 폴더로 이동합니다.

cd academy-management-system

3. Docker Compose로 실행합니다.

docker compose up -d --build

4. 브라우저에서 접속합니다.

http://localhost:8080

## 종료 방법

docker compose down

## 데이터 유지

PostgreSQL 데이터는 Docker volume에 저장되므로 docker compose down 후 다시 실행해도 데이터가 유지됩니다.

단, docker compose down -v 명령어를 사용하면 volume이 삭제되어 DB 데이터가 초기화됩니다.
