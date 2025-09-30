## DML
  - select, Insert, Update, Delete

## DDL
  - create, alter, drop, rename

## DCL
  - grant, revoke

## TCL
  - commit, rollback

## 일반 집합 연산자
  - Union -> Union
  - Intersection -> Intersect
  - Product -> cross join
  - Except -> Minus

## 정규화
  - 정합성 확보 -> 불필요한 중복 줄이기
  - 외부키 -> 다른 테이블 기본기 사용관계

## ERD
  - 엔티티, 관계, 속성

## 합성 연산자
  - Oracle -> ||
  - SQL Server -> +
  - Concat 함수

## substr('SQL Expert', 5, 3) -> Exp
## substring('SQL Expert', 5, 3) -> Exp

## Case 문
```
select ename
  , case 
      when ~
      else ~
    end as ~
from t;
```

## NULL 함수
  - NVL, ISNULL(Expr1, Expr2) Expr1이 Null 일 경우 Expr2로
  - NULLIF(Expr1, Expr2) > Expr1과 Expr2가 같으면 Null
  - coalesce(Expr1, Expr2, Expr3) -> Null 이 아닌 Expr의 최초 값

## Group by 절과 having 절 순서 변경
  - 에러 X 동일 결과 출력
  - where -> 그룹핑전 필터링, having을 그룹핑 후 필터링

## 집계 함수
  - ISNULL(SAL, 0) -> 불필요한 연산 진행

## select 문장 식행 순서
  - from -> where -> group by -> having -> select -> order by

## Outer join 
  - (+) 컬럼이 기준 -> 해당 컬림 null 가능

## Inner join 
  - 내부 조인

## natural join 
  - 동일한 이름 갖는 모든 컬럼에 대해 Join (데이터 성격)
```
select ~ from A natural join B
```

## Using 조건절
  -> 같은 이름 컬럼 중 원하는 컬럼만 선택적 Equal Join
```
select ~ from A join B Using(deptno)
```

## Cross Join 
  - Product 개념

## 서브쿼리
  - 비연관 -> 메인 쿼리와 연관 X
  - 연관 -> 메인 쿼리와 연관 O
  - Single Row -> 항상 1건
  - Multi Row -> 여러건 (IN, ALL, ANY, EXISTS
  - Multi Col -> 실행 결과 여러 컬럼
    ```
    select ~ from ~ where (A, B) IN (select A, B ~ from ~)
    ```

## 연관 서브쿼리
  - 메인 쿼리에 존재하는 모든 행에 반복 수행

## 스칼러 서브쿼리
  - 메인 쿼리의 결과 건수 만큼 수행

## 뷰 
  - 독립성 -> 구조 변경, 응용프로그램 변경 X
  - 편리성 -> 복합질의 -> 단순 질의
  - 보안성 -> 뷰 생성시 컬럼 선택 가능

```
  create view vw_1 as select ~

  drop view vw_1;
```

## 집합 연산자의 결과 표시 HEADING 부분은 첫번째
  - SQL문에 사용된 ALIAS 적용
  - INTERSECT -> EXISTS, IN 으로 변경 가능

## 그룹함수
  - ROLLUP 함수
  - Grouping column -> N -> N + 1 (subTotal)
  - 순서 바뀌면 결과 변경 인수 주의

## Grouping 함수
  - 소계가 계산된 결과 Grouping(Expr) -> 1 로 출력 그외 결과 0

## Cube 함수
  - 다차원 집계
  - 시스템 부담
  - 컬럼 순서 상관 X
  - 2^n 승 결과

## Grouping Sets
  - 인수별 개별 집계
  - 순서 변경 해도 결과 그대로

## 윈도우 함수 
  - RANK 함수 -> 컬럼에 대한 순위 -> 1,2,2,4 ...
  - DENSE_RANK 함수 -> 동일 순위 하나의 건수 -> 1,2,2,3,4..
  - RANGE UNBOUNED PRECEDING
      - 전체 행 기준 파티션 첫번쨰 행까지 범위
  - ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
      - 현재 행 기준 앞뒤 1행씩
  - RANGE BETWEEN 50 PRECEDING AND 150 FOLLOWING
      - 현재행 + 50 ~ 150 이하
  - First_Value 함수
      - 파티션 별 가장 먼저 나온 값
      - ROWS UNBOUNED PRECEDING
        - 현재 행부터 파티션 첫번째 행
  - LAST_VALUE 함수
      - ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        -  현재 행 포함 파티션 내 마지막 행까지
       
  - LAG 함수
    - 이전 몇번째 행 가져 올수 있다
      ex) LAG (SAL) OVER(ORDER BY ~ ) 위에서 1
      ex) LAG (SAL, 2, 0) OVER (ORDER BY ~ ) 위에서 2개
          - 이전 2번째 없으면 0 처리 한다.

  - lead 함수
    - 이후 몇번 째 행의 값
    - ex) LEAD (HIREDATE, 1)
        - 이후 1번째

## 그룹내 비율 함수 
  - ratio_to report -> 행별 컬럼값의 백분율 소수점
  - percent_rank -> 순서상 0~1 사이 값으로
  - cume_dist -> 누적 백분율
  - NTILE -> 전체 건수를 N등분

## Top N 쿼리
  - ROWNUM 슈도 컬럼
  - TOP 절
    - SELECT TOP(2) ~ FROM ~
   
## 계층형 질의 
