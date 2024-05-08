import os
from PIL import Image
import streamlit as st
from lyzr_automata.ai_models.openai import OpenAIModel
from lyzr_automata import Agent, Task
from lyzr_automata.tasks.task_literals import InputType, OutputType
from lyzr_automata.pipelines.linear_sync_pipeline  import  LinearSyncPipeline
from lyzr_automata import Logger
from dotenv import load_dotenv; load_dotenv()
from utils import utils

# Setup your config
utils.page_config()
utils.style_app()

# Load and display the logo
image = Image.open("./logo/lyzr-logo.png")
st.image(image, width=150)

# App title and introduction
st.title("AI Proofreader")
st.markdown("### Welcome to the AI Proofreader by Lyzr!")
st.markdown("AI Proofreader reviews and edits simple texts or text documents. This app will help you check for grammar, spelling, punctuation, and formatting errors !!!")



# replace this with your openai api key or create an environment variable for storing the key.
API_KEY = os.getenv('OPENAI_API_KEY')

data = "data"
os.makedirs(data, exist_ok=True)


open_ai_model_text = OpenAIModel(
    api_key= API_KEY,
    parameters={
        "model": "gpt-4-turbo-preview",
        "temperature": 0.5,
        "max_tokens": 1500,
    },
)

def ai_proofreader(text):
    
    ProofReader = Agent(
        prompt_persona="""You are an expert proofreader who are expert to find the grammatical error, as well you are very good at check for grammar, spelling, punctuation, and formatting errors""",
        role="AI Proofreader", 
    )

    rephrase_text =  Task(
        name="Rephrasing Text",
        agent=ProofReader,
        output_type=OutputType.TEXT,
        input_type=InputType.TEXT,
        model=open_ai_model_text,
        instructions=f"Use the description provided, Check the whole: '{text}' and rephrase the text according grammar, spelling, punctuation, and formatting errors, [!Important] Avoid Introduction and conclusion from the response",
        log_output=True,
        enhance_prompt=False,
        default_input=text
    )

    remarks = Task(
        name="Remarks",
        agent=ProofReader,
        output_type=OutputType.TEXT,
        input_type=InputType.TEXT,
        model=open_ai_model_text,
        instructions=f"Check the whole: '{text}' and provide the remarks in bullet points according grammar, spelling, punctuation, and formatting errors, [!Important] Avoid Introduction and conclusion from the response",
        log_output=True,
        enhance_prompt=False,
        default_input=text

    )




    logger = Logger()
    

    main_output = LinearSyncPipeline(
        logger=logger,
        name="AI ProofReader",
        completion_message="App Generated all things!",
        tasks=[
            rephrase_text,
            remarks,
        ],
    ).run()

    return main_output


def text_box_input():
    user_input = st.text_area("Drop the text you would like to have proofread.")

    if user_input == '':
        st.warning('Text was not provided in your input')

    if user_input != '':
        if st.button('Submit'):
            generated_output = ai_proofreader(text=user_input)
            output = generated_output[0]['task_output']
            st.subheader('Before Proofreading')
            st.write(user_input)
            st.markdown('---')
            st.subheader('Output after Proofread')
            st.write(output)
            st.markdown('---')
            remarks = generated_output[1]['task_output']
            st.subheader('Remarks:')
            st.write(remarks)


def text_file_input():
    text_file = st.file_uploader('Upload a text document', type=["txt"])

    if text_file is not None:
        utils.save_uploaded_file(directory=data, uploaded_file=text_file)
        file = utils.file_checker()
        if len(file)>0:
            file_path = utils.get_files_in_directory(data)

            with open(file_path[0], 'r') as file:
                text_data = file.read()
        
            if st.button('Submit'):
                generated_output = ai_proofreader(text=text_data)
                output = generated_output[0]['task_output']
                st.subheader('Text Before Proofreading')
                st.write(text_data)
                st.markdown('---')
                st.subheader('Text After Proofreading')
                st.write(output)
                st.markdown('---')
                remarks = generated_output[1]['task_output']
                st.subheader('Remarks:')
                st.write(remarks)
    
    elif text_file is None:
        utils.remove_existing_files(directory=data)





if __name__ == "__main__":
    # session state for tex box button
    if 'text_box_button' not in st.session_state:
        st.session_state.text_box_button = False


    # session state for text file button
    if 'text_file_button' not in st.session_state:
        st.session_state.text_file_button = False


    def text_box_button():
        st.session_state.text_box_button = True
        st.session_state.text_file_button = False

    def text_file_button():
        st.session_state.text_file_button = True
        st.session_state.text_box_button = False

    
    col1, col2 = st.columns(2)

    with col1:
        st.button('Input Text', on_click=text_box_button)
    with col2:
        st.button('Upload Text File', on_click=text_file_button)


    if st.session_state.text_box_button: 
        text_box_input()

    if st.session_state.text_file_button:
        text_file_input()


    utils.template_end()