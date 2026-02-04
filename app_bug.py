#### PRINCIPE: utiliser st.session_state pour stocker les valeurs de chaque objet,
### et pour déterminer s'il contient une valuer. Idem pour déterminer si un groupe d'objets 
# contiennent (ont été complétés) avec des valeurs. 

from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="Steamlit Chat", page_icon="💬")
st.title("Chatbot")


if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

# Let's initialize a session state to count the number of messages
# This will allow us later to limit the chatbot to a certain amount of messages

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

# This session_state will be set to True once the feedback is generated and shwon
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False

# Let's create a sessio_state that will keep the history of the messages by the usr and the assistant
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Let's create a session_state to identify when the interview is finished
if "chat_complete" not in st.session_state:  
  st.session_state.chat_complete = False

# We write the function below with a view to attach it to the on_click event of a button
def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:
        #Add user's personal information (Name, Experinece, Skills)
    # Let start by adding a subhead to indicate where the personal info should be added

    # Le divider est juste pour stylisé le display
    st.subheader("Personal information", divider='rainbow')
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input(label="Name", max_chars = 40, placeholder="Enter your name")

    st.session_state["experience"] = st.text_area(label = "Experience", value = "", height = None, max_chars = 200, placeholder = "Describe your experience")

    st.session_state["skills"] = st.text_area(label = "Skills", value = "", height = None, max_chars = 200, placeholder = "List your skills")

    # Test labels for personal information
    # two asterisks: means bold style
    st.write(f"**Your Name**: {st.session_state['name']}")
    st.write(f"**Your Experience**: {st.session_state['experience']}")
    st.write(f"**Your Skills**: {st.session_state['skills']}")

    # Company and Position Section
    st.subheader('Company and Position', divider = 'rainbow')

    # We initialize session state variables for each input with a default value
    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)
    # Initialize with default input values
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["Junior","Mid-level","Senior"]
        )

    with col2:
         st.session_state["position"]  = st.selectbox(
        "Choose a position",
        ("Data Scientist", "Data engineer", "ML Engineer", "BI Analyst", "Financial Analyst"))

    st.session_state["company"] = st.selectbox(
        "Choose a Company",
        ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify")
    )

    # Test labels for company and position information
    st.write(f"**Your information**: {st.session_state['level']} {st.session_state['position']} at {st.session_state['company']}")
    
    # This ensures the user completes the setup phase before moving on to the interview phase
    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting Interview...")

# If all the condtions are fullfilled to start the interview:
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info(
        """
        Start by introducing yourself.
        """,
        icon = "👋"
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

# Pour utiliser les valeurs d'input par l'utilisateur dans le chatbot,
# il faut ajouter à st.session_state.messages, une liste de dictionnaires représentant chacun un message
# Dans ce cas-ci un seul message pour démarrer le chatbot avec le rôle "system".
# (rappel: outre ce rôle, il en existe deux autres: user et assistance)
# Le message doit alors inclure {st.session_state['nom_de_variable']} pour utiliser la valeur dans le chatbot
# The if statement evaluates to false if  (st.session_state.messages) is empty
# Note: we are using this syntax instead of "messages" not in st.session_state,
#  because st.session_state.messages has been initialized with an empty list
    if not st.session_state.messages:
        st.session_state.messages = [{"role":"system",
                                      "content":(f"You are an HR executive that interviews an interviewee called {st.session_state['name']}"
                                                f"with experience {st.session_state['experience']} and skills {st.session_state['skills']}."
                                                f"You should interview him for the position {st.session_state['level']} {st.session_state['position']}"
                                                f"at the company {st.session_state['company']}")
                                                }]

    #Pour afficher l'historique de tous les messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):            
                st.markdown(message["content"])

# Let's make sure the input is only accepted if the count of messages is below 5
    if st.session_state.user_message_count <5:
    #assign a value to prompt and check if not empty
        if prompt := st.chat_input("Your Answer.", max_chars=1000):
            st.session_state.messages.append({"role":"user","content":prompt})
            #display the user's message in the chat interface
            with st.chat_message("user"):
                st.markdown(prompt)

            #We create another chat message block for the assistance response
            #  and call the openAI API to generate the response
            # We create a dedicated context block (with ....) to display the assistance response in the chat interface
            with st.chat_message("assitant"):
                #The argument Stream will allow us to use the write_stream method (see previous lesson)
                # The messages argument provides the entire context that the model will need to provide a reply
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role":m["role"],"content":m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream = True,
                )
                response = st.write_stream(stream)
            st.session_state.messages.append({"role":"assistant","content":response})

        st.session_state.user_message_count +=1

    if st.session_state.user_message_count >=5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching Feedback ....")


# Show feedback screen
if st.session_state.feedback_shown:
    st.subheader("Feedback")
    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    # Now, we need to setup another model to serve as an evaluator

     # Initialize new OpenAI client instance for feedback
    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

     # Generate feedback using the stored messages and write a system prompt for the feedback
    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the Feedback give a score of 1 to 10.
             Follow this format:
             Overal Score: //Your score
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questions.
              """},
            {"role": "user", "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you shouldn't engage in any converstation: {conversation_history}"}
        ]
    )

# We extract the first item from the choices , which is the feedback.
    st.write(feedback_completion.choices[0].message.content)