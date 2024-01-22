# 라이브러리 입력
## ifcopenshell은 IFC 데이터의 기하, 시맨틱 등을 처리하기 위한 기능을 제공하는 라이브러리
## 대화형 웹 어플리케이션을 생성하기 위한 오픈소스 라이브러리
import ifcopenshell
import streamlit as st


# 파일 업로드를 처리하기 위한 콜백 함수
def callback_upload():
    session["file_name"] = session["uploaded_file"].name
    session["array_buffer"] = session["uploaded_file"].getvalue()
    session["ifc_file"] = ifcopenshell.file.from_string(session["array_buffer"].decode("utf-8"))
    session["is_file_loaded"] = True
    
    ### 세션 상태에서 이전 모델 데이터를 초기화
    session["isHealthDataLoaded"] = False
    session["HealthData"] = {}
    session["Graphs"] = {}
    session["SequenceData"] = {}
    session["CostScheduleData"] = {}

    ### 세션 상태에서 이전 데이터 프레임을 초기화
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

# IFC 파일에서 프로젝트 이름을 검색하는 함수
def get_project_name():
    return session.ifc_file.by_type("IfcProject")[0].Name

# 프로젝트 이름을 변경하는 함수
def change_project_name():
    if session.project_name_input:
        session.ifc_file.by_type("IfcProject")[0].Name = session.project_name_input
        st.balloons()

# 메인 함수
def main():
    # 페이지 설정      
    st.set_page_config(
        layout= "wide",
        page_title="IFC Stream",
        page_icon="✍️",
    )
    # 타이틀 표시
    st.title("Web-based IFC data exploration module")
    st.markdown(
    """ 
    ###  📁 IFC Data
    """
    )

    ## 사이드 바 내비게이션 파일 업로더를 추가
    st.sidebar.header('Model Loader')
    st.sidebar.file_uploader("Choose a file", type=['ifc'], key="uploaded_file", on_change=callback_upload)

    ## 파일 이름과 성공 메시지를 추가
    if "is_file_loaded" in session and session["is_file_loaded"]:
        st.sidebar.success(f'Project successfuly loaded')
        st.sidebar.write("🔃 You can reload a new file  ")
        
        col1, col2 = st.columns([2,1])
        col1.subheader(f'Start Exploring "{get_project_name()}"')
        col2.text_input("✏️ Change Project Name", key="project_name_input")
        col2.button("✔️ Apply", key="change_project_name", on_click=change_project_name())

    st.sidebar.write("""
    --------------
    ### Author:
    #### Lee Heeseok
    
    
    --------------
    License: AYU
    
    """)
    st.write("")
    st.sidebar.write("")

if __name__ == "__main__":
    session = st.session_state
    main()