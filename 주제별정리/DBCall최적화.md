
1. DB Call 종류
- Parse Call: SQL 해석, 실행계획 생성. Cursor 캐시에 없을 때 발생.
- Execute Call: SQL 실행 (바인드 변수 포함), 실제 DB 작업 시작 시점.
- Fetch Call: Select 결과를 클라이언트로 전송. Row 단위 또는 Array 단위.
- Recursive Call: 내부 SQL 호출 (Dictionary 조회, 함수 내 SQL, View 내부 SQL 등).
- User Call: 애플리케이션 ↔ DB 간 SQL 요청. 네트워크 왕복 발생.

2. Parse Call 최소화 전략
- 바인드 변수 사용 → Cursor 공유 가능
- 애플리케이션 SQL 캐시 활용 → Parse Call 1회로 제한
- 사용자 함수, 프로시저 자동 실행 시 Parse 발생 주의
- View, Inline SQL, PL/SQL 내 다중 SQL → 불필요한 Parse 방지 필요

3. Execute Call 최적화
- 반복 SQL 실행 시 → Array Processing으로 전환
- 함수 내부에서 반복 호출 시 Execute Call 급증 위험
- One-SQL 구조로 통합하여 Execute + User Call 모두 최소화

4. Fetch Call 최적화
- ArraySize 조정: Fetch Call 수를 줄이는 핵심
- ArraySize는 클수록 좋지만 블록 반복 읽기(Block I/O)로 성능 역효과 가능
- Cursor FOR LOOP 사용 시 자동 Array Fetch
- 페이징 처리, 부분 범위 처리와 함께 사용 시 User Call 대폭 감소

5. Recursive Call 발생 조건 및 대체 방안
- 사용자 정의 함수 내부 SQL, View 내부 SQL, DUAL 테이블 조회 시 발생
- Bind 변수 사용 또는 View → Join/SubQuery로 대체 가능
- Recursive Call이 많아지면 Parse, Execute Call까지 동반 증가

※ DUAL 테이블 예외
- SELECT 1 FROM dual → I/O 없음
- SELECT dummy FROM dual → Dictionary 조회 → Recursive Call 발생

6. User Call 최소화 전략
- SQL 호출 횟수 = User Call 발생 횟수
- 집합 처리로 다건 요청 병합 (One-SQL 활용)
- Array 단위 처리 적용
- PL/SQL 블록 내 반복 호출 지양

7. One-SQL 전략 (SQL 통합)
- 복수의 SQL을 하나로 통합
- 사용자 정의 함수 → Scalar SubQuery, Join, Inline View 대체
- 조건 분기 → CASE, DECODE
- 부하 분산 + 호출수 최소화 목적
- 뷰 병합 방지 힌트: NO_MERGE, INLINE, MATERIALIZE

8. Array Processing 설계
- PL/SQL: Cursor FOR LOOP 사용 시 Array 단위 처리 자동 적용
- 대용량 처리 시 효과 큼. 단, 메모리 낭비 주의
- ArraySize 설정 = 한번에 전송되는 Row 수

※ 유의사항:
- ArraySize가 크다고 무조건 효율 ↑ 아님 (Block 반복 읽기 고려)
- OLTP 환경 → Fetch가 ArraySize만큼 채울 때까지 대기 가능성 존재

9. 사용자 정의 함수 실행 조건 (보완 포함)
- SELECT 절: 결과 Row 수만큼 반복 실행
- WHERE 절: 인덱스 여부 및 등치/범위 여부에 따라 실행 횟수 달라짐
- JOIN ON 절: 조인 대상 Row 수만큼 반복 가능
- GROUP BY / ORDER BY 절: 그룹핑/정렬 Row 수만큼
- HAVING 절: 그룹 수만큼
- WITH 절 / VIEW 내부: 병합 시 반복 실행 위험 → NO_MERGE, MATERIALIZE 필요

※ 인덱스 + 함수 최적화 조건
- 인덱스 선두 컬럼 + 등치조건 → 1회 실행
- 인덱스 선두 컬럼 + 범위조건 → 옵티마이저 판단 또는 힌트 필요
- 인덱스 후행 컬럼 또는 미사용 시 → Table Access 수만큼 반복

10. 함수 일관성과 캐싱 전략
- Scalar SubQuery (조인): PGA, 일관성 우수
- Scalar SubQuery (단독): PGA, 입력값 적으면 효과, 많으면 비효율
- Deterministic 함수: PGA, 참조 테이블 변경 시 주의
- Result Cache: SGA, 힌트 필요, Latch 경합 가능

※ 캐싱 불가 대상
- Data Dictionary 객체
- TEMP 테이블
- SEQUENCE(NEXTVAL, CURRVAL)
- SYSDATE, SYSTIMESTAMP 포함 컬럼

11. Result Cache 활용법
- 힌트 /*+ result_cache */ 필요
- 결과 변경 시 자동 무효화
- 읽기 전용/정적 데이터에 적합
- 코드 테이블, 명칭 테이블에 효과적

12. DML / SELECT별 Call 차이
- INSERT/UPDATE/DELETE: Fetch Call 없음
- INSERT ... SELECT: SELECT 측에서 Fetch 발생
- SELECT: Execute + Fetch Call 발생
- SELECT FOR UPDATE: Execute + TM Lock 발생

13. Fetch 최적화 방안
- ArraySize 증가 → Fetch Call 수 감소
- Top-N 처리: ROWNUM, FETCH FIRST N ROWS 사용
- 정렬/소팅 생략 가능 시 성능 향상
- 함수 외부 분리, Scalar SubQuery로 대체

14. PL/SQL 함수 성능 특징
- 실행: 컴파일 → 바이트코드 → 인터프리터
- SQL ↔ PL/SQL 간 Context Switching 비용 발생
- 함수 내 SQL 포함 시 Recursive Call 동반

15. PL/SQL 함수 해소 및 최적화
- 조건 분기: CASE, DECODE로 SQL 내 처리
- 함수 → Scalar SubQuery 또는 조인으로 변환
- Deterministic, Result Cache 사용 가능
- 외부 함수 호출 SQL 밖으로 이동

16. 뷰 머징(View Merging) 방지 전략
- 사용자 정의 함수, ROWNUM, DISTINCT, CONNECT BY, GROUP BY, ROW_NUMBER, RANK 병합 방지 대상
- 힌트: NO_MERGE, INLINE, MATERIALIZE
- 목적: 함수 중복 실행 방지, 캐시 유도, 최적 실행 계획 유지
