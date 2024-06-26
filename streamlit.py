import os

# Importing necessary modules and classes
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import logging
import datetime
import streamlit as st
import asyncio

# includes SearchManager
from pagemanager import PageManager

os.system('playwright install')
os.system('playwright install-deps')

TOP_MATCHES = 5
GPT_MODEL = 'mixtral-8x7b-32768' # 'gpt-3.5-turbo'# Defining the model to be used with OpenAI
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 100

st.sidebar.markdown("""
An Groq API key is required to make the client-sided call to the LLM.  A Groq account is required for this service.   
""")

models = {"LLaMA3 8b": "llama3-8b-8192","LLaMA3 70b": "llama3-70b-8192","Mixtral 8x7b": "mixtral-8x7b-32768","Gemma 7b": "gemma-7b-it"}
API_KEY = st.sidebar.text_input("API key: ", key="api_key", type='password')
MODELO = st.sidebar.selectbox("Select you model", options=list(models.keys()), index=0)
GPT_MODEL = models[MODELO]

st.sidebar.markdown("""
If you have a ChatGroq account, you can get one of your api keys from here:                 
https://console.groq.com/keys   
""")


# Setting the OpenAI API key environment variable
if API_KEY:
    os.environ['GROQ_API_KEY'] = API_KEY

# Explicitly disable parallelism in tokenizers to avoid the multiprocessing issue.
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=TEXT_CHUNK_SIZE, chunk_overlap=TEXT_CHUNK_OVERLAP)

# turn down the logging for embedding
logging.getLogger('transformers').setLevel(logging.WARNING)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)

embedding = HuggingFaceEmbeddings(
    model_name='BAAI/bge-small-en-v1.5',
    model_kwargs={'device': 'cpu'},
    cache_folder="./"
)

template = """
    Act as a professional investigative journalist and answer the question with a one page detailed explation based on the snippets 
    of context provided below. The snippets will also include a score that will give an estimate of how closely the text correlates 
    to the question. Summarize the information and provide a clear and concise response. If you are unsure of a correct answer, do 
    your best to infer a response based on the context provided but inform the reader that you are unsure.  Make sure that the user 
    understands that the information provided is based on the context provided.  Dont ever mention the snippets or your role in the 
    response.  Just provide the information as if you were a professional investigative journalist.

    ### User Submitted Question:
    
    {question}

    ### Context: 
    
    {context}
"""

st.title("Real-time Google Research Assistant")
st.subheader("built by AI-Programming")
st.markdown("""
    This application takes a question from the user and does a google search query on that question.  Then scrapes the 
    first 10 pages from the search then scrapes the content from each of the pages.  That content is loaded in a vector
    db (in memory) and the question is posed to the vector db to find the top 5 most relevant snippets.  Those snippets 
    are sent to the Groq models to generate a response to the initial research question before displaying the 
    response to the user.  
    
    Make sure you wait at least 30 seconds for the scraping and processing to complete.
""")

if 'search_logs' not in st.session_state:
    st.session_state['search_logs'] = []
if 'search_result' not in st.session_state:
    st.session_state['search_result'] = ''
    
async def main_async(question, st):
    # get page contents from search and then scrape
    page_contents = await PageManager.get_search_content_async(question, st)
    
    # Split all the flat data text into chunks
    chunks = text_splitter.split_text(page_contents)

    # turn down the logging level for docarray
    logger = logging.getLogger('docarray')
    logger.setLevel(logging.WARNING)
    
    print(f"chunks: {len(chunks)}")
    
    # Initialize vector store with texts and their embeddings
    vector_store = DocArrayInMemorySearch.from_texts(chunks, embedding)

    # Retrieve top 5 most matching chunks
    scores = vector_store.similarity_search_with_score(question, k=5)
    
    # Setting up a parallel runnable with context retrieval and question passthrough
    setup = RunnableParallel(context=vector_store.as_retriever(), question=RunnablePassthrough())

    # Creating a chat prompt template from the predefined template
    prompt = ChatPromptTemplate.from_template(template)

    # Initializing the chat model with the OpenAI API key and model choice
    model = ChatGroq(groq_api_key=API_KEY, model=GPT_MODEL)

    # Setting up a parser to handle the output from the chat model
    parser = StrOutputParser()

    # Defining a chain of operations: setup, prompt, model, and parser
    chain = (
        setup
        | prompt
        | model
        | parser
    )

    # Invoking the chain with the question and printing the response
    response = chain.invoke(question)
    
    return response

# Function to trigger the search and update logs
def trigger_search(query, st):
    st.session_state['search_logs'] = []
    st.session_state['search_result'] = ''
    st.session_state['search_logs'].append("Start searching at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.session_state['search_logs'].append(f"search: {query}")
    
    # result = main(query)
    result = asyncio.run(main_async(query, st))
    
    st.session_state['search_logs'].append("Finished searching at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.session_state['search_result'] = result

# Define the form
with st.form("search_form"):
    query = st.text_input("Enter your search query", key="search_query")
    submitted = st.form_submit_button("Search")
    
# After form submission, check for missing data
if submitted:
    if not API_KEY:
        st.warning("API key is required. Please enter your API key.")
    if not query:
        st.warning("Search query is required. Please enter your search query.")
    if API_KEY and query:
        st.session_state['search_result'] = ''  # Clear previous result
        # Only proceed if both values are present
        trigger_search(query, st)    

if st.session_state['search_result']:
    st.text_area("Search Results", value=st.session_state['search_result'], height=300)

if st.session_state['search_logs']:
    st.write("## Search Logs")
    for log in st.session_state['search_logs']:
        st.text(log)
