인덱스 튜닝

48.  
조건 두가지 합쳐 처리 in 조건으로 묶고  
```
nvl(sum(case when 구분코드 = 'G' then 기본 이체금액 end), 0) 
-> 조건 G가 아닌 경우 null return, sum 내역에서 누락 된다
```

인덱스  
- 등치 + 등치 + 범위(일자) + 거래 코드 (in 조건)  

49.  

OR 조건 튜닝 시  
쿼리 -> OR조건  
힌트 -> USE_CONCAT  

인덱스 -> 등치 + OR 조건(USE_CONCAT으로 분기처리)

64.  
인덱스 선두 컬럼 + LIKE 조건 -> 값 입력 X -> 인덱스 FULL SCAN  
숫자형 컬럼 + LIKE 조건 -> 형변환 -> 성능 저하  
Null 허용 컬럼 + LIKE 조건 (OR + 등치)-> 결과 집합 오류 가능성 있음  

67.

Not Null 컬럼이 옵션 조건일 때  
- NVL 사용  

Nullable 컬럼이 옵션 조건일 때  
- Nullable 컬럼 기준 Union all 분기 처리

Erd 
  - O : Option  
  - * : Not null  
  - # : Pk




