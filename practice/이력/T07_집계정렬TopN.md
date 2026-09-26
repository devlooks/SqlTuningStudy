# 🗂️ T07 GROUP BY / Sort / Top-N — 이력

- **최종 갱신:** 2026-09-27
- **사다리 위치:** 3/11 · **상태:** 🔵 진행 중 (현재 테마)
- **교안:** `SQLP_실기_테마교안.md` §2 T07 · **숙련도:** `SQLP_실기_테마별_숙련도.md` §4·§5·§9
- **세션 전문:** `이력/_세션전문.md` (시간순 원본)

> 이 파일에는 **T07 문항의 풀이 결과만** 적는다. 세션 전체 서술은 `_세션전문.md` 에 append 한다.

---

## 1. 풀이 이력

| 일자 | 세션 | Pattern ID | 난이도 | 판정 | 요약 |
|:---:|---|---|:---:|---|---|
| 2026-09-06 | B01 T07 | O01, P01 | 중급 | **독립해결 (60/100 -> 최종수정 100)** | [1교시: 계좌 거래내역] '='조건 선두 배치 및 정렬 컬럼 순서 완벽 도출. ASC 생성 인덱스에 순방향 INDEX 힌트 사용으로 스캔 방향 충돌 진단(부분오답 60점). 튜터의 'INDEX_DESC' 피드백을 즉시 수용 및 교정하여 최종 Mastered. |
| 2026-09-10 | 1교시 집계 위치 판별 (원본2 + 변형2) | G01, G03, R06 | 중~고 | 4문항 평균 66.3 / **독립해결 0** | 병목 Id **4/4**, ④비중 **4/4**, ③낭비율 코칭 후 2/2. B/C 판별 **3/4**. 그러나 **판정→SQL 이관 1/4 · 힌트 물리 검증 1/4 · 결과집합 3문장 0/4** — RC1(판정→SQL 이관 실패)·RC2(힌트 물리 검증 부재) 신규 특정. 진단 능력과 처방 능력의 분리가 실증된 세션 |
| 2026-09-27 | 1교시 실기형 "월간 카테고리별 매출 집계" (표준) | G03, R06, J01, J02, G04 | 고 | **⚠️ 부분 오답 (70/100)** | [1] 병목 Id 6 정답(40/40). [2] **집계 위치 판단 생략** → 선집계 없이 `LEADING(S P) USE_HASH(P) FULL(P)`만 적용(107,502, 22배). 정답 선집계+NL 27,502(87배). Inner FULL 블록을 테이블 통계 100,000에서 정확히 가져옴(슬립 #24 1회 회복). 힌트 물리 성립. 결과 3칸 신설했으나 "동일"만 기재. A4 0 · A5 1 · A6 1 · A7 0 |
| 2026-09-27 | 2교시 보강 드릴 — R2-집계 판정 2사례 (브랜드별 / VIP 지역별) | G03 | 초 | ⚠️ 부분 오답 (결론 2/2) | 결론(선집계/후집계) 2/2 정답. 그러나 사례 2의 C에 **GROUP BY 노드 자신(Id 1) A-Rows 17** 기입(정답 Id 2 9,000) → 슬립 #25 신규. 조인 역할 근거에 "Buffers가 늘어남"(누적값, K01), 900,000→9,000을 "1000건 줄어듦"으로 산술 오류 |
| 2026-09-27 | 2교시 실기형 변형 "이벤트 포인트 정산" (표준) | G03, R06, J01, G04 | 고 | **⚠️ 부분 오답 (60/100)** | AS-IS HASH(MEMBER FULL 400,000블록). [1] Id 5 정답(40/40). [2] **선집계 자력 판정·적용 성공(A4 1)**, 바깥 `SUM(SAVE_CNT)` 정확. 그러나 ① `LEADING(M V) USE_NL(V)` — 판정(12,000건 선행)과 조인 순서 반대(K35·K13) ② AVG 분모 `SUM(COUNT(*))` → NULL 포함으로 결과 파괴(K22, G2-②) ③ 문법 오류 3곳 ④ 근거 출발값 4,000,000(정답 240,000). 교정 2회: 2차 `USE_NL(V)` 대상 오류(K16, 슬립 #8 재발) → 3차 완료. 정답 84,602(5.2배). A4 1 · A5 0 · A6 0 · A7 0 |
| 2026-09-27 | 3교시 처방 전용 "일별 업종 승인 집계" | G03, R06, J01, G04 | 중 | **❌ 오답 ([2] 10/60)** | 병목 판정 제공(Id 5 NL 반복 탐색 1,000,000회). **차원 테이블 MERCHANT를 SECTOR_CD로 집계** → 뷰에 MERCHANT_ID 없음(ORA-00904), 팩트 테이블 식별 실패(R2-집계 ①). `NO_MERGE(M)` 뷰 안 테이블 지정(G1-②). G1 칸 미작성, G2 "컬럼 동일 사용". USE_HASH 대상(두 번째 자리)은 정확. 정답 선집계(1,000,000→20,000)+NL 90,000(44.6배). A4 0 · A5 0 · A6 0 · A7 0 |

---

## 2. 출제 완료 · 미풀이 문항

> 출제는 끝났으나 아직 풀지 않은 문항이다. 풀고 나면 **§2 테마별 이력**과 **§3 세션 전문**으로 옮기고 이 절에서 지운다.


### 실기형 — 월간 카테고리별 매출 집계 (✅ 2026-09-27 풀이 완료 → §1. 오답 재출제 원본으로 보관)

- **출제일:** 2026-09-26 · **형식:** 표준(실기형) · **난이도:** 고 (집계 위치 판단 → 조인 방식 재판단 → COUNT 변환이 연쇄)
- **내부 Pattern:** G03, R06, J01, J02, G04 / 타깃 K09, K18, K20~K23, G2-② (사용자 비공개)
- **사용자에게 이미 제시됨.** 다음 세션에서 아래 문제 본문을 그대로 다시 보여준다.

#### 문제 본문

아래 SQL은 매월 초 전월 매출을 **상품 카테고리별로 집계하는 배치**입니다. 수행 시간이 길어 튜닝이 필요합니다.
**제약 조건:** 인덱스 추가·변경 불가 / 테이블 구조 변경 불가 / 결과집합(행 수와 각 컬럼 값)은 원본과 같아야 함 / 힌트 사용 가능

```sql
CREATE TABLE PRODUCT (
  PROD_ID      NUMBER        NOT NULL,
  PROD_NM      VARCHAR2(100) NOT NULL,
  CATEGORY_CD  VARCHAR2(10)  NOT NULL,
  CONSTRAINT PRODUCT_PK PRIMARY KEY (PROD_ID)       -- 높이 3
);

CREATE TABLE SALES (
  SALE_NO   NUMBER       NOT NULL,
  SALE_DT   VARCHAR2(8)  NOT NULL,                 -- 'YYYYMMDD'
  PROD_ID   NUMBER       NOT NULL,                 -- FK → PRODUCT
  SALE_AMT  NUMBER,                                -- NULL 허용
  CONSTRAINT SALES_PK PRIMARY KEY (SALE_NO)
);

CREATE INDEX SALES_X1 ON SALES (SALE_DT);           -- 높이 3
```

| 항목 | 값 |
|---|---|
| PRODUCT | 5,000,000건 / 100,000블록 / CATEGORY_CD 종류 50개 |
| SALES | 20,000,000건 / 200,000블록 / 판매일자 순으로 적재됨 |
| SALES 2026년 8월분 | 600,000건 |
| 8월에 팔린 서로 다른 PROD_ID 수 | 5,000개 |

```sql
SELECT P.CATEGORY_CD,
       SUM(S.SALE_AMT) AS SALE_AMT,
       COUNT(*)        AS SALE_CNT
  FROM SALES S, PRODUCT P
 WHERE S.SALE_DT BETWEEN '20260801' AND '20260831'
   AND P.PROD_ID = S.PROD_ID
 GROUP BY P.CATEGORY_CD;
```

```text
---------------------------------------------------------------------------------------
| Id | Operation                      | Name       | Starts | A-Rows |  Buffers |
---------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT               |            |      1 |     50 |  2407502 |
|  1 |  HASH GROUP BY                 |            |      1 |     50 |  2407502 |
|  2 |   NESTED LOOPS                 |            |      1 | 600000 |  2407502 |
|  3 |    TABLE ACCESS BY INDEX ROWID | SALES      |      1 | 600000 |     7502 |
|* 4 |     INDEX RANGE SCAN           | SALES_X1   |      1 | 600000 |     1502 |
|  5 |    TABLE ACCESS BY INDEX ROWID | PRODUCT    | 600000 | 600000 |  2400000 |
|* 6 |     INDEX UNIQUE SCAN          | PRODUCT_PK | 600000 | 600000 |  1800000 |
---------------------------------------------------------------------------------------

Predicate Information:
  4 - access("S"."SALE_DT">='20260801' AND "S"."SALE_DT"<='20260831')
  6 - access("P"."PROD_ID"="S"."PROD_ID")
```

(Buffers는 자식을 포함한 누적값)

**답안:** `[1] 병목 판단 (40점)` 가장 많은 블록을 직접 읽은 Id와 그 이유 한 줄 / `[2] 개선 SQL (60점)` 힌트 포함 완성 SQL + 튜닝 근거(숫자) + 결과 동일성 근거(행 수·NULL·건수). 한 번에 제출, 첫 제출 기준 채점.

#### 정답 (채점용 · 사용자 비공개)

- **[1]** 병목 **Id 6** `INDEX UNIQUE SCAN PRODUCT_PK` — 자기 Buffers 1,800,000 (74.8%)
  - 목표 건수: 병목 위에 `HASH GROUP BY`가 있으므로 집계 직전 Id 2 A-Rows 600,000 (K09 개정)
  - ③ 600,000 ÷ 600,000 = **1배** → 블록 낭비형 / ③' 1,800,000 ÷ 600,000 = **3블록/건** = 회당 3 = 인덱스 높이 → **NL 반복 탐색**
  - ④ 1,800,000 ÷ 2,407,502 = **74.8%**
  - 검산: 1,502 + 6,000 + 1,800,000 + 600,000 = 2,407,502
- **[2] 판단 연쇄**
  1. R2-집계: B = Id 3 600,000, C = Id 2 600,000 → B ≈ C. PRODUCT 조인은 PK·조건 없음·FK NOT NULL이라 붙이기(K21) → **선집계**
  2. 선집계 결과 5,000건으로 조인 방식 재판단(R2-집계 ⑥, K18): PRODUCT FULL 100,000블록 ÷ 4 = 25,000 > 5,000 → **NL**
  3. 바깥 단계: `COUNT(*)` → **`SUM(건수)`** (K22)

```sql
SELECT /*+ LEADING(S P) USE_NL(P) INDEX(P PRODUCT_PK) */
       P.CATEGORY_CD,
       SUM(S.SALE_AMT) AS SALE_AMT,
       SUM(S.SALE_CNT) AS SALE_CNT                 -- 바깥 COUNT(*) 금지 (K22)
  FROM (SELECT /*+ NO_MERGE INDEX(S2 SALES_X1) */
               S2.PROD_ID,
               SUM(S2.SALE_AMT) AS SALE_AMT,
               COUNT(*)         AS SALE_CNT
          FROM SALES S2
         WHERE S2.SALE_DT BETWEEN '20260801' AND '20260831'
         GROUP BY S2.PROD_ID) S,                   -- 600,000 → 5,000
       PRODUCT P
 WHERE P.PROD_ID = S.PROD_ID
 GROUP BY P.CATEGORY_CD;
```

- TO-BE Buffers ≈ 7,502 + 5,000 × 3 + 5,000 = **27,502** (약 87배 개선)
- 비교안: 선집계 없이 HASH 전환 ≈ 7,502 + 100,000 = 107,502 / 선집계 + HASH ≈ 107,502 → 선집계 + NL이 최선
- **G1:** LEADING(S P) 사이 조인 조건 P.PROD_ID = S.PROD_ID ✅ / USE_NL + INDEX 짝 모순 없음 ✅ / PRODUCT_PK 실존·선두 PROD_ID ✅ / 5,000 × 4 = 20,000 < 100,000 ✅
- **G2:** ① 행 수 — FK NOT NULL + PK 조인이라 선집계 전후 모두 행 손실·증폭 없음, 최종 50행 ② NULL — 상품별 SUM은 NULL 무시, 한 상품이 전부 NULL이면 NULL이고 바깥 SUM이 다시 무시하므로 원본과 동일 ③ 건수 — 안 COUNT(*) → 밖 SUM(SALE_CNT). 밖에서 COUNT(*)를 쓰면 카테고리별 **상품 수**가 나와 결과가 깨짐
- **함정:** 선집계만 하고 HASH 유지 / 선집계 없이 HASH만 전환(Buffers는 같아 보이나 조인 행 600,000) / 바깥 COUNT(*) / NO_MERGE 누락으로 뷰 병합


### SQLP 실기 2회독 — 1교시 3차 드릴 P·Q (SQL 작성 전용)


- **출제일:** 2026-09-18 (09-10 세션 이월분 재출제) · **테마:** T07 GROUP BY / 선집계 / Top-N
- **형식:** 처방 전용 — `[1] 병목 판정은 제공`, `[2] 개선 SQL만 작성`. 진단이 아니라 **처방** 훈련
- **설계 의도(사용자 제시분에는 미노출):**
  - **P:** 선집계 정답 + **AVG 결합법칙 함정** (`K22` 검증)
  - **Q:** 후집계 정답 + **허브 테이블 LEADING 카티션 함정** (`K15` 검증)
- ⚠️ 처방 전용 형식이므로 **진급 게이트 판정 대상이 아니다**(AGENTS §2.1).

#### 필수 제출물 3파트 (양 문항 공통)

1. **집계 위치 판단** — ① 금액·건수 컬럼이 속한 팩트 테이블 ② 조인 전 팩트 건수(B: 팩트 액세스 노드 A-Rows) ③ 모든 조인·필터 후 집계 직전 건수(C: 최종 GROUP BY 바로 아래 A-Rows) ④ **조인의 역할(컬럼만 붙이기 / 행을 줄이는 필터)** ⑤ 결론(조인 전 선집계 / 조인·필터 후 후집계)
2. **개선 SQL** — 힌트 세트 포함 완성본 + 필요 시 인덱스 DDL
3. **힌트 사전검증 4항 + 결과집합 3문장**
   - 사전검증 ① LEADING 인접성(각 테이블이 앞에 나온 테이블 중 하나와 WHERE 조인 조건을 갖는가)
   - 사전검증 ② 힌트 짝 정합성(`PUSH_PRED`는 NL 전용, `USE_HASH`와 동시 사용 시 무효)
   - 사전검증 ③ 인덱스 실존 / 신규 설계 시 선두 컬럼 = 조인키
   - 사전검증 ④ 손익분기(NL 반복횟수 × 회당 블록수 **vs** 상대 FULL 블록수, 숫자로)
   - 결과집합 3문장 = 행 수 / NULL / 중복

---

#### 드릴 P

##### 테이블·통계

| 테이블 | 건수 | 비고 |
|---|---:|---|
| TB_SALE_DTL | 200,000,000 | PK (SALE_NO, DTL_SEQ) / `TB_SALE_DTL_X01 (SALE_DT)` / SALE_DT 순 적재(클러스터링 양호) / FULL 시 약 2,500,000 블록 |
| TB_CUST | 20,000,000 | PK (CUST_NO) / GRADE_CD 5종 / **FULL 시 약 250,000 블록** |

- `TB_SALE_DTL.SALE_AMT`, `UNIT_PRICE`, `STORE_CD`, `CUST_NO` 는 **NOT NULL**
- 2026-01 판매상세 = 12,000,000건, 해당 기간 (STORE_CD, CUST_NO) 조합 = **500,000**
- 점포 3,000개, 최종 결과 12,400행

##### AS-IS SQL

```sql
SELECT d.STORE_CD,
       c.GRADE_CD,
       SUM(d.SALE_AMT)   AS TOT_AMT,
       COUNT(*)          AS SALE_CNT,
       AVG(d.UNIT_PRICE) AS AVG_PRICE
  FROM TB_SALE_DTL d,
       TB_CUST     c
 WHERE d.SALE_DT >= DATE '2026-01-01'
   AND d.SALE_DT <  DATE '2026-02-01'
   AND c.CUST_NO  = d.CUST_NO
 GROUP BY d.STORE_CD, c.GRADE_CD;
```

##### AS-IS 실행계획

```
-----------------------------------------------------------------------------------------------------------------
| Id | Operation                              | Name            |     Starts | E-Rows |     A-Rows |    Buffers |
-----------------------------------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT                       |                 |          1 |        |     12,400 | 48,182,140 |
|  1 |  HASH GROUP BY                         |                 |          1 | 11,908 |     12,400 | 48,182,140 |
|  2 |   NESTED LOOPS                         |                 |          1 | 11,842K| 12,000,000 | 48,182,140 |
|  3 |    TABLE ACCESS BY INDEX ROWID BATCHED | TB_SALE_DTL     |          1 | 11,842K| 12,000,000 |    182,140 |
|  4 |     INDEX RANGE SCAN                   | TB_SALE_DTL_X01 |          1 | 11,842K| 12,000,000 |     32,140 |
|  5 |    TABLE ACCESS BY INDEX ROWID         | TB_CUST         | 12,000,000 |      1 | 12,000,000 | 48,000,000 |
|  6 |     INDEX UNIQUE SCAN                  | TB_CUST_PK      | 12,000,000 |      1 | 12,000,000 | 36,000,000 |
-----------------------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   4 - access("D"."SALE_DT">=TO_DATE('2026-01-01') AND "D"."SALE_DT"<TO_DATE('2026-02-01'))
   6 - access("C"."CUST_NO"="D"."CUST_NO")
```

##### [1] 병목 판정 (제공)

- **병목 Id: 5 (+6)** — TB_CUST 반복 액세스
- **③ 낭비율:** 12,000,000 ÷ 12,400 = **968배** (행 낭비형)
- **④ 비중:** (12,000,000 + 36,000,000) ÷ 48,182,140 = **99.6%**

##### [2] 요구 — 개선 SQL (60점) + 필수 제출물 3파트

- 제약: 인덱스 신규 생성 1개까지 허용(불필요하면 생성하지 않아도 됨). 결과집합은 AS-IS와 완전히 동일해야 한다.

---

#### 드릴 Q

##### 테이블·통계

| 테이블 | 건수 | 비고 |
|---|---:|---|
| TB_CLAIM_DTL | 300,000,000 | PK (CLAIM_NO, DTL_SEQ) / CLAIM_AMT NOT NULL / FULL 시 4,300,000 블록 / 청구당 평균 7.5행 |
| TB_CLAIM | 40,000,000 | PK (CLAIM_NO) / `TB_CLAIM_X01 (CLAIM_DT)` / 컬럼 CLAIM_DT, HOSP_CD, MEMB_NO |
| TB_HOSP | 30,000 | PK (HOSP_CD) / REGION_CD / FULL 700 블록 / REGION_CD='11' = 4,000건 |
| TB_MEMB | 8,000,000 | PK (MEMB_NO) / PROD_CD / FULL 160,000 블록 / PROD_CD='P0731' = 1,600,000명 |

- 2026-01-01 ~ 2026-03-31 청구 = 480,000건, 그중 서울(11) 병원 = 62,000건, 그중 P0731 가입자 = **12,400건**
- TB_CLAIM_DTL 은 모든 청구에 대해 1건 이상 존재

##### AS-IS SQL

```sql
SELECT cl.CLAIM_NO, cl.CLAIM_DT, h.HOSP_NM, m.MEMB_NO,
       d.TOT_AMT, d.DTL_CNT
  FROM (SELECT CLAIM_NO,
               SUM(CLAIM_AMT) AS TOT_AMT,
               COUNT(*)       AS DTL_CNT
          FROM TB_CLAIM_DTL
         GROUP BY CLAIM_NO) d,
       TB_CLAIM cl,
       TB_HOSP  h,
       TB_MEMB  m
 WHERE cl.CLAIM_DT >= DATE '2026-01-01'
   AND cl.CLAIM_DT <  DATE '2026-04-01'
   AND h.HOSP_CD   = cl.HOSP_CD
   AND h.REGION_CD = '11'
   AND m.MEMB_NO   = cl.MEMB_NO
   AND m.PROD_CD   = 'P0731'
   AND d.CLAIM_NO  = cl.CLAIM_NO;
```

##### AS-IS 실행계획

```
-----------------------------------------------------------------------------------------------------------------
| Id | Operation                              | Name            | Starts | E-Rows |      A-Rows |    Buffers |
-----------------------------------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT                       |                 |      1 |        |      12,400 |  4,487,105 |
|  1 |  HASH JOIN                             |                 |      1 | 11,902 |      12,400 |  4,487,105 |
|  2 |   HASH JOIN                            |                 |      1 | 12,400 |      12,400 |    187,105 |
|  3 |    HASH JOIN                           |                 |      1 | 62,000 |      62,000 |     27,105 |
|  4 |     TABLE ACCESS FULL                  | TB_HOSP         |      1 |  4,000 |       4,000 |        700 |
|  5 |     TABLE ACCESS BY INDEX ROWID BATCHED| TB_CLAIM        |      1 |   480K |     480,000 |     26,405 |
|  6 |      INDEX RANGE SCAN                  | TB_CLAIM_X01    |      1 |   480K |     480,000 |      1,405 |
|  7 |    TABLE ACCESS FULL                   | TB_MEMB         |      1 | 1,600K |   1,600,000 |    160,000 |
|  8 |   VIEW                                 |                 |      1 | 40,000K|  40,000,000 |  4,300,000 |
|  9 |    HASH GROUP BY                       |                 |      1 | 40,000K|  40,000,000 |  4,300,000 |
| 10 |     TABLE ACCESS FULL                  | TB_CLAIM_DTL    |      1 |   300M | 300,000,000 |  4,300,000 |
-----------------------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   1 - access("D"."CLAIM_NO"="CL"."CLAIM_NO")
   2 - access("M"."MEMB_NO"="CL"."MEMB_NO")
   3 - access("H"."HOSP_CD"="CL"."HOSP_CD")
   4 - filter("H"."REGION_CD"='11')
   6 - access("CL"."CLAIM_DT">=TO_DATE('2026-01-01') AND "CL"."CLAIM_DT"<TO_DATE('2026-04-01'))
   7 - filter("M"."PROD_CD"='P0731')
```

##### [1] 병목 판정 (제공)

- **병목 Id: 8 (+9, 10)** — 인라인 뷰 `d`
- **③ 낭비율:** 40,000,000 ÷ 12,400 = **3,226배** (Id 10 기준이면 24,194배)
- **④ 비중:** 4,300,000 ÷ 4,487,105 = **95.8%**

##### [2] 요구 — 개선 SQL (60점) + 필수 제출물 3파트

- 제약: 인덱스 신규 생성 1개까지 허용. 결과집합은 AS-IS와 완전히 동일해야 한다.
- 힌트 세트는 **LEADING 을 반드시 포함**하여 조인 순서를 명시할 것.

---

#### 채점 배점 (문항당 100점)

| 항목 | 배점 |
|---|---:|
| B/C 판별 + 조인의 정체 판정 | 20 |
| 개선 SQL 구조 (선집계/후집계 정확 반영) | 30 |
| 힌트 세트 물리적 성립 | 20 |
| 인덱스 설계 (선두 컬럼) | 10 |
| 힌트 사전검증 4항 | 10 |
| 결과집합 3문장 | 10 |

---

### [추가 출제] 2교시 문제 1 — 1:N 증폭 / DISTINCT 제거

- **출제일:** 2026-09-18
- **설계 의도(비공개):** J07·J10·O03 — 1:N 증폭 후 `DISTINCT` 정리 구조를 **세미 조인(EXISTS)** 으로 전환.
  부수 검증: ① 테이블 액세스 소멸(커버링) ② **신규 인덱스 불필요** 판단 ③ `DISTINCT` 동반 제거
- **형식:** 정식 2문항 (`[1]` 40점 + `[2]` 60점)

##### 통계

| 테이블 | 건수 | 비고 |
|---|---:|---|
| TB_CUST | 20,000,000 | PK (CUST_NO) / `TB_CUST_X02 (GRADE_CD)` / GRADE_CD 6종 / CUST_NO·GRADE_CD NOT NULL |
| TB_CUST (VIP+VVIP) | 400,000 | |
| TB_ORD | 300,000,000 | PK (ORD_NO) / `TB_ORD_X01 (CUST_NO, ORD_DT)` / CUST_NO·ORD_DT NOT NULL / CUST_NO 순 적재 아님 |

- VIP/VVIP 고객의 2026년 주문 = 24,000,000건 (1인 평균 60건)
- 2026년 주문이 1건 이상인 VIP/VVIP 고객 = **380,000명** (= 최종 결과)

##### AS-IS SQL

```sql
SELECT DISTINCT c.CUST_NO, c.CUST_NM, c.GRADE_CD
  FROM TB_CUST c,
       TB_ORD  o
 WHERE c.GRADE_CD IN ('VIP','VVIP')
   AND o.CUST_NO = c.CUST_NO
   AND o.ORD_DT >= DATE '2026-01-01';
```

##### AS-IS 실행계획

```
--------------------------------------------------------------------------------------------------------------
| Id | Operation                              | Name        |  Starts | E-Rows |     A-Rows |    Buffers |
--------------------------------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT                       |             |       1 |        |    380,000 | 25,341,400 |
|  1 |  HASH UNIQUE                           |             |       1 |   366K |    380,000 | 25,341,400 |
|  2 |   NESTED LOOPS                         |             |       1 | 23,842K| 24,000,000 | 25,341,400 |
|  3 |    TABLE ACCESS BY INDEX ROWID BATCHED | TB_CUST     |       1 |   398K |    400,000 |     61,400 |
|  4 |     INDEX RANGE SCAN                   | TB_CUST_X02 |       1 |   398K |    400,000 |      1,400 |
|  5 |    TABLE ACCESS BY INDEX ROWID BATCHED | TB_ORD      | 400,000 |     59 | 24,000,000 | 25,280,000 |
|  6 |     INDEX RANGE SCAN                   | TB_ORD_X01  | 400,000 |     59 | 24,000,000 |  1,280,000 |
--------------------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   4 - access("C"."GRADE_CD"='VIP' OR "C"."GRADE_CD"='VVIP')
   6 - access("O"."CUST_NO"="C"."CUST_NO" AND "O"."ORD_DT">=TO_DATE('2026-01-01'))
```

##### 정답 (채점용)

- `[1]` 병목 **Id 5** — 순수 Buffers 24,000,000 (전체의 94.7%). 존재 여부만 필요한데 24,000,000행의 테이블 블록을 랜덤 액세스
- ③ 24,000,000 ÷ 380,000 = **63배** (행 낭비형) / ④ **94.7%**
- 검산 4항: 1,400 + 60,000 + 1,280,000 + 24,000,000 = 25,341,400

```sql
SELECT c.CUST_NO, c.CUST_NM, c.GRADE_CD
  FROM TB_CUST c
 WHERE c.GRADE_CD IN ('VIP','VVIP')
   AND EXISTS (SELECT /*+ NL_SJ INDEX(o TB_ORD_X01) */ 1
                 FROM TB_ORD o
                WHERE o.CUST_NO = c.CUST_NO
                  AND o.ORD_DT >= DATE '2026-01-01');
```

- **신규 인덱스 불필요** — `TB_ORD_X01 (CUST_NO, ORD_DT)` 가 이미 커버링
- TO-BE Buffers ≈ 61,400 + 1,200,000 = **약 1,261,400 → 20배 개선**
- `DISTINCT` 제거 필수 (세미 조인은 좌측을 증폭하지 않음 → `HASH UNIQUE` 소멸)
