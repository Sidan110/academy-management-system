# EduManager - Docker Compose 기반 소규모 학원 관리 시스템

EduManager는 소규모 학원에서 학생, 수업반, 수강 등록, 진도, 출석, 상담 예약, 수납 상태를 통합 관리하기 위한 웹 애플리케이션입니다.

본 프로젝트는 Django, PostgreSQL, Nginx, Docker Compose 구조를 사용하여 사용자의 요청이 웹 서버, 백엔드, 데이터베이스로 이어지는 전체 흐름을 이해하고 구현하는 것을 목표로 합니다.

## 사용 기술

- Django 4.2.7
- PostgreSQL 15.4
- Nginx 1.25.3
- Gunicorn
- Docker Compose
- HTML
- CSS
- JavaScript

## 시스템 구조

사용자 브라우저 -> Nginx 컨테이너 -> Django/Gunicorn 컨테이너 -> PostgreSQL 컨테이너

- 사용자는 http://localhost:8080 으로 접속합니다.
- Nginx는 사용자의 요청을 먼저 받습니다.
- CSS, JavaScript 같은 정적 파일 요청은 Nginx가 직접 처리합니다.
- 일반 웹 요청은 Gunicorn을 통해 Django로 전달됩니다.
- Django는 URL, View, Form, Model을 이용해 요청을 처리합니다.
- PostgreSQL은 학생, 수업반, 출석, 진도, 상담, 수납 데이터를 저장합니다.

## 주요 기능

### 원장 기능

- 대시보드 조회
- 학생 등록, 조회, 수정, 삭제
- 수업반 등록, 조회, 수정, 삭제
- 학생 수강 등록
- 방문상담 예약 관리
- 수납 청구서 생성
- 미납, 부분납, 완납, 연체 상태 관리
- 알림 발송 로그 관리

### 교사 기능

- 학생 조회
- 수업반 조회
- 진도 기록
- 출석 체크
- 출석 현황 조회

### 외부 사용자 기능

- 학부모 비회원 방문상담 예약 신청
- 학생 직접 출석 체크

## 테스트 계정

| 역할 | 아이디 | 비밀번호 |
|---|---|---|
| 원장 | owner | owner1234 |
| 교사 | teacher | teacher1234 |

## 실행 방법

1. 저장소를 복제합니다.

    git clone https://github.com/Sidan110/academy-management-system.git

2. 프로젝트 폴더로 이동합니다.

    cd academy-management-system

3. 환경변수 예시 파일을 복사합니다.

    cp .env.example .env

4. Docker Compose로 실행합니다.

    docker compose up -d --build

5. 브라우저에서 접속합니다.

    http://localhost:8080

## 종료 방법

    docker compose down

주의: 아래 명령어는 PostgreSQL 데이터 볼륨까지 삭제하므로 일반 종료 시 사용하지 않습니다.

    docker compose down -v

## 주요 URL

| 기능 | URL |
|---|---|
| 로그인 | /login/ |
| 대시보드 | / |
| 학생 관리 | /students/ |
| 수업반 관리 | /classes/ |
| 수강 등록 | /enrollments/ |
| 진도 기록 | /progress/ |
| 출석 체크 | /attendance/ |
| 출석 현황 | /attendance/report/ |
| 방문상담 관리 | /consultations/ |
| 학부모 상담 신청 | /apply/ |
| 수납 관리 | /payments/ |
| 알림 로그 | /notifications/ |
| 학생 직접 출석 체크 | /checkin/ |

## 권한 구조

본 프로젝트는 원장과 교사 계정을 구분합니다.

- 원장은 학생, 수업반, 수강 등록, 상담, 수납, 알림 로그 등 전체 기능에 접근할 수 있습니다.
- 교사는 학생 조회, 수업반 조회, 진도 기록, 출석 체크 중심으로 접근할 수 있습니다.
- 교사가 수납 관리와 같은 원장 전용 페이지에 접근하면 권한 제한 화면이 출력됩니다.

## 프로젝트 특징

이 프로젝트는 게시판 예제의 Post/Comment 구조를 단순히 변경한 것이 아니라, 학원 운영 도메인에 맞춰 학생, 수업반, 수강 등록, 진도, 출석, 상담 예약, 수납 청구서, 알림 로그 기능을 구성했습니다.

또한 Nginx가 정적 파일을 직접 제공하고, 일반 웹 요청은 Gunicorn을 통해 Django로 전달하도록 구성하여 Docker Compose 기반 웹 서비스의 전체 동작 흐름을 확인할 수 있도록 했습니다.

## 향후 개선 방향

- AWS EC2 배포
- HTTPS 적용
- 실제 SMS 또는 카카오 알림톡 API 연동
- 학부모용 조회 페이지 추가
- 성적 관리 기능 추가
- UI/UX 개선
