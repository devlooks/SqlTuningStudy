## 1. DB Call 종류 및 개념

- Parse Call: SQL 해석, 실행계획 생성 (라이브러리 캐시에 없을 때 발생)
- Execute Call: SQL 실행(바인드 포함), 실제 작업 시작
- Fetch Call: Select 결과를 클라이언트로 전송 (Row/Array 단위)
- Recursive Call: 내부 SQL 호출 (View, 함수, Dictionary 조회 등)
- User Call: 애플리케이션 ↔ DB 간 SQL 요청 (네트워크 왕복 발생)

## 2. Parse Call 최소화 전략

- 바인드 변수 사용 → Cursor 공유
- SQL 재사용 캐시 → Parse 1회 제한
- View/함수 내부 다중 SQL → 병합 또는 SubQuery로 대체
- 사용자 함수 실행 시 하드파싱 주의

## 3. Execute Call 최적화

- 반복 SQL → Array Processing 적용
- One-SQL 통합 전략
- 함수 내부 반복 실행 방지
- 집합 처리 구조 설계

## 4. Fetch Call 최적화

- ArraySize 조정 → Call 수 감소
- Block 반복 읽기 주의 (OLTP 환경에서 비효율 가능)
- Cursor FOR LOOP 사용 시 자동 Array Fetch
- 페이징/부분 범위 처리 → User Call도 줄일 수 있음

## 5. Recursive Call 발생 조건 및 대안

- 사용자 함수 내부 SQL / View 내부 SQL / DUAL 테이블
- View → Join/SubQuery로 대체
- 바인드 변수 적용
- SELECT dummy FROM dual → Recursive Call 유발
- SELECT 1 FROM dual → 없음

## 6. User Call 최소화 전략

- SQL 호출 횟수 줄이기
- Array 처리
- PL/SQL 내 반복 호출 최소화
- 집합 처리 기반 One-SQL 설계

## 7. One-SQL 전략

- 조건 분기 → CASE, DECODE
- 사용자 함수 → Join, Scalar SubQuery로 대체
- 병합 방지 힌트: NO_MERGE, INLINE, MATERIALIZE

## 8. Array Processing

- PL/SQL Cursor FOR LOOP 자동 적용
- 고성능 집합 처리 유리 (단, 메모리 낭비 주의)
- ArraySize는 튜닝 대상 (과하면 I/O 비효율)

## 9. 사용자 함수 실행 조건별 반복 여부

| 위치 | 실행 횟수 기준 |
|------|----------------|
| SELECT | Row 수 만큼 반복 |
| WHERE | 인덱스/조건 종류 |
| JOIN ON | 조인 Row 수 만큼 |
| GROUP BY | 그룹 수 만큼 |
| HAVING | 그룹 수 만큼 |
| VIEW/WITH | 병합 시 반복 가능성 |

## 10. 함수 일관성 및 캐싱 전략

| 유형 | 캐싱 위치 | 특징 |
|------|-----------|------|
| Scalar SubQuery(Join) | PGA | 고성능, 일관성 우수 |
| Deterministic | PGA | 함수 결과 캐싱, 참조 테이블 주의 |
| Result Cache | SGA | 정적/읽기 전용 적합, 힌트 필요 |

캐싱 불가 대상: Dictionary, TEMP, SEQUENCE, SYSDATE 포함 등

## 11. Result Cache 활용

- 힌트 /*+ result_cache */
- SGA에 결과 저장, 자동 무효화
- 정적 코드/명칭 테이블 활용

## 12. DML / SELECT별 Call 차이

| 유형 | Parse | Execute | Fetch |
|------|--------|----------|--------|
| SELECT | O | O | O |
| DML(Insert/Update/Delete) | O | O | X |
| INSERT ... SELECT | O | O | O (SELECT 측 Fetch) |
| SELECT FOR UPDATE | O | O | O + TM Lock |

## 13. Fetch 최적화 방안

- ArraySize 조정
- Top-N 처리: ROWNUM, FETCH FIRST N ROWS
- 정렬 생략 가능 여부 확인
- Scalar SubQuery 적극 활용

## 14. PL/SQL 함수 성능 특징 및 해소

- Context Switching 비용
- SQL 포함 시 Recursive Call 발생
- 조건 분기 → CASE/DECODE
- Scalar SubQuery 대체
- 캐싱 힌트 사용: DETERMINISTIC, RESULT_CACHE

## 15. View Merging 방지 전략

| 병합 방지 대상 |
|----------------|
| 사용자 함수 |
| ROWNUM |
| DISTINCT |
| CONNECT BY |
| GROUP BY |
| RANK, ROW_NUMBER 등 분석 함수 |

힌트: NO_MERGE, INLINE, MATERIALIZE
