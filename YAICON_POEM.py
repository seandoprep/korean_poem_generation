import streamlit as st
import io
from PIL import Image
from model import ClipCaptionPrefix, predict


def inference(prefix_length, clip_length, prefix_size, num_layers, mapping_type, image):
    
    model = ClipCaptionPrefix(
        prefix_length=prefix_length,
        clip_length=clip_length,
        prefix_size=prefix_size,
        num_layers=num_layers,
        mapping_type=mapping_type,
     )

    return predict(image, model)


def poem_postprocess(poem):
    sentences = []
    is_prev_period = False
    start = 0
    i = 0
    while i < len(poem):
        if poem[i] in ['.', '?', '!']:
            is_prev_period = True
            i += 1
        else:
            if is_prev_period == True:
                is_prev_period = False
                end = i
                sentences.append(poem[start:end])
                # 공백은 건너뛴다.
                while poem[i] == ' ':
                    i += 1
                start = i
            else:
                i += 1

    # 마지막 문장의 경우, 마침표로 끝나야 (i.e. 온전한 문장이어야) 리스트에 추가.
    if poem[-1] == '.':
        sentences.append(poem[start:])

    return "\n".join(sentences)


st.set_page_config(
    page_title='YAICON 김삿갓',
    page_icon='✍️',
    layout='wide'
    )

st.header("AI 시인 김삿갓 ✍️")
st.subheader("당신의 추억을 \"시\"로 간직해보세요!")

with st.sidebar:
    bytes_data = st.file_uploader("당신의 추억을 업로드해주세요!")

if bytes_data:
    data = io.BytesIO(bytes_data.getvalue())
    image = Image.open(data)
    st.image(image)

    if st.button("시 쓰기"):
        with st.spinner("시를 작성하고 있습니다!"):
            poem = inference(prefix_length=10, clip_length=10, prefix_size=512, num_layers=8, mapping_type="mlp", image=image)
            # poem = """
            # 살어리 살어리랏다 청산에 살어리랏다
            # 만수산 드렁칡이 얽혀진들 어떠하리
            # """
            poem = poem_postprocess(poem)
        st.text(poem)
else:
    st.text("당신이 간직하고 싶은 사진을 옆의 사이드바에서 업로드해주세요.")

