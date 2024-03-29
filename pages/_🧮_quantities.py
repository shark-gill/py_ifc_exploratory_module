import streamlit as st
import pandas as pd
import io
from tools import ifchelper
from tools import pandashelper
from tools import graph_maker

session = st.session_state

def initialize_session_state():
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

def load_data():
    if "ifc_file" in session:
        session["DataFrame"] = get_ifc_pandas()
        session.Classes = session.DataFrame["Class"].value_counts().keys().tolist()
        session["IsDataFrameLoaded"] = True

def get_ifc_pandas():
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session.ifc_file, 
        "IfcBuildingElement"
    )
    frame = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return frame

def get_csv(dataframe):
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer.getvalue()

def get_excel(dataframe):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def execute():  
    st.set_page_config(
        page_title="Quantities",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.header(" 🧮 Model Quantities")
    if not "IsDataFrameLoaded" in session:
        initialize_session_state()
    if not session.IsDataFrameLoaded:
        load_data()
    if session.IsDataFrameLoaded:    
        tab1, tab2 = st.tabs(["Dataframe Utilities", "Quantities Review"])
        with tab1:
            st.header("DataFrame Review")  
            st.write(session.DataFrame)

            csv_data = get_csv(session.DataFrame)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="data.csv",
                mime="text/csv"
            )

            excel_data = get_excel(session.DataFrame)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with tab2:
            row2col1, row2col2 = st.columns(2)
            with row2col1:
                if session.IsDataFrameLoaded:
                    class_selector = st.selectbox("Select Class", session.Classes, key="class_selector")
                    session["filtered_frame"] = pandashelper.filter_dataframe_per_class(session.DataFrame, session.class_selector)
                    session["qtos"] = pandashelper.get_qsets_columns(session["filtered_frame"])
                    if session["qtos"] is not None:
                        qto_selector = st.selectbox("Select Quantity Set", session.qtos, key='qto_selector')
                        quantities = pandashelper.get_quantities(session.filtered_frame, session.qto_selector)
                        st.selectbox("Select Quantity", quantities, key="quantity_selector")
                        st.radio('Split per', ['Level', 'Type'], key="split_options")
                    else:
                        st.warning("No Quantities to Look at !")
            ## DRAW FRAME
            with row2col2: 
                if "quantity_selector" in session and session.quantity_selector == "Count":
                    total = pandashelper.get_total(session.filtered_frame)
                    st.write(f"The total number of {session.class_selector} is {total}")
                else:
                    if session.qtos is not None:
                        st.subheader(f"{session.class_selector} {session.quantity_selector}")
                        graph = graph_maker.load_graph(
                            session.filtered_frame,
                            session.qto_selector,
                            session.quantity_selector,
                            session.split_options,                                
                        )
                        st.plotly_chart(graph)
    else: 
        st.header("Step 1: Load a file from the Home Page")
    
execute()