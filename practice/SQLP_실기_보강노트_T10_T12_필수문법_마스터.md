# SQLP 실기 보강노트: T10~T12 필수 문법 마스터 (Pre-초급 훈련용)

- **목적:** SQLP 실기 T10(DML/DDL), T11(DB Call), T12(Lock/동시성) 영역에서 반드시 백지상태로 작성할 수 있어야 하는 핵심 DDL/DML 문법 총정리
- **활용:** [Pre-초급] 단계에서 본 문서의 템플릿을 메모장에 3~5회 손코딩(블라인드 타이핑)하여 머슬 메모리 구축

---

## 📦 [T10] DML / Batch / DDL (대용량 데이터 처리)

### 1. CTAS 5단계 표준 절차 (대량 삭제/복제)
대량의 데이터를 지우거나 복제할 때 Undo/Redo를 제거하고 가장 빠르게 처리하는 정석 절차.

```sql
-- [Step 1] 데이터 복제 (NOLOGGING + PARALLEL 4 필수)
CREATE TABLE 임시테이블 NOLOGGING PARALLEL 4
AS 
SELECT /*+ FULL(A) PARALLEL(A 4) */ * 
FROM   원본테이블 A 
WHERE  조건;

-- [Step 2] PK 및 일반 인덱스 후속 일괄 빌드 (데이터 적재 후 생성해야 Index Split 방지)
CREATE UNIQUE INDEX PK_임시_명칭 ON 임시테이블 (PK컬럼1, PK컬럼2) NOLOGGING PARALLEL 4;
ALTER TABLE 임시테이블 ADD CONSTRAINT PK_임시_명칭 PRIMARY KEY (PK컬럼1, PK컬럼2) USING INDEX PK_임시_명칭;

CREATE INDEX IX_임시_명칭 ON 임시테이블 (일반컬럼1, 일반컬럼2) NOLOGGING PARALLEL 4;

-- [Step 3] 원본 파괴 (공간 즉시 반환을 위해 PURGE 필수)
DROP TABLE 원본테이블 PURGE;

-- [Step 4] RENAME 원복 (테이블과 인덱스 모두 이름 원복)
RENAME 임시테이블 TO 원본테이블;
ALTER INDEX PK_임시_명칭 RENAME TO PK_원본_명칭;
ALTER INDEX IX_임시_명칭 RENAME TO IX_원본_명칭;

-- [Step 5] 서비스 정상화 릴리즈 (가장 중요! 로깅 복구 및 병렬도 해제)
ALTER TABLE 원본테이블 LOGGING NOPARALLEL;
ALTER INDEX PK_원본_명칭 LOGGING NOPARALLEL;
ALTER INDEX IX_원본_명칭 LOGGING NOPARALLEL;
```

### 2. 파티션 교체 (EXCHANGE PARTITION) 및 사전 인덱스 매핑
파티션 교체 시 로컬 인덱스가 `UNUSABLE`로 깨지는 것을 막기 위한 문법.

```sql
-- [사전 준비] 파티션 테이블에 로컬 PK와 로컬 일반 인덱스가 있다면, 스테이징 테이블에도 1:1로 미리 생성!
CREATE UNIQUE INDEX PK_스테이징테이블 ON 스테이징테이블 (PK컬럼1, PK컬럼2);
ALTER TABLE 스테이징테이블 ADD CONSTRAINT PK_스테이징테이블 PRIMARY KEY (PK컬럼1, PK컬럼2) USING INDEX PK_스테이징테이블;

CREATE INDEX IX_스테이징테이블_N1 ON 스테이징테이블 (일반컬럼1, 일반컬럼2);

-- [파티션 교체 실행]
ALTER TABLE 파티션테이블 
EXCHANGE PARTITION 교체할파티션명 
WITH TABLE 스테이징테이블 
INCLUDING INDEXES      -- 사전 인덱스를 파티션 로컬 인덱스와 맞바꾸는 핵심 옵션
WITHOUT VALIDATION;
```

### 3. Direct-Path INSERT (고속 병렬 적재)
CTAS를 쓸 수 없을 때, Redo를 최소화하며 기존 테이블에 밀어 넣는 문법.

```sql
-- [필수] 병렬 DML 세션 활성화
ALTER SESSION ENABLE PARALLEL DML;

-- [주의] 타겟 힌트의 별칭(T)과 소스 힌트의 별칭(S)이 쿼리의 별칭과 정확히 일치해야 함!
INSERT /*+ APPEND PARALLEL(T 4) */ INTO 타겟테이블 T (컬럼1, 컬럼2)
SELECT /*+ FULL(S) PARALLEL(S 4) */ 컬럼1, 컬럼2
FROM   소스테이블 S;

-- [필수] Direct-Path Insert 후에는 테이블에 Exclusive Lock이 걸리므로 즉시 COMMIT
COMMIT;
```

### 4. Set-Based MERGE (단일 병합 처리)
건건이 LOOP 도는 로직을 한 방의 SQL로 튜닝.

```sql
MERGE INTO 타겟테이블 T
USING (
    -- [핵심] 1:N 조인 에러(ORA-30926) 방지를 위한 선집계 뷰
    SELECT 조인키_컬럼, 
           SUM(금액컬럼) AS SUM_AMT
    FROM   소스테이블
    GROUP BY 조인키_컬럼
) S
ON (T.조인키_컬럼 = S.조인키_컬럼)
WHEN MATCHED THEN
    UPDATE SET T.총금액 = T.총금액 + S.SUM_AMT
    -- 주의: ON 절에 쓰인 조인키 컬럼은 UPDATE SET 절에서 갱신 불가
WHEN NOT MATCHED THEN
    INSERT (조인키_컬럼, 총금액) 
    VALUES (S.조인키_컬럼, S.SUM_AMT);
```

---

## ⚡ [T11] Runtime / Trace / DB Call (네트워크 통신 비용 감소)

### 1. PL/SQL Array Processing (BULK BIND)
단일 SQL(MERGE)로 처리가 불가능한 복잡한 로직일 때, DB Call 횟수를 획기적으로 줄이는 배열 처리.

```sql
DECLARE
    -- 커서 및 컬렉션 타입 정의 (생략)
BEGIN
    OPEN 커서명;
    LOOP
        -- 1000건씩 배열에 한 번에 담아서 Fetch (DB Call 대폭 감소)
        FETCH 커서명 BULK COLLECT INTO 컬렉션변수 LIMIT 1000;
        
        -- FOR LOOP 대신 FORALL을 사용하여 배열의 데이터를 한 번에 DML 수행
        FORALL i IN 1..컬렉션변수.COUNT
            INSERT INTO 타겟테이블 VALUES 컬렉션변수(i);
            
        EXIT WHEN 커서명%NOTFOUND;
    END LOOP;
    CLOSE 커서명;
    COMMIT;
END;
```

---

## 🔒 [T12] Lock / Transaction / Concurrency (동시성 제어)

### 1. 비관적 락(Pessimistic Lock) 구문
경합이 심한 환경에서 트랜잭션 대기 시간을 직접 제어하는 문법.

```sql
-- 대기하지 않고 즉시 에러(ORA-00054) 반환
SELECT * FROM 테이블명 WHERE 조건 FOR UPDATE NOWAIT;

-- 최대 3초만 대기 후 안 풀리면 에러 반환
SELECT * FROM 테이블명 WHERE 조건 FOR UPDATE WAIT 3;

-- [실무 큐잉 처리 핵심] 락이 걸린 행은 건너뛰고 락이 없는 행만 가져옴
SELECT * FROM 테이블명 WHERE 조건 FOR UPDATE SKIP LOCKED;
```

### 2. TM Lock (테이블 락) 방지용 인덱스
부모 테이블 데이터 삭제/수정 시, 자식 테이블 전체에 Lock이 걸려 시스템이 멈추는 것을 막는 필수 문법.

```sql
-- 자식 테이블의 외래키(FK) 컬럼에 반드시 일반 인덱스를 생성해야 함!
CREATE INDEX IX_자식테이블_FK ON 자식테이블(부모를_참조하는_FK컬럼);
```
