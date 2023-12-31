import streamlit as st
from pubmed_manager import PubmedManager
from llama_index import VectorStoreIndex
from llama_index.evaluation import DatasetGenerator
from llama_index.readers.schema.base import Document
import os 
import openai
import uuid
from trubrics.integrations.streamlit import FeedbackCollector

# userId = str(uuid.uuid4())

#initialisation
if "search" not in st.session_state:
    st.session_state["search"] = False
if "query" not in st.session_state:
    st.session_state["query"] = None
if "response" not in st.session_state:
    st.session_state["response"] = None
if "feedbackRating" not in st.session_state:
    st.session_state["feedbackRating"] = None
if "feedbackText" not in st.session_state:
    st.session_state["feedbackText"] = None
if "apikey" not in st.session_state:
    st.session_state["apikey"] = None
if "references" not in st.session_state:
    st.session_state["references"] = []
# if "userID" not in st.session_state:
#     st.session_state["userId"] = userId
# if "pubmedPapers" not in st.session_state:
#     st.session_state.pubmedPapers = []

# config = trubrics.init(
#     email=st.secrets["TRUBRICS_EMAIL"],  # read your Trubrics secrets from environment variables
#     password=st.secrets["TRUBRICS_PASSWORD"]
# )

#streamlit code

st.set_page_config(page_title="fastbio")
col1,col2,col3 = st.columns([1,1,1])
col2.title("FastBio")
st.divider()


collectorCitations = FeedbackCollector(
    component_name="citations-feedback",
    email=st.secrets["TRUBRICS_EMAIL"], # Store your Trubrics credentials in st.secrets:
    password=st.secrets["TRUBRICS_PASSWORD"], # https://blog.streamlit.io/secrets-in-sharing-apps/
)


collectorMain=FeedbackCollector(
    component_name="default",
    email=st.secrets["TRUBRICS_EMAIL"], # Store your Trubrics credentials in st.secrets:
    password=st.secrets["TRUBRICS_PASSWORD"], # https://blog.streamlit.io/secrets-in-sharing-apps/
)

#@st.cache_resource(show_spinner=False)
# def create_feedback_collector(name):
#     collector = FeedbackCollector(
#         component_name=name,
#         email=st.secrets["TRUBRICS_EMAIL"],
#         password=st.secrets["TRUBRICS_PASSWORD"],
#     )
#     return collector

#sidebar
# apiKey = st.sidebar.text_input("OpenAI API Key", type="password")
# st.session_state.apikey = apiKey
# if not apiKey:
#     st.info("Please add your OpenAI API key to continue.")
#     st.stop()
openai.api_key = st.secrets["OPENAI_API_KEY"]




#main content




#add logic to create a userId
#link userId to VectorStoreIndices
#@st.cache_resource(show_spinner=False)
class SearchBackend1():
  def __init__(self):
    #   self.indexCreated = False
    self.index = None
    #self.queryEngine = None
    #self.persistDir = "/Users/arihantbarjatya/Documents/fastbio/database_storage/stored_embeddings/pubmed"
    #self.userId = str(uuid.uuid4())
    self.pubObj = PubmedManager()


  #@st.cache_data(show_spinner=False)
  def fetch_docs(_self,query):
    docs = _self.pubObj.fetch_details(query)
    return docs
  
  def update_index(self,docs):  
    for doc in docs:
      self.index.insert(doc)


  # add userId logic so once a users DB is created its remembered
  @st.cache_data(show_spinner=False)
  def main(_self,query):
    with st.spinner("Searching PubMed"):
        currentDocs,pubmedPapers = _self.fetch_docs(query)
        
        _self.index = VectorStoreIndex.from_documents(currentDocs)
        _self.queryEngine = _self.index.as_query_engine()
        response = _self.queryEngine.query(query)
        citations = []
        for node in response.source_nodes:
            # print(node)
            start_idx = node.node.start_char_idx
            end_idx = node.node.end_char_idx
            text = node.node.text
            text = text[start_idx:end_idx]
            score = node.score
            title = node.node.metadata["Title of this paper"]
            url = node.node.metadata["URL"]
            citations.append([text,title,url,score])
    
    return response,citations,pubmedPapers

def searchButtonCallback():
    st.session_state.search = True
    #st.session_state.toggle1 = not st.session_state.toggle2 
    # print(userInput)
    # response,citations,pubmedPapers = searchObj1.main(userInput)
    # st.session_state.query = userInput
    # st.session_state.response = str(response)
    # st.session_state.references = citations
    # st.session_state.pubmedPapers = pubmedPapers


def editcallback():
    st.session_state["search"] = False
    st.session_state["response"] = None
    st.session_state["feedbackRating"] = None
    st.session_state["feedbackText"] = None
    #st.session_state["engine"] = None
    st.session_state["references"] = []

def reboot():
    st.session_state["search"] = False
    st.session_state["query"] = None
    st.session_state["response"] = None
    st.session_state["feedbackRating"] = None
    st.session_state["feedbackText"] = None
    #st.session_state["engine"] = None
    st.session_state["references"] = []

def generatedQuestionCallback(newQuery):
    st.session_state["query"] = newQuery
    st.session_state["response"] = None
    #st.session_state["feedbackRating"] = None
    #st.session_state["feedbackText"] = None
    st.session_state["references"] = []
    st.session_state["search"] = True




@st.cache_data(show_spinner=False,experimental_allow_widgets=True)
def createNewQuestions(query,response):
    responseDoc = Document(text=response,extra_info={"Original Query":query})
    dataGenerator = DatasetGenerator.from_documents([responseDoc])
    numberOfQuestions = 3 
    newQuestions = dataGenerator.generate_questions_from_nodes(numberOfQuestions)
    newQuestions = sorted(newQuestions,key=len)
    #print(newQuestions)
           
    
    # try:
    #     newQuestions = newQuestions[:numberOfQuestions]
    # except Exception as e:
    #     pass
    
    # newQuestions = sorted(newQuestions,key=len)    
    # return newQuestions
    
    # n = len(newQuestions)

    return newQuestions


searchObj1 = SearchBackend1()
# userInput = st.text_input("Typer your query and Press Enter!")
# st.session_state.query = userInput
userEmail = st.experimental_user.email

# if userInput:
#     # tab1,tab2 = st.tabs(["Home","More Info!"])
#     # with tab1:
#     response,citations,pubmedPapers = searchObj1.main(st.session_state.query)
#     st.session_state.response = str(response)
#     st.session_state.references = citations

#     #st.write(f'<p style="font-size:30px"><b>Response</b></p>',unsafe_allow_html=True)
#         #st.markdown(f"*:{st.session_state.response}:*")
    
#     st.markdown("")
#     st.subheader("Response")
#     if st.session_state.response != "None":
#         st.write(f'<i>{st.session_state.response}</i>',unsafe_allow_html=True)
#     else:
#         st.write(f'<i>Sorry! Try a different question</i>',unsafe_allow_html=True)
    
#     st.markdown("")
#     if st.session_state.response != "None":
#         st.subheader("Deep Dive")
#         newQuestions = createNewQuestions(st.session_state.query,st.session_state.response) 
#         col1,col2,col3 = st.columns([0.3,0.3,0.4])
#         col1.button(newQuestions[0],on_click=generatedQuestionCallback,args=[newQuestions[0]])
#         col2.button(newQuestions[1],on_click=generatedQuestionCallback,args=[newQuestions[1]])
#         col3.button(newQuestions[2],on_click=generatedQuestionCallback,args=[newQuestions[2]])

#     st.markdown("")
#     otherPaperCheck = []
#     st.subheader("Citations")
#     for i,reference in enumerate(st.session_state.references):
#         citationsCol1,citationsCol2 = st.columns([0.9,0.1])
#         otherPaperCheck.append(reference[2])
#         with citationsCol1:
#             st.write(f'<a href = {reference[2]}>{reference[1]}</a>',unsafe_allow_html=True)
#             showText = st.checkbox("Show Details",key=f"citations{i}")
#             if showText:
#                 st.caption(f'<i>{reference[0]}</i>',unsafe_allow_html=True)
#                 st.caption(f'Confidence Score: {round(reference[3],2)}')
#             st.markdown("")
#         with citationsCol2:
#             #citationsCollector = create_feedback_collector("citations-feedback")
#             collectorCitations.st_feedback(
#                 feedback_type="thumbs",
#                 model="model-001",
#                 metadata={"query":st.session_state.query,"response":st.session_state.response,"url":reference[2]},
#                 user_id=userEmail,
#                 success_fail_message=False,
#                 key=f"Citations-Feedback:{i}",
#             )
#                     # citationPositive = st.button(":thumbsup:",key=f"citationsPositive{i}")
#                     # citationPositive = st.button(":thumbsdown:",key=f"citationsNegative{i}")    

        # st.markdown("")
    # st.divider()
        #st.subheader("Feedback")
    #mainCollector = create_feedback_collector("default")
    
    # st.markdown("")
    # mainCollector.st_feedback(
    #     label="Please provide feedback",
    #     feedback_type="textbox",
    #     model="model-001",
    #     metadata={"query":st.session_state.query,"response":st.session_state.response},
    #     success_fail_message=False,
    #     user_id=userEmail,
    #     #open_feedback_label="Please help us understand your response better"
    # )

    # st.markdown("")
    # # feedbackCol1, feedbackCol2, feedbackCol3 = st.columns([1,1,1])
    # # with feedbackCol2:
    # collectorMain.st_feedback(
    #     feedback_type="faces",
    #     model="model-001",
    #     metadata={"query":st.session_state.query,"response":st.session_state.response},
    #     success_fail_message=False,
    #     user_id=userEmail,
    #     align="flex-start",
    #     open_feedback_label="Please help us understand your response better"
    # )
    
    #st.write(st.session_state)
    





    # with tab2:
    #     with st.expander("Other relevant papers"):
    #         for i,data in enumerate(pubmedPapers):
    #             url = data["url"]
    #             url = str(url)
    #             relevantCol1,relevantCol2 = st.columns([0.9,0.1])
    #             if url not in otherPaperCheck:
    #                 with relevantCol1:
    #                     st.write(f'<a href = {url}>{data["title"]}</a>',unsafe_allow_html=True)
    #                     showText = st.checkbox("Show Text",key=f"moreInfo{i}")
    #                     if showText:
    #                         st.caption(f'<i>{data["abstract"]}</i>',unsafe_allow_html=True)
    #                     # st.caption(data["title"])
    #                     # st.caption(url)
    #                 with relevantCol2:
    #                     collectorCitations.st_feedback(
    #                         feedback_type="thumbs",
    #                         model="model-001",
    #                         metadata={"query":st.session_state.query,"response":st.session_state.response,"url":url},
    #                         success_fail_message=False,
    #                         key=f"Pubmed-Feedback:{i}",
    #                         user_id=st.session_state.userId
    #                     )



#     with st.form("Search_Form"):
#         if st.session_state.query == None:
#             userInput = st.text_input("Search with papers")
#         else:
#             userInput = st.text_input("Search with papers",value=st.session_state.query)
#         st.session_state.query = userInput
#         isSearch = st.form_submit_button("Search",on_click=searchButtonCallback,args=[st.session_state.query],type="primary")

    
#         if isSearch:
#             st.write(f'<p style="font-size:30px"><b>Response</b></p>',unsafe_allow_html=True)
#             #st.markdown(f"*:{st.session_state.response}:*")
#             if st.session_state.response != "None":
#                 st.write(f'<i>{st.session_state.response}</i>',unsafe_allow_html=True)
#             else:
#                 st.write(f'<i>Sorry! Try a different question</i>',unsafe_allow_html=True)
#             st.markdown("")
#             st.markdown("")

#             if st.session_state.response != "None":
#                 newQuestions = createNewQuestions(st.session_state.query,st.session_state.response) 
#                 col1,col2,col3 = st.columns([0.3,0.3,0.4])
#                 col1.button(newQuestions[0],on_click=generatedQuestionCallback,args=[newQuestions[0]])
#                 col2.button(newQuestions[1],on_click=generatedQuestionCallback,args=[newQuestions[1]])
#                 col3.button(newQuestions[2],on_click=generatedQuestionCallback,args=[newQuestions[2]])

#             otherPaperCheck = []
#             with st.expander("Citations"):
#                 for i,reference in enumerate(st.session_state.references):
#                     citationsCol1,citationsCol2 = st.columns([0.9,0.1])
#                     otherPaperCheck.append(reference[2])
#                     with citationsCol1:
#                         st.write(f'<a href = {reference[2]}>{reference[1]}</a>',unsafe_allow_html=True)
#                         st.caption(f'Confidence Score: {round(reference[3],2)}')
#                         showText = st.checkbox("Show Text",key=f"citations{i}")
#                         if showText:
#                             st.caption(f'<i>{reference[0]}</i>',unsafe_allow_html=True)
#                         st.markdown("")
#                     with citationsCol2:
#                         collectorCitations.st_feedback(
#                             feedback_type="thumbs",
#                             model="model-001",
#                             metadata={"query":st.session_state.query,"response":st.session_state.response,"url":reference[2]},
#                             success_fail_message=False,
#                             key=f"Citations-Feedback:{i}",
#                             user_id=st.session_state.userId
#                         )
#                         # citationPositive = st.button(":thumbsup:",key=f"citationsPositive{i}")
#                         # citationPositive = st.button(":thumbsdown:",key=f"citationsNegative{i}")    

#             # st.markdown("")
#             st.divider()
#             #st.subheader("Feedback")
#             feedbackCol1, feedbackCol2, feedbackCol3 = st.columns([1,1,1])
#             with feedbackCol2:
#                 collectorMain.st_feedback(
#                     feedback_type="faces",
#                     model="model-001",
#                     metadata={"query":st.session_state.query,"response":st.session_state.response},
#                     success_fail_message=False,
#                     user_id=st.session_state.userId,
#                     #open_feedback_label="Please help us understand your response better"
#                 )
        

            









if st.session_state["search"] == False:
    # engine = st.selectbox('Select Engine',["Engine1","Engine2","Engine3"])   
    # st.session_state["engine"] = engine
    if st.session_state.query == None:
        userInput = st.text_input("Search with papers")
    else:
        userInput = st.text_input("Search with papers",value=st.session_state.query)
    st.session_state.query = userInput
    buttonClick = st.button("Search",on_click=searchButtonCallback)


if st.session_state.search:

    response,citations,pubmedPapers = searchObj1.main(st.session_state.query)
    st.session_state.response = str(response)
    st.session_state.references = citations


    tab1,tab2 = st.tabs(["Home","More Info!"])
    
    with tab1:
        queryCol1,queryCol2 = st.columns([0.8,0.2])
        with queryCol1:
            #st.subheader("Query")
            st.write(f'<p style="font-size:30px"><b>Query</b></p>',unsafe_allow_html=True)
            #st.markdown(st.session_state.query)
            st.write(f'{st.session_state.query}',
unsafe_allow_html=True)
        with queryCol2:
            st.button("Edit Query",on_click = editcallback)
        
        st.write(f'<p style="font-size:30px"><b>Response</b></p>',unsafe_allow_html=True)
        #st.markdown(f"*:{st.session_state.response}:*")
        if st.session_state.response != "None":
            st.write(f'<i>{st.session_state.response}</i>',unsafe_allow_html=True)
        else:
            st.write(f'<i>Sorry! Try a different question</i>',unsafe_allow_html=True)
        st.markdown("")
        st.markdown("")

        if st.session_state.response != "None":
            newQuestions = createNewQuestions(st.session_state.query,st.session_state.response) 
            col1,col2,col3 = st.columns([0.3,0.3,0.4])
            col1.button(newQuestions[0],on_click=generatedQuestionCallback,args=[newQuestions[0]])
            col2.button(newQuestions[1],on_click=generatedQuestionCallback,args=[newQuestions[1]])
            col3.button(newQuestions[2],on_click=generatedQuestionCallback,args=[newQuestions[2]])

        otherPaperCheck = []
        with st.expander("Citations"):
            for i,reference in enumerate(citations):
                citationsCol1,citationsCol2 = st.columns([0.9,0.1])
                otherPaperCheck.append(reference[2])
                with citationsCol1:
                    st.write(f'<a href = {reference[2]}>{reference[1]}</a>',unsafe_allow_html=True)
                    st.caption(f'Confidence Score: {round(reference[3],2)}')
                    showText = st.checkbox("Show Text",key=f"citations{i}")
                    if showText:
                        st.caption(f'<i>{reference[0]}</i>',unsafe_allow_html=True)
                    st.markdown("")
                with citationsCol2:
                    collectorCitations.st_feedback(
                        feedback_type="thumbs",
                        model="model-001",
                        metadata={"query":st.session_state.query,"response":st.session_state.response,"url":reference[2]},
                        success_fail_message=False,
                        key=f"Citations-Feedback:{i}",
                        user_id=userEmail
                    )
                    # citationPositive = st.button(":thumbsup:",key=f"citationsPositive{i}")
                    # citationPositive = st.button(":thumbsdown:",key=f"citationsNegative{i}")    

        st.markdown("")
        #st.divider()
        #st.subheader("Feedback")
        collectorMain.st_feedback(
            feedback_type="faces",
            model="model-001",
            metadata={"query":st.session_state.query,"response":st.session_state.response},
            success_fail_message=False,
            user_id=userEmail,
            align="flex-start",
            open_feedback_label="Please help us understand your response better"
        )

        #st.divider()
        feedbackCol1, feedbackCol2, feedbackCol3 = st.columns([1,1,1])
        with feedbackCol2:
            searchAgain = st.button("Search Again!", on_click=reboot,type="primary")

        # responseFeedback = st.radio('Choose for the generated response',options=('Correct Response, No Hallucinations','Hallucinations','Didnt Like the Response','No Response'))
        # st.session_state["feedbackRating"] = responseFeedback
        # if responseFeedback:
        #     feedbackText = st.text_area("Please help us understand your feedback better")
        #     st.session_state["feedbackText"] = feedbackText
        # st.markdown("")
        # st.markdown("") 
        # finalCol1, finalCol2, finalCol3 = st.columns([1,1,1])
        # finalCol2.button("Search Again!", on_click=reboot,type="primary")

    
    with tab2:
        with st.expander("Other relevant papers"):
            for i,data in enumerate(pubmedPapers):
                url = data["url"]
                url = str(url)
                relevantCol1,relevantCol2 = st.columns([0.9,0.1])
                if url not in otherPaperCheck:
                    with relevantCol1:
                        st.write(f'<a href = {url}>{data["title"]}</a>',unsafe_allow_html=True)
                        showText = st.checkbox("Show Text",key=f"moreInfo{i}")
                        if showText:
                            st.caption(f'<i>{data["abstract"]}</i>',unsafe_allow_html=True)
                        # st.caption(data["title"])
                        # st.caption(url)
                    with relevantCol2:
                        collectorCitations.st_feedback(
                            feedback_type="thumbs",
                            model="model-001",
                            metadata={"query":st.session_state.query,"response":st.session_state.response,"url":url},
                            success_fail_message=False,
                            key=f"Pubmed-Feedback:{i}",
                            user_id=userEmail
                        )
                        #st.button(":thumbsup:",key=f"positive{i}")
                        #st.button(":thumbsdown:",key=f"negative{i}")
                        



# # import streamlit as st
# # from pubmed_manager import PubmedManager
# # from llama_index import VectorStoreIndex
# # from llama_index.evaluation import DatasetGenerator
# # from llama_index.readers.schema.base import Document
# # import os 
# # import openai
# # import uuid


# # #initialisation
# # if "search" not in st.session_state:
# #     st.session_state["search"] = False
# # if "query" not in st.session_state:
# #     st.session_state["query"] = None
# # if "response" not in st.session_state:
# #     st.session_state["response"] = None
# # if "feedbackRating" not in st.session_state:
# #     st.session_state["feedbackRating"] = None
# # if "feedbackText" not in st.session_state:
# #     st.session_state["feedbackText"] = None
# # if "apikey" not in st.session_state:
# #     st.session_state["apikey"] = None
# # if "references" not in st.session_state:
# #     st.session_state["references"] = []


# # #streamlit code

# # st.set_page_config(page_title="fastbio")
# # col1,col2,col3 = st.columns([1,1,1])
# # col2.title("FastBio")
# # st.divider()

# # #sidebar
# # apiKey = st.sidebar.text_input("OpenAI API Key", type="password")
# # st.session_state.apikey = apiKey
# # if not apiKey:
# #     st.info("Please add your OpenAI API key to continue.")
# #     st.stop()
# # openai.api_key = apiKey


# # #main content




# # #add logic to create a userId
# # #link userId to VectorStoreIndices
# # #@st.cache_resource(show_spinner=False)
# # class SearchBackend1():
# #   def __init__(self):
# #     #   self.indexCreated = False
# #     self.index = None
# #     self.queryEngine = None
# #     #self.persistDir = "/Users/arihantbarjatya/Documents/fastbio/database_storage/stored_embeddings/pubmed"
# #     #self.userId = str(uuid.uuid4())
# #     self.pubObj = PubmedManager()


# #   #@st.cache_data(show_spinner=False)
# #   def fetch_docs(_self,query):
# #     docs,papers = _self.pubObj.fetch_details(query)
# #     return docs,papers
  
# #   def update_index(self,docs):  
# #     for doc in docs:
# #       self.index.insert(doc)


# #   # add userId logic so once a users DB is created its remembered
# #   @st.cache_data(show_spinner=False)
# #   def main(_self,query):
# #     with st.spinner("Creating the best response for you"):
# #         currentDocs,ogPapers = _self.fetch_docs(query)
# #         _self.index = VectorStoreIndex.from_documents(currentDocs)
# #         _self.queryEngine = _self.index.as_query_engine()
        
# #         # if self.indexCreated == False:
# #         #     self.index = VectorStoreIndex.from_documents(currentDocs)
# #         #     self.index.set_index_id(self.userId)
# #         #     indexPath = self.persistDir+"/"+self.userId
# #         #     if not os.path.exists(indexPath):
# #         #         os.makedirs(indexPath)
# #         #     self.index.storage_context.persist(indexPath)
# #         #     self.indexCreated = True
# #         #     self.queryEngine = self.index.as_query_engine()
# #         # else:
# #         #     self.update_index(currentDocs)
# #         #     self.queryEngine = self.index.as_query_engine()
    
# #         response = _self.queryEngine.query(query)
# #         citations = []
# #         for node in response.source_nodes:
# #             title = node.node.metadata["Title of this paper"]
# #             url = node.node.metadata["URL"]
# #             citations.append((title,url))
    
# #     return response,citations,ogPapers

# # def searchButtonCallback():
# #   st.session_state.search = True


# # if st.session_state["search"] == False:
# #     # engine = st.selectbox('Select Engine',["Engine1","Engine2","Engine3"])   
# #     # st.session_state["engine"] = engine
# #     if st.session_state.query == None:
# #         userInput = st.text_input("Search with papers")
# #     else:
# #         userInput = st.text_input("Search with papers",value=st.session_state.query)
# #     st.session_state.query = userInput
# #     buttonClick = st.button("Ask",on_click=searchButtonCallback)


# # def editcallback():
# #     st.session_state["search"] = False
# #     st.session_state["response"] = None
# #     st.session_state["feedbackRating"] = None
# #     st.session_state["feedbackText"] = None
# #     #st.session_state["engine"] = None
# #     st.session_state["references"] = []

# # def log():
# #     pass

# # def reboot():
# #     log()
# #     st.session_state["search"] = False
# #     st.session_state["query"] = None
# #     st.session_state["response"] = None
# #     st.session_state["feedbackRating"] = None
# #     st.session_state["feedbackText"] = None
# #     #st.session_state["engine"] = None
# #     st.session_state["references"] = []

# # def feedbackEngine(_id):
# #     key = f"feedbackEngine{_id}"
# #     if key not in st.session_state:
# #         st.session_state[key] = False
# #     st.session_state[key] = True

# # def feedbackPubmed(_id):
# #     key = f"feedbackPubmed{_id}"
# #     if key not in st.session_state:
# #         st.session_state[key] = False
# #     st.session_state[key] = True

# # def generatedQuestionCallback(newQuery):
# #     log()
# #     st.session_state["query"] = newQuery
# #     st.session_state["response"] = None
# #     st.session_state["feedbackRating"] = None
# #     st.session_state["feedbackText"] = None
# #     st.session_state["references"] = []
# #     st.session_state["search"] = True



# # @st.cache_data(show_spinner=False,experimental_allow_widgets=True)
# # def createNewQuestions(query,response):
# #     responseDoc = Document(text=response,extra_info={"Original Query":query})
# #     dataGenerator = DatasetGenerator.from_documents([responseDoc])
# #     newQuestions = dataGenerator.generate_questions_from_nodes()
# #     numberOfQuestions = 3        
    
# #     try:
# #         newQuestions = newQuestions[:numberOfQuestions]
# #     except Exception as e:
# #         pass
    
# #     newQuestions = sorted(newQuestions,key=len)     
# #     n = len(newQuestions)
# #     for question in newQuestions:
# #         st.button(question,on_click=generatedQuestionCallback,args=[question])

# # searchObj1 = SearchBackend1()

# # if st.session_state.search:

# #     response,citations,pubmedPapers = searchObj1.main(st.session_state.query)
# #     st.session_state.response = str(response)
# #     st.session_state.references = citations
# #     urlsOnly = [x[1] for x in citations]


# #     tab1,tab2 = st.tabs[("Home","More Info!")]
    
# #     with tab1:

# #         queryCol1,queryCol2 = st.columns([0.8,0.2])
# #         with queryCol1:
# #             st.subheader("Query")
# #             st.markdown(st.session_state.query)
# #         with queryCol2:
# #             st.button("Edit Query",on_click = editcallback)
# #         st.subheader("Response")
# #         st.markdown(st.session_state.response)


# #         #homePageBaseDisplay(st.session_state.query,st.session_state.response)
# #         if st.session_state.response != None:
# #             createNewQuestions(st.session_state.query,st.session_state.response)
        
# #         st.divider()

# #         with st.expander("Citations for response"):
# #             for i,reference in enumerate(citations):
# #                 col1,col2 = st.columns([0.9,0.1])
# #                 with col1:
# #                     st.caption(reference[0])
# #                     st.caption(reference[1])
# #                 #otherPapercheck.append(str(reference[1]))
# #                 with col2:
# #                     st.button(":thumbsdown:",key=f"Citations{i}")

# #         #homePageCitation(st.session_state.references)
# #         st.divider()
        
# #         st.subheader("Feedback")
# #         responseFeedback = st.radio('Choose for the generated response',options=('Correct Response, No Hallucinations','Hallucinations','No Response'))
# #         st.session_state["feedbackRating"] = responseFeedback
# #         if responseFeedback:
# #             feedbackText = st.text_area("Please help us understand your feedback better")
# #             st.session_state["feedbackText"] = feedbackText
# #         #homePageFeedback()
# #         st.markdown("")
# #         st.markdown("") 
        
# #         col1, col2, col3 = st.columns([1,1,1])
# #         col2.button("Search Again!",type="primary",on_click=reboot)


# #     with tab2:

# #         with st.expander("Other relevant papers"):
# #             for i,data in enumerate(pubmedPapers):
# #                 url = data["url"]
# #                 url = str(url)
# #                 col1,col2 = st.columns([0.9,0.1])
# #                 if url not in otherPapercheck:
# #                     with col1:
# #                         st.caption(data["title"])
# #                         st.caption(url)
# #                     with col2:
# #                         st.button(":thumbsup:",key=f"{i}")
        


# #                 #st.button(label = ':thumbsdown')



        










    



