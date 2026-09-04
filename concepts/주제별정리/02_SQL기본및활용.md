
# SQL 기본 및 활용 - 통합 정리본

## ✅ 1. SQL 명령어 분류

| 분류 | 명령어 | 설명 |
|------|--------|------|
| **DML** | SELECT, INSERT, UPDATE, DELETE | 데이터 조작어 (데이터 조회 및 수정) |
| **DDL** | CREATE, ALTER, DROP, RENAME | 데이터 정의어 (객체 생성 및 구조 변경) |
| **DCL** | GRANT, REVOKE | 권한 부여 및 회수 |
| **TCL** | COMMIT, ROLLBACK, SAVEPOINT | 트랜잭션 제어어 (일괄 처리 단위 관리) |

※ `DROP`, `TRUNCATE`는 DDL → **자동 COMMIT 발생**, ROLLBACK 불가

## ✅ 2. WHERE절과 집계 함수, NULL 처리

- `WHERE절`에서는 **집계 함수 사용 불가** → `HAVING` 사용
- `NULL` 연산:
  - NULL + 사칙연산 → `NULL`
  - NULL + 비교연산 → `FALSE`
  - NULL은 어떤 값과도 **직접 비교 불가** (`IS NULL`, `IS NOT NULL` 사용)
- 오라클에서 `''` (빈 문자열) 입력 → `NULL`
- SQL Server는 `''` 그대로 빈 문자열로 인식

## ✅ 3. Group by / 집계 함수 주의사항

- `GROUP BY NULL` → 불가 (NULL은 그룹핑 대상 아님)
- `GROUP BY ALIAS` → 별칭은 `GROUP BY`에서 사용 불가 (컬럼명 사용)
- `집계 함수 + WHERE` → ❌ (`HAVING` 사용해야 함)

## ✅ 4. 날짜/시간 연산 (Oracle 기준)

- 날짜 + 숫자 → `일(day)` 단위 연산
  - `1/24` = 1시간, `1/24/60` = 1분, `1/24/(60/10)` = 10분
- 오라클 `SYSDATE`, SQL Server `GETDATE()`

## ✅ 5. NULL 관련 함수

| 함수 | 설명 |
|------|------|
| `NVL(A, B)` | A가 NULL이면 B 반환 |
| `NULLIF(A, B)` | A = B → NULL 반환, 다르면 A |
| `COALESCE(A, B, C, …)` | 처음으로 NULL이 아닌 값 반환 |

## ✅ 6. 문자열 함수

- `SUBSTR('문자열', 8, 4)` → 8번째 문자부터 4개 추출
- `TRIM(문자)` → 양쪽 문자 제거
- `LTRIM` / `RTRIM` → 앞/뒤 문자 제거  
  ※ SQL Server는 `LTRIM`, `RTRIM`에서 특정 문자 제거 불가 (공백만 가능)

## ✅ 7. 비교 연산자 / 조인

- **Non-equi Join**: `<>`, `>`, `<` 등 비교 연산으로 조인
- 순수 관계 연산자: `SELECT`, `PROJECT`, `JOIN`, `DIVIDE`
- 조인 종류: `INNER JOIN`, `USING`, `NATURAL JOIN`

## ✅ 8. 집합 연산자

- `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`
- 순서대로 위에서 아래로 실행됨
- `UNION`: 중복 제거 / `UNION ALL`: 중복 허용

```sql
SELECT * FROM A
UNION ALL
SELECT * FROM B
```

## ✅ 9. 계층형 질의 (Hierarchical Query)

### ◾ Oracle

- `START WITH ... CONNECT BY PRIOR`
- `LEVEL`: 루트 노드부터 1로 시작
- `START WITH` 값은 결과 집합에 포함됨
- `WHERE` → 먼저 필터 조건 적용, 그 후 계층 구성

### ◾ SQL Server

- `CTE(Common Table Expression)` + `RECURSIVE`
- `ANCHOR MEMBER` → 초기 집합
- `RECURSIVE MEMBER` → 반복적으로 실행하여 계층 구성

## ✅ 10. 윈도우 함수 (Window Function)

- `PARTITION BY` → 그룹핑 유사, 단 `GROUP BY`처럼 줄이지 않음
- **윈도우는 파티션을 넘어가지 않음**

| 함수 | 설명 |
|------|------|
| `RANK()` | 동일 순위 → 이후 순위 건너뜀 |
| `DENSE_RANK()` | 동일 순위 → 이후 순위 건너뛰지 않음 |
| `ROW_NUMBER()` | 유일한 순위 |
| `LEAD()` | 다음 행 참조 |
| `LAG()` | 이전 행 참조 |
| `NTILE(N)` | N등분하여 순서 부여 |
| `CUME_DIST()` | 누적 백분율 |
| `PERCENT_RANK()` | 0~1 백분율 순위 |
| `RATIO_TO_REPORT()` | 전체 합 대비 행 비율 |

※ `ORDER BY` + 윈도우 함수 가능  
※ `GROUP BY` + 윈도우 함수도 병행 가능

## ✅ 11. 집계 함수의 확장: ROLLUP / CUBE / GROUPING SETS

| 유형 | 설명 |
|------|------|
| `ROLLUP(A, B)` | A→B로 점진적 그룹핑 |
| `CUBE(A, B)` | A, B 모든 조합 집계 |
| `GROUPING SETS((A), (B))` | 선택적 그룹 집계 |

## ✅ 12. Inline View

- **FROM 절**에 `SELECT` 결과를 임시 테이블처럼 활용하는 동적 뷰

## ✅ 13. 제약조건 및 키

| 구분 | 설명 |
|------|------|
| PRIMARY KEY | 유일 + NOT NULL |
| FOREIGN KEY | 외래키, 참조 무결성 |
| UNIQUE | 유일하지만 NULL 허용 |
| CHECK | 지정 조건 만족 |
| NOT NULL | NULL 입력 불가 |

### ◾ 제약조건 작성 예시

```sql
CREATE TABLE Tname (
  prod_id NUMBER,
  CONSTRAINT pk_prod PRIMARY KEY(prod_id)
);

ALTER TABLE Tname ADD CONSTRAINT pk_name PRIMARY KEY(prod_id);
```

## ✅ 14. 외래키 참조 옵션

| 옵션 | 동작 |
|------|------|
| CASCADE | 부모 삭제 시 자식도 삭제 |
| SET NULL | 부모 삭제 시 자식 NULL 처리 |
| SET DEFAULT | 부모 삭제 시 기본값 설정 |
| RESTRICT / NO ACTION | 자식 존재 시 부모 삭제 불가 |

## ✅ 15. 권한 부여 / 회수

- `WITH GRANT OPTION` → 권한을 **다른 사용자에게 재부여 가능**
- `REVOKE WITH GRANT OPTION` → 권한 회수 시 **연쇄적으로 회수**

## ✅ 16. MERGE 문

```sql
MERGE INTO t1 a
USING t2 b
ON (a.key = b.key)
WHEN MATCHED THEN UPDATE ...
WHEN NOT MATCHED THEN INSERT ...
```

## ✅ 17. 컬럼/테이블 수정

- 컬럼 삭제:  
  `ALTER TABLE emp DROP COLUMN comm;`
- 테이블 컬럼 수정:
  ```sql
  ALTER TABLE 기관분류 
    MODIFY (분류명 VARCHAR2(30) NOT NULL,
            등록일자 DATE NOT NULL);
  ```
  ※ SQL Server는 다중 컬럼 변경 불가

## ✅ 18. DROP / DELETE / TRUNCATE 비교

| 명령어 | 유형 | ROLLBACK | 설명 |
|--------|------|----------|------|
| DELETE | DML | 가능 | 조건부 삭제, 트리거 작동 |
| TRUNCATE | DDL | 불가 | 전체 삭제, 성능 좋음 |
| DROP | DDL | 불가 | 객체 자체 삭제 |

## ✅ 19. 트랜잭션의 ACID 특성

| 항목 | 설명 |
|------|------|
| Atomicity | 전부 실행 or 전부 실패 |
| Consistency | 일관성 유지 |
| Isolation | 트랜잭션 간 간섭 없음 |
| Durability | 영구적 반영 |

## ✅ 20. 기타

- `WITH TIES`: TOP N에서 동일 순위가 있는 경우 모두 출력
- 산술 연산자 우선순위: `() > ** > *, / > +, -`
- 테이블 명명 규칙:
  - 의미 있는 단수형 이름
  - 예약어 및 중복 명 피하기
