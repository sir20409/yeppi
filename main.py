import streamlit as st

# 진법 변환을 위한 함수
def base_n_to_decimal(num_str, base):
    return int(num_str, base)

def decimal_to_base_n(num, base):
    if num == 0:
        return "0"
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    while num > 0:
        result = digits[num % base] + result
        num //=base
    return result

st.title("진법 변환 및 시각화 도구")

st.write("진법을 이해하기 어려운 학생들을 위한 시각적 도구입니다.")

# 진법 선택
base = st.slider("몇 진법으로 할까요?", min_value=2, max_value=36, value=10)

st.write(f"선택된 진법: {base}진법")

# 입력 모드 선택: 1) 십진법 입력 2) 선택한 진법 입력
mode = st.radio("입력 모드 선택", ("십진법 숫자 입력", f"{base}진법 숫자 입력"))

if mode == "십진법 숫자 입력":
    dec_val = st.number_input("십진법 숫자 입력", min_value=0, step=1)
    # 십진법 -> 선택한 진법
    base_val = decimal_to_base_n(dec_val, base)
    st.write(f"{dec_val} (10진법) = {base_val} ({base}진법)")

elif mode == f"{base}진법 숫자 입력":
    base_val = st.text_input(f"{base}진법 숫자 입력 (0-9, A-Z 사용)")
    if base_val:
        try:
            dec_val = base_n_to_decimal(base_val.upper(), base)
            st.write(f"{base_val} ({base}진법) = {dec_val} (10진법)")
        except ValueError:
            st.error(f"잘못된 {base}진법 숫자입니다.")

# 추가: 주요 진법별 변환값 표 보여주기
st.markdown("---")
st.subheader("다른 주요 진법별 변환 예시")

if mode == "십진법 숫자 입력":
    dec_val = int(dec_val)
elif mode == f"{base}진법 숫자 입력" and base_val:
    try:
        dec_val = base_n_to_decimal(base_val.upper(), base)
    except:
        dec_val = None
else:
    dec_val = None

if dec_val is not None:
    bases = [2, 8, 10, 16]
    if base not in bases:
        bases.append(base)
    bases = sorted(list(set(bases)))

    data = []
    for b in bases:
        val = decimal_to_base_n(dec_val, b)
        data.append((f"{b}진법", val))
    st.table(data)


